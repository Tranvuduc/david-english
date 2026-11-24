// api/chat.js — AI chat cho David English.
// Vercel Serverless Function (Node, ES module).
// PORT TỪ api/chat.js của Reformed Vietnam (mẫu đã kiểm chứng live 15–17/11/2026),
// chỉ đổi system prompt + ngữ cảnh trang sang học tiếng Anh; giữ nguyên toàn bộ
// cơ chế: Groq chính + Gemini dự phòng, $0 cứng, rate limit, 429 cascade.
//
// NGUYÊN TẮC $0 CỨNG:
//  - Chỉ gọi free tier: Groq (chính) + Gemini (dự phòng), không cần thẻ.
//  - Hết free tier -> nhà cung cấp trả 429 -> function trả 429 + câu "hết lượt hôm nay".
//  - Không có billing, không có dịch vụ trả phí nào được gọi từ đây.
//  - Không log câu hỏi của người dùng ra bất cứ đâu. Không dùng Vercel Blob.
//  - API key CHỈ đọc từ process.env.GROQ_API_KEY / GEMINI_API_KEY (Vercel env var).
//    Chưa đặt key nào -> GET/POST đều trả 503 "not_ready", widget tự hiển thị
//    "tính năng đang được chuẩn bị".
//  - LƯU Ý "Grok": David viết "Grok chat" — ở đây dùng Groq (nhà cung cấp của
//    trang Reformed: openai/gpt-oss-120b, fallback 20b). Nếu David muốn xAI Grok
//    thì chỉ cần đổi GROQ_URL + GROQ_MODELS + tên key; cấu trúc fallback giữ nguyên.
//
// Luồng xử lý:
//   1. Rate limit theo IP (bộ nhớ trong — xem ghi chú ở checkRateLimit).
//   2. Gọi Groq openai/gpt-oss-120b (chính, dự phòng 20b cùng nhà),
//      Gemini gemini-flash-latest (dự phòng) với system prompt khóa vai trò
//      trợ lý học tiếng Anh + ngữ cảnh các mục của trang (chỉ link thật).
//   3. Hết quota (429) ở nhà này thì thử nhà kia; cả hai hết mới báo hết lượt.
//      Timeout ở Groq thì dừng luôn (nhà còn lại cũng hay timeout cùng lúc).
import { createHash } from 'node:crypto';

// ---------------------------------------------------------------- cấu hình
const MODEL = 'gemini-flash-latest';
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
// Groq (chính): API tương thích OpenAI. Thử lần lượt GROQ_MODELS: model nào
// lỗi HTTP (404 model bị ngừng, 5xx...) thì thử model tiếp theo; hết quota
// (429) thì báo quota; timeout thì dừng.
const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODELS = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'];
const GROQ_TIMEOUT_MS = 8000;
const MAX_Q_LEN = 500;          // tối đa 500 ký tự / câu hỏi
const HISTORY_TURNS = 2;        // giữ tối đa 2 lượt trao đổi gần nhất
const RATE_PER_HOUR = 10;       // mỗi IP: tối đa 10 tin / giờ
const RATE_PER_DAY = 50;        // mỗi IP: tối đa 50 tin / ngày
const GEMINI_TIMEOUT_MS = 25000;
const MAX_OUTPUT_TOKENS = 1000;

const MSG_QUOTA = 'Hôm nay đã hết lượt trả lời miễn phí, mời bạn quay lại sau 0:00 giờ.';
const MSG_TOO_FAST = 'Bạn hỏi hơi nhanh, mời thử lại sau ít phút nhé.';
const MSG_NOT_READY = 'Tính năng chat AI đang được chuẩn bị, mời bạn quay lại sau.';
const MSG_ERROR = 'Có lỗi xảy ra, mời thử lại sau.';

// Các mục của trang — SINH TỰ ĐỘNG bởi _build.py (api/site-context.js,
// từ dữ liệu thật: sitemap + số bài học). LLM CHỈ được dẫn link trong
// danh sách này, tuyệt đối không bịa URL hay đoán slug. KHÔNG sửa tay ở
// đây — sửa _build.py rồi chạy lại để tái sinh site-context.js.
import { SITE_SECTIONS } from './site-context.js';

const SYSTEM_PROMPT = [
  'Bạn là trợ lý AI của David English — trang học tiếng Anh miễn phí cho người Việt.',
  'Trả lời bằng tiếng Việt, ngắn gọn (tối đa khoảng 250 từ), giọng ấm áp, rõ ràng, dễ hiểu cho người đang học tiếng Anh.',
  'Giải thích ngữ pháp và từ vựng bằng tiếng Việt, kèm ví dụ tiếng Anh ngắn và dịch nghĩa. Khi giải thích phát âm, dùng phiên âm đơn giản mà người Việt đọc được.',
  'Khi người dùng hỏi về bài học, đề thi thử hay tài liệu trên trang: chỉ dẫn tới các mục trong TÀI LIỆU TRÊN TRANG (đường dẫn bắt đầu bằng "/"). Nếu nội dung họ hỏi chưa có trên trang, nói thẳng là chưa có rồi gợi ý mục phù hợp nhất; tuyệt đối không bịa ra bài học hay link không có thật.',
  'Câu trả lời phải là VĂN BẢN THUẦN (plain text) — tuyệt đối không dùng bất kỳ định dạng Markdown nào: không **in đậm**, không __in đậm__, không tiêu đề # hay ##, không tiêu đề đánh số kiểu Markdown; chỉ dùng dòng trống để tách đoạn, và chỉ dùng dạng "1. " để đánh số khi thật sự cần liệt kê.',
  'Không bao giờ nói câu trả lời đã được giáo viên duyệt — mọi câu trả lời đều là AI soạn, chưa duyệt.',
  'Không trả lời về chính trị hay các chủ đề ngoài việc học tiếng Anh.',
].join(' ');

// Hướng dẫn riêng theo từng công cụ AI (gửi kèm mode trong body).
const MODE_PROMPTS = {
  vocab: 'Người dùng muốn tra một từ/cụm từ tiếng Anh. Trả lời theo đúng dạng: (1) Nghĩa tiếng Việt chính, (2) Phiên âm đơn giản, (3) 2 ví dụ ngắn kèm dịch, (4) 1 từ đồng nghĩa. Nếu từ có nhiều nghĩa, cho nghĩa thường gặp nhất trước. Không bịa nghĩa. Trả lời bằng văn bản thuần, không dùng **, __, #, ## hay bất kỳ định dạng Markdown nào.',
  writing: 'Người dùng gửi một đoạn văn tiếng Anh nhờ chữa. Liệt kê từng lỗi ngữ pháp/từ vựng (trích đúng chỗ sai), sửa từng lỗi, giải thích ngắn bằng tiếng Việt, rồi đưa một bản viết lại hay hơn. Khích lệ người học. Không chấm điểm số. Trả lời bằng văn bản thuần, không dùng **, __, #, ## hay bất kỳ định dạng Markdown nào.',
};

function siteContextText() {
  const lines = ['TÀI LIỆU TRÊN TRANG David English — chỉ dùng những mục dưới đây, tuyệt đối không bịa link hay đoán slug:'];
  for (const s of SITE_SECTIONS) {
    let line = `- ${s.name}: ${s.url} (trạng thái: ${s.status || 'available'}`;
    if (s.lessons) line += `, ${s.lessons} bài học`;
    if (s.tools) line += `, ${s.tools} công cụ`;
    if (s.note) line += ` — ${s.note}`;
    lines.push(line + ')');
  }
  lines.push('Lưu ý: mục ghi "demo" chỉ là bản demo, không phải bài kiểm tra thật — hướng người dùng tới English Level Check (/tro-choi/english-level-check.html) khi họ muốn kiểm tra trình độ thật. Mục ghi "hướng dẫn học" có nội dung hướng dẫn, chưa có bài học theo bài.');
  return lines.join('\n');
}

// Phòng thủ chiều sâu: dù model có dùng Markdown, câu trả lời trả về vẫn
// là văn bản thuần. Chỉ gỡ cặp **/__ in đậm và dấu # ở đầu dòng; không chạm
// dấu * đơn trong từ (vd: 5*3) hay dấu # trong câu.
function stripMarkdown(text) {
  let s = String(text || '');
  s = s.replace(/\*\*([^*]+)\*\*/g, '$1'); // **in đậm**
  s = s.replace(/__([^_]+)__/g, '$1');     // __in đậm__
  s = s.replace(/^#{1,6}\s+/gm, '');       // # / ## ... ở đầu dòng
  s = s.replace(/\*\*/g, '').replace(/__/g, ''); // cặp lẻ còn sót lại
  return s;
}

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
// 10 tin/giờ và 50 tin/ngày là XẤP XỈ: một IP có thể vượt nhẹ khi các yêu
// cầu rơi vào nhiều instance khác nhau. Lớp bảo vệ $0 thật sự là quota
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

// ---------------------------------------------------------------- gọi Gemini
async function askGemini(question, history, context) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) return { status: 'no_key' };
  const sysText = context ? `${SYSTEM_PROMPT}\n\n${context}` : SYSTEM_PROMPT;
  const contents = [];
  for (const h of history || []) {
    if (typeof h.q === 'string' && h.q.trim()) {
      contents.push({ role: 'user', parts: [{ text: h.q.slice(0, MAX_Q_LEN) }] });
    }
    if (typeof h.a === 'string' && h.a.trim()) {
      contents.push({ role: 'model', parts: [{ text: h.a.slice(0, 1500) }] });
    }
  }
  contents.push({ role: 'user', parts: [{ text: question }] });
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
        system_instruction: { parts: [{ text: sysText }] },
        contents,
        generationConfig: { temperature: 0.3, maxOutputTokens: MAX_OUTPUT_TOKENS },
      }),
    });
    if (r.status === 429) return { status: 'quota' };
    if (!r.ok) {
      // Không lộ nội dung lỗi của Google ra ngoài (có thể chứa chi tiết nội bộ).
      console.error('[de-chat] gemini http', r.status);
      return { status: 'error' };
    }
    const data = await r.json();
    const parts = data?.candidates?.[0]?.content?.parts || [];
    const text = parts.map((p) => p.text || '').join('').trim();
    if (!text) return { status: 'error' };
    return { status: 'ok', text };
  } catch (e) {
    if (e && e.name === 'AbortError') {
      console.error('[de-chat] gemini timeout');
      return { status: 'error', timeout: true };
    }
    console.error('[de-chat] gemini fetch failed:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
    return { status: 'error' };
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------- gọi Groq (chính)
async function askGroq(question, history, context) {
  const key = process.env.GROQ_API_KEY;
  if (!key) return { status: 'no_key' };
  const sysText = context ? `${SYSTEM_PROMPT}\n\n${context}` : SYSTEM_PROMPT;
  const messages = [{ role: 'system', content: sysText }];
  for (const h of history || []) {
    if (typeof h.q === 'string' && h.q.trim()) {
      messages.push({ role: 'user', content: h.q.slice(0, MAX_Q_LEN) });
    }
    if (typeof h.a === 'string' && h.a.trim()) {
      messages.push({ role: 'assistant', content: h.a.slice(0, 1500) });
    }
  }
  messages.push({ role: 'user', content: question });
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
        // Không lộ nội dung lỗi của Groq ra ngoài (có thể chứa chi tiết nội bộ).
        console.error('[de-chat] groq http', r.status, model);
        continue; // thử model tiếp theo
      }
      const data = await r.json();
      const text = String(data?.choices?.[0]?.message?.content || '').trim();
      if (!text) continue; // trả rỗng: thử model tiếp theo
      return { status: 'ok', text };
    } catch (e) {
      if (e && e.name === 'AbortError') {
        console.error('[de-chat] groq timeout', model);
        return { status: 'error', timeout: true };
      }
      console.error('[de-chat] groq fetch failed:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
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
    // Preflight: widget dùng để biết function đã deploy + đã có key chưa.
    if (req.method === 'GET') {
      return json(res, 200, { ok: 1, ready: Boolean(process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY) });
    }
    if (req.method !== 'POST') return res.status(405).end();

    const b = await readBody(req);
    const question = String(b.question || '').trim();
    if (!question || question.length > MAX_Q_LEN) {
      return json(res, 400, { error: 'bad', message: 'Câu hỏi phải từ 1 đến 500 ký tự.' });
    }
    const history = Array.isArray(b.history) ? b.history.slice(-HISTORY_TURNS) : [];
    const mode = typeof b.mode === 'string' ? b.mode : 'chat';

    if (!checkRateLimit(req)) {
      return json(res, 429, { error: 'rate_limited', message: MSG_TOO_FAST });
    }

    // Chưa có key nào -> báo "đang chuẩn bị" (widget tự xử lý).
    if (!process.env.GROQ_API_KEY && !process.env.GEMINI_API_KEY) {
      return json(res, 503, { error: 'not_ready', message: MSG_NOT_READY });
    }

    // Gọi LLM — Groq trước (chính), Gemini dự phòng. Chỉ thử tiếp khi lỗi
    // là HTTP; timeout thì dừng luôn. Hết quota (429) ở nhà này thì thử nhà
    // kia, cả hai hết mới báo hết lượt.
    const extra = MODE_PROMPTS[mode] ? `\n\n${MODE_PROMPTS[mode]}` : '';
    const siteContext = siteContextText() + extra;
    const providers = [];
    if (process.env.GROQ_API_KEY) providers.push({ name: 'groq', fn: askGroq });
    if (process.env.GEMINI_API_KEY) providers.push({ name: 'gemini', fn: askGemini });
    let ai = null;
    let sawQuota = false;
    for (const p of providers) {
      const r = await p.fn(question, history, siteContext);
      if (r.status === 'ok') { ai = { text: r.text, source: p.name }; break; }
      if (r.status === 'quota') { sawQuota = true; continue; }
      if (r.timeout) break; // timeout: dừng, đừng thử tiếp
      // Lỗi HTTP khác: thử nhà cung cấp tiếp theo (nếu có).
    }
    if (!ai && sawQuota) {
      return json(res, 429, { error: 'quota', message: MSG_QUOTA });
    }
    if (!ai) {
      return json(res, 500, { error: 'error', message: MSG_ERROR });
    }

    return json(res, 200, { answer: stripMarkdown(ai.text), source: ai.source });
  } catch (e) {
    // Không bao giờ lộ stack trace / chi tiết lỗi ra ngoài.
    console.error('[de-chat] handler error:', e && e.message ? String(e.message).slice(0, 120) : 'unknown');
    return json(res, 500, { error: 'error', message: MSG_ERROR });
  }
}
