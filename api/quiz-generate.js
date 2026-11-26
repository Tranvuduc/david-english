// api/quiz-generate.js — Tạo bộ câu hỏi quiz theo chủ đề cho David English.
// Vercel Serverless Function (Node, ES module).
// Giáo viên nhập chủ đề + trình độ + số câu; AI tạo bộ câu hỏi trộn nhiều
// dạng (trắc nghiệm, gõ đáp án, sắp xếp từ, nối cặp, điền từ, nghe rồi gõ)
// cho trang tro-choi/class-quiz-games.html.
//
// Cơ chế giống hệt api/chat.js + api/grade-writing.js: Groq chính + Gemini
// dự phòng, $0 cứng, rate limit theo IP (bộ nhớ trong, xấp xỉ), không log
// chủ đề người dùng nhập. Mọi câu hỏi đều được kiểm tra/làm sạch ở server
// trước khi trả về; câu hỏng bị loại bỏ.
//
// NGUYÊN TẮC $0 CỨNG:
//  - Chỉ gọi free tier: Groq (chính) + Gemini (dự phòng), không cần thẻ.
//  - Hết free tier -> nhà cung cấp trả 429 -> function trả 429 + câu "hết lượt hôm nay".
//  - Không có billing, không có dịch vụ trả phí nào được gọi từ đây.
//  - API key CHỈ đọc từ process.env.GROQ_API_KEY / GEMINI_API_KEY (Vercel env var).
//    Chưa đặt key nào -> GET/POST đều trả 503 "not_ready".
import { createHash } from 'node:crypto';

// ---------------------------------------------------------------- cấu hình
const MODEL = 'gemini-flash-latest';
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODELS = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'];
const GROQ_TIMEOUT_MS = 25000;
const GEMINI_TIMEOUT_MS = 40000;
const MAX_OUTPUT_TOKENS = 4500;
const MAX_TOPIC_LEN = 120;
const MIN_COUNT = 5;
const MAX_COUNT = 25;
const MIN_VALID = 5;            // cần ít nhất 5 câu hợp lệ mới trả pack
const RATE_PER_HOUR = 6;        // mỗi IP: tối đa 6 lần tạo / giờ (xấp xỉ)
const RATE_PER_DAY = 20;        // mỗi IP: tối đa 20 lần tạo / ngày (xấp xỉ)
const LEVELS = ['A1', 'A2', 'B1', 'B2'];

const MSG_QUOTA = 'Hôm nay đã hết lượt tạo câu hỏi AI miễn phí, mời bạn quay lại sau 0:00 giờ.';
const MSG_TOO_FAST = 'Bạn tạo hơi nhanh, mời thử lại sau ít phút nhé.';
const MSG_NOT_READY = 'Tính năng tạo câu hỏi AI đang được chuẩn bị, mời bạn quay lại sau.';
const MSG_ERROR = 'AI chưa tạo được bộ câu hỏi, mời thử lại hoặc đổi chủ đề nhé.';

function buildSystem(topic, level, count) {
  return [
    'Bạn là giáo viên tiếng Anh tạo bộ câu hỏi quiz cho học viên Việt Nam.',
    `Chủ đề: "${topic}". Trình độ: ${level} (CEFR). Số câu cần tạo: ${count + 4}.`,
    'Trả lời DUY NHẤT bằng JSON hợp lệ, không thêm chữ nào ngoài JSON, đúng dạng:',
    '{"title": "tiêu đề ngắn bằng tiếng Anh", "questions": [ ... ]}',
    'Mỗi câu hỏi là một object thuộc một trong 6 dạng sau, trộn đều các dạng:',
    '1. mcq: {"type":"mcq","q":"câu hỏi","options":["a","b","c","d"],"answer":0,"explain":"giải thích tiếng Việt"} — options đúng 4 lựa chọn, answer là chỉ số 0-3 của đáp án đúng.',
    '2. type: {"type":"type","q":"câu hỏi","answer":"đáp án ngắn","accept":["cách viết khác cũng đúng"],"explain":"..."} — đáp án ngắn 1-4 từ.',
    '3. order: {"type":"order","q":"Put the words in order","words":["I","went","to","school","yesterday"],"explain":"..."} — words là các từ của một câu đúng, PHẢI theo đúng thứ tự của câu đúng (trang web sẽ tự xáo trộn), 4-8 từ.',
    '4. match: {"type":"match","q":"Match the pairs","pairs":[["hot","cold"],["big","small"],["fast","slow"],["happy","sad"]],"explain":"..."} — đúng 4 cặp.',
    '5. fill: {"type":"fill","q":"She ___ to school by bus.","bank":["goes","go","went","going"],"answer":"goes","explain":"..."} — q chứa đúng một chỗ trống ___, bank có 4 từ gồm đáp án, answer phải nằm trong bank.',
    '6. listen: {"type":"listen","say":"câu tiếng Anh ngắn để nghe","answer":"câu đó","accept":[],"explain":"..."} — say là câu ngắn đúng trình độ.',
    'Quy tắc: nội dung tiếng Anh phải đúng trình độ ' + level + ' và đúng chủ đề; explain viết bằng tiếng Việt, 1 câu ngắn; không lặp câu hỏi; đáp án phải chắc chắn đúng.',
  ].join(' ');
}

// ---------------------------------------------------------------- tiện ích
function json(res, status, obj) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  return res.status(status).json(obj);
}

function str(x, max) {
  return typeof x === 'string' ? x.trim().slice(0, max) : '';
}

// ---------------------------------------------------------------- rate limit
// GHI CHÚ TRUNG THỰC: Vercel serverless có thể chạy nhiều instance song song,
// mỗi instance có bộ nhớ riêng, nên giới hạn này chỉ là "phanh" chống spam
// trong từng instance — không phải giới hạn toàn cục tuyệt đối. Lớp bảo vệ
// $0 thật sự là quota free tier của chính Groq/Gemini (429 -> tạm nghỉ).
const _hits = new Map(); // hashIP -> [timestampMs, ...]
const _salt = Math.random().toString(36).slice(2);
function clientIp(req) {
  const fwd = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  const real = String(req.headers['x-real-ip'] || '').trim();
  return fwd || real || 'unknown';
}
function ipHash(ip) {
  return createHash('sha256').update(_salt + '|' + ip).digest('hex').slice(0, 16);
}
function checkRateLimit(req) {
  const now = Date.now();
  const h = ipHash(clientIp(req));
  let arr = _hits.get(h) || [];
  arr = arr.filter((t) => now - t < 24 * 3600 * 1000); // chỉ giữ 24h gần nhất
  const lastHour = arr.filter((t) => now - t < 3600 * 1000).length;
  if (lastHour >= RATE_PER_HOUR || arr.length >= RATE_PER_DAY) {
    _hits.set(h, arr);
    return false;
  }
  arr.push(now);
  _hits.set(h, arr);
  if (_hits.size > 5000) { // chống phình bộ nhớ: xoá mục cũ nhất
    const first = _hits.keys().next().value;
    _hits.delete(first);
  }
  return true;
}

// ---------------------------------------------------------------- kiểm tra câu hỏi
function validQuestion(raw) {
  if (!raw || typeof raw !== 'object') return null;
  const type = str(raw.type, 10);
  const explain = str(raw.explain, 300);
  if (!explain) return null;
  if (type === 'mcq') {
    const q = str(raw.q, 300);
    const options = Array.isArray(raw.options) ? raw.options.map((o) => str(o, 120)).filter(Boolean) : [];
    const answer = Number(raw.answer);
    if (!q || options.length !== 4 || !Number.isInteger(answer) || answer < 0 || answer > 3) return null;
    if (new Set(options.map((o) => o.toLowerCase())).size !== 4) return null;
    return { type, q, options, answer, explain };
  }
  if (type === 'type') {
    const q = str(raw.q, 300);
    const answer = str(raw.answer, 80);
    const accept = Array.isArray(raw.accept) ? raw.accept.map((a) => str(a, 80)).filter(Boolean).slice(0, 4) : [];
    if (!q || !answer) return null;
    return { type, q, answer, accept, explain };
  }
  if (type === 'order') {
    let words = Array.isArray(raw.words) ? raw.words.map((w) => str(w, 40)).filter(Boolean) : [];
    if (words.length < 3 || words.length > 10) return null;
    // Model đôi khi xáo trộn words dù đã dặn; nếu explain nêu câu đúng
    // ("Câu đúng là: ...") và cùng tập từ, dùng thứ tự trong explain.
    const m = explain.match(/Câu đúng là:\s*(.+)/);
    if (m) {
      const tokens = m[1].replace(/[.!?]+$/, '').split(/\s+/).map((w) => w.trim()).filter(Boolean);
      const norm = (arr) => arr.map((w) => w.toLowerCase()).sort().join('|');
      if (tokens.length === words.length && norm(tokens) === norm(words)) words = tokens;
    }
    return { type, q: str(raw.q, 120) || 'Put the words in order', words, explain };
  }
  if (type === 'match') {
    const pairs = Array.isArray(raw.pairs)
      ? raw.pairs.map((p) => (Array.isArray(p) && p.length === 2 ? [str(p[0], 60), str(p[1], 60)] : null)).filter((p) => p && p[0] && p[1])
      : [];
    if (pairs.length !== 4) return null;
    return { type, q: str(raw.q, 120) || 'Match the pairs', pairs, explain };
  }
  if (type === 'fill') {
    const q = str(raw.q, 300);
    const bank = Array.isArray(raw.bank) ? raw.bank.map((w) => str(w, 60)).filter(Boolean) : [];
    const answer = str(raw.answer, 60);
    if (!q || !q.includes('___') || bank.length !== 4 || !bank.includes(answer)) return null;
    return { type, q, bank, answer, explain };
  }
  if (type === 'listen') {
    const say = str(raw.say, 200);
    const answer = str(raw.answer, 200) || say;
    const accept = Array.isArray(raw.accept) ? raw.accept.map((a) => str(a, 200)).filter(Boolean).slice(0, 4) : [];
    if (!say || !answer) return null;
    return { type, say, answer, accept, explain };
  }
  return null;
}

// Cân bằng vị trí đáp án đúng của câu mcq (tránh đáp án dồn vào một vị trí).
function balanceMcq(questions) {
  let slot = 0;
  for (const q of questions) {
    if (q.type !== 'mcq') continue;
    const target = slot % 4;
    slot += 1;
    if (q.answer !== target) {
      const tmp = q.options[target];
      q.options[target] = q.options[q.answer];
      q.options[q.answer] = tmp;
      q.answer = target;
    }
  }
  return questions;
}

function parsePack(text, count) {
  if (!text) return null;
  let s = String(text).trim();
  const fenced = s.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fenced) s = fenced[1].trim();
  const start = s.indexOf('{');
  const end = s.lastIndexOf('}');
  if (start < 0 || end <= start) return null;
  let obj;
  try {
    obj = JSON.parse(s.slice(start, end + 1));
  } catch (e) {
    return null;
  }
  if (!Array.isArray(obj.questions)) return null;
  const seen = new Set();
  const questions = [];
  for (const raw of obj.questions) {
    const q = validQuestion(raw);
    if (!q) continue;
    const key = (q.q || q.say || '').toLowerCase();
    if (key && seen.has(key)) continue;
    if (key) seen.add(key);
    questions.push(q);
    if (questions.length >= count) break;
  }
  if (questions.length < MIN_VALID) return null;
  return { title: str(obj.title, 80) || 'AI Quiz', questions: balanceMcq(questions) };
}

// ---------------------------------------------------------------- gọi Gemini
async function askGemini(system) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) return { status: 'no_key' };
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), GEMINI_TIMEOUT_MS);
  try {
    const r = await fetch(GEMINI_URL, {
      method: 'POST',
      signal: ctrl.signal,
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': key,
      },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: system }] },
        contents: [{ role: 'user', parts: [{ text: 'Tạo bộ câu hỏi ngay bây giờ.' }] }],
        generationConfig: { temperature: 0.7, maxOutputTokens: MAX_OUTPUT_TOKENS },
      }),
    });
    if (r.status === 429) return { status: 'quota' };
    if (!r.ok) {
      console.error('[de-quiz] gemini http', r.status);
      return { status: 'error' };
    }
    const data = await r.json();
    const parts = data?.candidates?.[0]?.content?.parts || [];
    const text = parts.map((p) => p.text || '').join('').trim();
    if (!text) return { status: 'error' };
    return { status: 'ok', text };
  } catch (e) {
    if (e && e.name === 'AbortError') {
      console.error('[de-quiz] gemini timeout');
      return { status: 'error', timeout: true };
    }
    console.error('[de-quiz] gemini fetch failed:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
    return { status: 'error' };
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------- gọi Groq (chính)
async function askGroq(system) {
  const key = process.env.GROQ_API_KEY;
  if (!key) return { status: 'no_key' };
  const messages = [
    { role: 'system', content: system },
    { role: 'user', content: 'Tạo bộ câu hỏi ngay bây giờ.' },
  ];
  for (const model of GROQ_MODELS) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), GROQ_TIMEOUT_MS);
    try {
      const r = await fetch(GROQ_URL, {
        method: 'POST',
        signal: ctrl.signal,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model,
          messages,
          temperature: 0.7,
          max_tokens: MAX_OUTPUT_TOKENS,
        }),
      });
      if (r.status === 429) return { status: 'quota' };
      if (!r.ok) {
        console.error('[de-quiz] groq http', r.status, model);
        continue; // thử model tiếp theo
      }
      const data = await r.json();
      const text = String(data?.choices?.[0]?.message?.content || '').trim();
      if (!text) continue; // trả rỗng: thử model tiếp theo
      return { status: 'ok', text };
    } catch (e) {
      if (e && e.name === 'AbortError') {
        console.error('[de-quiz] groq timeout', model);
        return { status: 'error', timeout: true };
      }
      console.error('[de-quiz] groq fetch failed:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
      return { status: 'error' }; // lỗi mạng: cùng endpoint, thử tiếp cũng vậy
    } finally {
      clearTimeout(timer);
    }
  }
  return { status: 'error' };
}

// ---------------------------------------------------------------- handler
async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  let s = '';
  for await (const c of req) {
    s += c;
    if (s.length > 20000) throw new Error('big');
  }
  return s ? JSON.parse(s) : {};
}

export default async function handler(req, res) {
  try {
    // Preflight: cho biết function đã deploy + đã có key chưa.
    if (req.method === 'GET') {
      return json(res, 200, { ok: 1, ready: Boolean(process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY), max_count: MAX_COUNT });
    }
    if (req.method !== 'POST') return res.status(405).end();

    const b = await readBody(req);
    const topic = str(b.topic, MAX_TOPIC_LEN);
    const level = LEVELS.includes(String(b.level || '').toUpperCase()) ? String(b.level).toUpperCase() : 'A1';
    let count = parseInt(b.count, 10);
    if (!Number.isInteger(count)) count = 15;
    count = Math.max(MIN_COUNT, Math.min(MAX_COUNT, count));
    if (topic.length < 2) {
      return json(res, 400, { error: 'bad', message: 'Mời nhập chủ đề (ví dụ: travel, food, past tense).' });
    }

    if (!checkRateLimit(req)) {
      return json(res, 429, { error: 'rate_limited', message: MSG_TOO_FAST });
    }

    if (!process.env.GROQ_API_KEY && !process.env.GEMINI_API_KEY) {
      return json(res, 503, { error: 'not_ready', message: MSG_NOT_READY });
    }

    const system = buildSystem(topic, level, count);
    const providers = [];
    if (process.env.GROQ_API_KEY) providers.push({ name: 'groq', fn: askGroq });
    if (process.env.GEMINI_API_KEY) providers.push({ name: 'gemini', fn: askGemini });
    let pack = null;
    let sawQuota = false;
    for (const p of providers) {
      const r = await p.fn(system);
      if (r.status === 'ok') {
        pack = parsePack(r.text, count);
        if (pack) break; // parse được: xong
        continue; // parse lỗi: thử nhà cung cấp tiếp theo (nếu có)
      }
      if (r.status === 'quota') { sawQuota = true; continue; }
      if (r.timeout) break; // timeout: dừng, đừng thử tiếp
      // Lỗi HTTP khác: thử nhà cung cấp tiếp theo (nếu có).
    }
    if (!pack && sawQuota) {
      return json(res, 429, { error: 'quota', message: MSG_QUOTA });
    }
    if (!pack) {
      return json(res, 502, { error: 'error', message: MSG_ERROR });
    }

    return json(res, 200, { ok: 1, pack });
  } catch (e) {
    // Không bao giờ lộ stack trace / chi tiết lỗi ra ngoài.
    console.error('[de-quiz] handler error:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
    return json(res, 500, { error: 'error', message: MSG_ERROR });
  }
}
