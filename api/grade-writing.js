// api/grade-writing.js — Chấm bài viết cho David English.
// Vercel Serverless Function (Node, ES module).
// Endpoint chuyên cho bài viết: nhận bài luận tới 3.000 ký tự và chấm theo
// 4 tiêu chí (thang 3.0–9.0), thay cho việc nhét bài viết vào /api/chat
// (giới hạn 500 ký tự/câu hỏi nên trước đây chỉ chấm được đoạn trích đầu).
//
// Cơ chế giống hệt api/chat.js: Groq chính + Gemini dự phòng, $0 cứng,
// rate limit theo IP (bộ nhớ trong, xấp xỉ), không log bài viết.
//
// NGUYÊN TẮC $0 CỨNG:
//  - Chỉ gọi free tier: Groq (chính) + Gemini (dự phòng), không cần thẻ.
//  - Hết free tier -> nhà cung cấp trả 429 -> function trả 429 + câu "hết lượt hôm nay".
//  - Không có billing, không có dịch vụ trả phí nào được gọi từ đây.
//  - Không log bài viết của người dùng ra bất cứ đâu. Không dùng Vercel Blob.
//  - API key CHỈ đọc từ process.env.GROQ_API_KEY / GEMINI_API_KEY (Vercel env var).
//    Chưa đặt key nào -> GET/POST đều trả 503 "not_ready".
import { createHash } from 'node:crypto';

// ---------------------------------------------------------------- cấu hình
const MODEL = 'gemini-flash-latest';
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODELS = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'];
const GROQ_TIMEOUT_MS = 8000;
const GEMINI_TIMEOUT_MS = 25000;
const MAX_OUTPUT_TOKENS = 1000;
const MAX_ESSAY_LEN = 3000;     // tối đa 3.000 ký tự / bài viết
const MIN_ESSAY_LEN = 20;       // tối thiểu 20 ký tự (dưới mức này không chấm được)
const MAX_PROMPT_LEN = 200;     // đề bài tối đa 200 ký tự
const RATE_PER_HOUR = 10;       // mỗi IP: tối đa 10 bài / giờ (xấp xỉ, xem ghi chú)
const RATE_PER_DAY = 50;        // mỗi IP: tối đa 50 bài / ngày (xấp xỉ, xem ghi chú)

const MSG_QUOTA = 'Hôm nay đã hết lượt chấm bài miễn phí, mời bạn quay lại sau 0:00 giờ.';
const MSG_TOO_FAST = 'Bạn gửi bài hơi nhanh, mời thử lại sau ít phút nhé.';
const MSG_NOT_READY = 'Tính năng chấm bài AI đang được chuẩn bị, mời bạn quay lại sau.';
const MSG_ERROR = 'Có lỗi xảy ra, mời thử lại sau.';

// 4 tiêu chí chấm, thang 3.0–9.0 (bước 0.5), theo khung CEFR/IELTS.
const CRITERIA = ['task', 'coherence', 'lexical', 'grammar'];

const GRADE_SYSTEM = [
  'Bạn là giám khảo chấm bài viết tiếng Anh cho người Việt học tiếng Anh.',
  'Chấm bài viết dưới đây theo đúng 4 tiêu chí, thang 3.0–9.0, bước 0.5:',
  '(1) task: hoàn thành yêu cầu đề bài (lạc đề hoặc chép lại đề: 4.0 trở xuống).',
  '(2) coherence: mạch lạc, liên kết giữa các ý và đoạn.',
  '(3) lexical: vốn từ, dùng từ đúng và đa dạng.',
  '(4) grammar: phạm vi và độ chính xác ngữ pháp.',
  'Trả lời DUY NHẤT bằng JSON hợp lệ, không thêm chữ nào ngoài JSON, đúng dạng sau:',
  '{"task": 6.0, "coherence": 6.5, "lexical": 6.0, "grammar": 6.5,',
  '"strengths": "điểm mạnh, viết bằng tiếng Việt, 1-2 câu",',
  '"improvements": "cần cải thiện, viết bằng tiếng Việt, 1-2 câu",',
  '"examples": ["một câu sai trong bài -> cách sửa đúng"]}',
  'strengths/improvements viết bằng tiếng Việt, ngắn gọn, cụ thể cho bài này.',
].join(' ');

// ---------------------------------------------------------------- tiện ích
function json(res, status, obj) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  return res.status(status).json(obj);
}

// ---------------------------------------------------------------- rate limit
// GHI CHÚ TRUNG THỰC: Vercel serverless có thể chạy nhiều instance song song,
// mỗi instance có bộ nhớ riêng, nên giới hạn này chỉ là "phanh" chống spam
// trong từng instance — không phải giới hạn toàn cục tuyệt đối. Giới hạn
// 10 bài/giờ và 50 bài/ngày là XẤP XỈ. Lớp bảo vệ $0 thật sự là quota
// free tier của chính Groq/Gemini (429 -> tạm nghỉ).
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

// ---------------------------------------------------------------- chấm dự phòng
// Kiểm tra tự động đơn giản trên máy (không gọi AI) — dùng khi AI không
// chấm được. Port từ heuristicBand trong tro-choi/english-level-check.html.
// Chỉ trả điểm tổng thể, không có điểm từng tiêu chí.
function heuristicBand(text) {
  const w = (text.toLowerCase().match(/[a-z']+/g) || []);
  const n = w.length;
  if (n < 20) return null;
  const u = {};
  w.forEach((x) => { u[x] = 1; });
  const ttr = Object.keys(u).length / n;
  const avg = w.join('').length / n;
  const sents = (text.match(/[.!?]+/g) || []).length || 1;
  const c1 = Math.min(((text.match(/\b(however|although|whereas|moreover|furthermore|therefore|nevertheless|for example|for instance|as a result|while|despite)\b/gi) || []).length / 4), 1);
  const c2 = Math.min(((text.match(/\b(which|who|whereas|although|because|while|if|unless|since|even though)\b/gi) || []).length / 4), 1);
  const s = Math.min(n / 120, 1) * 0.3
    + Math.min(Math.max((ttr - 0.45) / 0.25, 0), 1) * 0.2
    + Math.min(Math.max((avg - 3.9) / 1.2, 0), 1) * 0.15
    + c1 * 0.15 + c2 * 0.1
    + Math.min(Math.max((n / sents - 9) / 10, 0), 1) * 0.1;
  return 4 + s * 3;
}

function fallbackResult(essay) {
  const band = heuristicBand(essay);
  const overall = band == null ? 4 : Math.max(3, Math.min(9, Math.round(Math.min(7, band) * 2) / 2));
  return {
    graded_by: 'fallback',
    task: null, coherence: null, lexical: null, grammar: null,
    overall, strengths: '', improvements: '', examples: [],
  };
}

// ---------------------------------------------------------------- xử lý JSON trả về
function clampHalf(x) {
  const n = parseFloat(x);
  if (!isFinite(n)) return null;
  return Math.max(3, Math.min(9, Math.round(n * 2) / 2));
}

function parseGrade(text) {
  if (!text) return null;
  let s = String(text).trim();
  // Bóc khối ```json ... ``` nếu model trả kèm markdown.
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
  const out = {};
  for (const k of CRITERIA) {
    out[k] = clampHalf(obj[k]);
    if (out[k] == null) return null;
  }
  out.overall = Math.max(3, Math.min(9, Math.round(((out.task + out.coherence + out.lexical + out.grammar) / 4) * 2) / 2));
  out.strengths = typeof obj.strengths === 'string' ? obj.strengths.slice(0, 500) : '';
  out.improvements = typeof obj.improvements === 'string' ? obj.improvements.slice(0, 500) : '';
  out.examples = Array.isArray(obj.examples)
    ? obj.examples.filter((x) => typeof x === 'string').slice(0, 3).map((x) => x.slice(0, 300))
    : [];
  out.graded_by = 'ai';
  return out;
}

// ---------------------------------------------------------------- gọi Gemini
async function askGemini(essay, prompt) {
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
        system_instruction: { parts: [{ text: GRADE_SYSTEM }] },
        contents: [{ role: 'user', parts: [{ text: `Đề bài: ${prompt || '(không có đề cụ thể)'}\n\nBài viết cần chấm:\n${essay}` }] }],
        generationConfig: { temperature: 0.3, maxOutputTokens: MAX_OUTPUT_TOKENS },
      }),
    });
    if (r.status === 429) return { status: 'quota' };
    if (!r.ok) {
      console.error('[de-grade] gemini http', r.status);
      return { status: 'error' };
    }
    const data = await r.json();
    const parts = data?.candidates?.[0]?.content?.parts || [];
    const text = parts.map((p) => p.text || '').join('').trim();
    if (!text) return { status: 'error' };
    return { status: 'ok', text };
  } catch (e) {
    if (e && e.name === 'AbortError') {
      console.error('[de-grade] gemini timeout');
      return { status: 'error', timeout: true };
    }
    console.error('[de-grade] gemini fetch failed:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
    return { status: 'error' };
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------- gọi Groq (chính)
async function askGroq(essay, prompt) {
  const key = process.env.GROQ_API_KEY;
  if (!key) return { status: 'no_key' };
  const messages = [
    { role: 'system', content: GRADE_SYSTEM },
    { role: 'user', content: `Đề bài: ${prompt || '(không có đề cụ thể)'}\n\nBài viết cần chấm:\n${essay}` },
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
          temperature: 0.3,
          max_tokens: MAX_OUTPUT_TOKENS,
        }),
      });
      if (r.status === 429) return { status: 'quota' };
      if (!r.ok) {
        console.error('[de-grade] groq http', r.status, model);
        continue; // thử model tiếp theo
      }
      const data = await r.json();
      const text = String(data?.choices?.[0]?.message?.content || '').trim();
      if (!text) continue; // trả rỗng: thử model tiếp theo
      return { status: 'ok', text };
    } catch (e) {
      if (e && e.name === 'AbortError') {
        console.error('[de-grade] groq timeout', model);
        return { status: 'error', timeout: true };
      }
      console.error('[de-grade] groq fetch failed:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
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
      return json(res, 200, { ok: 1, ready: Boolean(process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY), max_chars: MAX_ESSAY_LEN });
    }
    if (req.method !== 'POST') return res.status(405).end();

    const b = await readBody(req);
    const essay = String(b.essay || '').trim();
    const prompt = String(b.prompt || '').slice(0, MAX_PROMPT_LEN);
    const context = String(b.context || '').slice(0, 200);
    if (!essay || essay.length < MIN_ESSAY_LEN || essay.length > MAX_ESSAY_LEN) {
      return json(res, 400, { error: 'bad', message: `Bài viết phải từ ${MIN_ESSAY_LEN} đến ${MAX_ESSAY_LEN} ký tự.` });
    }

    if (!checkRateLimit(req)) {
      return json(res, 429, { error: 'rate_limited', message: MSG_TOO_FAST });
    }

    // Chưa có key nào -> trả kết quả dự phòng (không báo "đang chuẩn bị",
    // vì bài kiểm tra vẫn cần một điểm tham khảo).
    if (!process.env.GROQ_API_KEY && !process.env.GEMINI_API_KEY) {
      return json(res, 200, fallbackResult(essay));
    }

    // Gọi LLM — Groq trước (chính), Gemini dự phòng. Chỉ thử tiếp khi lỗi
    // là HTTP; timeout thì dừng luôn. Hết quota (429) ở nhà này thì thử nhà
    // kia, cả hai hết mới báo hết lượt.
    const providers = [];
    if (process.env.GROQ_API_KEY) providers.push({ name: 'groq', fn: askGroq });
    if (process.env.GEMINI_API_KEY) providers.push({ name: 'gemini', fn: askGemini });
    let grade = null;
    let sawQuota = false;
    for (const p of providers) {
      const r = await p.fn(essay, prompt || context);
      if (r.status === 'ok') {
        grade = parseGrade(r.text);
        if (grade) break; // parse được: xong
        // parse lỗi: thử nhà cung cấp tiếp theo (nếu có)
        continue;
      }
      if (r.status === 'quota') { sawQuota = true; continue; }
      if (r.timeout) break; // timeout: dừng, đừng thử tiếp
      // Lỗi HTTP khác: thử nhà cung cấp tiếp theo (nếu có).
    }
    if (!grade && sawQuota) {
      return json(res, 429, { error: 'quota', message: MSG_QUOTA });
    }
    if (!grade) {
      // AI không chấm được (lỗi hoặc parse lỗi ở cả hai nhà): trả dự phòng
      // thay vì lỗi 500, để bài kiểm tra vẫn có điểm tham khảo.
      return json(res, 200, fallbackResult(essay));
    }

    return json(res, 200, grade);
  } catch (e) {
    // Không bao giờ lộ stack trace / chi tiết lỗi ra ngoài.
    console.error('[de-grade] handler error:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
    return json(res, 500, { error: 'error', message: MSG_ERROR });
  }
}
