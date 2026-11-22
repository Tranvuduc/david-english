# DEPLOY-NOTE — David English, khung sườn v1 (22/11/2026)

Sẵn sàng đưa lên Vercel. Khung sườn trước, nội dung sau — KHÔNG dùng tài liệu
dạy học cũ nào trong v1.

## Cây file (27 trang HTML + API + assets, tổng ~156 KB)

```
david-english-site/
├── index.html                    trang chủ (hero + 8 mục + 3 công cụ AI)
├── bai-xep-lop.html              bài xếp lớp — DEMO 3 câu mẫu, chấm tạm tính
├── trinh-do/                     index + a1/a2/b1/b2/c1/c2.html
├── ky-nang/                      index + nghe/noi/doc/viet.html
├── luyen-thi/                    index + ielts/toeic/pte/toefl/vstep.html
├── tre-em.html                   Sắp có
├── cong-viec.html                Sắp có
├── du-hoc.html                   Sắp có
├── tai-nguyen.html               Sắp có
├── tro-chuyen-ai.html            trang chat AI riêng (khung #deChatPage)
├── cong-cu/
│   ├── tu-vung.html              tra từ bằng AI (gọi /api/chat mode=vocab)
│   └── viet.html                 chữa bài viết bằng AI (mode=writing)
├── chat/
│   ├── de-chat.js                widget chat nổi mọi trang + chế độ trang riêng
│   └── de-chat.css               CSS widget (port từ rv-chat.css)
├── api/
│   └── chat.js                   Vercel Function: Groq chính + Gemini dự phòng
├── assets/style.css              CSS chính (mobile-first, không font ngoài)
├── vercel.json                   headers bảo mật + cache
├── package.json                  {"name":"david-english","type":"module"}
├── README-DEPLOY.md              hướng dẫn triển khai + biến môi trường
├── DEPLOY-NOTE.md                file này
├── _build.py                     sinh lại toàn bộ HTML (python3 _build.py)
└── .vercelignore                 loại _build.py khỏi deploy
```

## Sẵn sàng live vs stub

SẴN SÀNG:
- Toàn bộ điều hướng + 27 route thật, trang "Sắp có" có cấu trúc dự kiến.
- Widget chat AI nổi mọi trang + trang chat riêng.
- `api/chat.js`: Groq `openai/gpt-oss-120b` → `openai/gpt-oss-20b`, Gemini
  `gemini-flash-latest` dự phòng; 429 cascade; hết lượt → "hết lượt hôm nay";
  rate limit 10/giờ + 50/ngày/IP; không key → 503 "đang được chuẩn bị".
- Công cụ tra từ + chữa bài viết gọi cùng `/api/chat` (mode=vocab/writing).
- Mọi câu trả lời AI đều kèm nhãn "AI, chưa duyệt".

STUB (ghi rõ trên trang, không giả kết quả thật):
- Bài xếp lớp: 3 câu mẫu, kết quả "tạm tính", bộ câu hỏi thật chưa có.
- Các trang bài học: "Sắp có" + mô tả nội dung dự kiến, chưa có bài nào.
- Tra từ / chữa bài: cần key API mới trả lời; chưa có key thì báo "đang được chuẩn bị".

## Biến môi trường cần đặt ở Vercel (không có giá trị nào trong repo)

- `GROQ_API_KEY` (chính) — key Groq free tier.
- `GEMINI_API_KEY` (dự phòng, tùy chọn) — key Gemini free tier.

## Các bước deploy (mẫu git-push như trang Reformed)

1. Tạo repo GitHub mới, push toàn bộ thư mục này lên nhánh `main`.
   (Không commit/push trong bước này — do Molly/David làm theo quy tắc repo.)
2. Vercel Dashboard → Add New Project → Import repo → Deploy.
3. Settings → Environment Variables: thêm `GROQ_API_KEY` (+ `GEMINI_API_KEY`
   nếu có) cho Production + Preview → Redeploy.
4. Kiểm tra live: trang chủ → bấm "Hỏi AI" → hỏi thử. Chưa có key thì chat
   hiện "đang được chuẩn bị" (đúng thiết kế).
5. Gắn tên miền sau khi chọn (đang cân nhắc `davidenglish.vn` — chưa kiểm chứng
   dứt điểm còn trống; `davidenglish.com` đã có chủ, không dùng được).

## Kết quả kiểm tra local (22/11 ~20:40)

- HTTP local (python http.server): 30/30 route trả 200 (27 trang + 2 CSS + 1 JS).
- Link nội bộ: 29/29 href đều trỏ tới file có thật.
- Chat snippet: 27/27 trang đều có `<script src="/chat/de-chat.js">` +
  `<link href="/chat/de-chat.css">`; `tro-chuyen-ai.html` có `#deChatPage`.
- `node --check`: `api/chat.js`, `chat/de-chat.js` và 3 inline script đều OK.
- `api/chat.js` chạy thử bằng Node (không key thật, không gọi nhà cung cấp):
  GET → 200 `{ok:1, ready:false}`; POST không key → 503 `not_ready`;
  câu rỗng / quá 500 ký tự → 400; sai method → 405; 11 POST liên tiếp
  cùng IP → 10× 503 rồi lần 11 → 429 `rate_limited`; mode=vocab/writing
  không key → 503, không crash.
- Grep nội dung cấm: `Kingdom English|flashcard|workbook|on-tap|megacities|
  changing lives|long 4b|unit 9|units 9` → 0 kết quả trong toàn bộ site.
- Nhãn "AI, chưa duyệt" có trên 27/27 trang; "Sắp có" trên 19 trang
  (8 trang còn lại là trang chủ, bài xếp lớp demo, 3 trang index mục,
  trang chat, 2 trang công cụ).
- `vercel.json` là JSON hợp lệ.

## CHƯA kiểm chứng được (cần kiểm tra sau khi deploy)

- Chạy thật trên trình duyệt (widget mở/đóng, không lỗi console) — không có
  trình duyệt headless trong bước này; kiểm tra trên URL preview của Vercel.
- `api/chat.js` với key thật (Groq/Gemini) — chưa có key trong bước này; chỉ
  kiểm tra được nhánh không key + rate limit. Sau khi đặt key ở Vercel, hỏi
  thử 1 câu và kiểm tra câu trả lời về đúng, có nhãn "AI, chưa duyệt".
- Tên miền `davidenglish.vn` còn trống hay không — kiểm tra ở VNNIC / nhà
  đăng ký .vn (nhiệm vụ của Molly).

## Ghi chú

- "Grok" trong lệnh của David được hiểu là **Groq** (nhà cung cấp của trang
  Reformed). Nếu David muốn xAI Grok thì đổi `GROQ_URL` + `GROQ_MODELS` +
  tên key trong `api/chat.js`; cấu trúc fallback giữ nguyên.
- Mẫu chat port từ Reformed Vietnam `api/chat.js` (34 KB, HEAD 22/11),
  `chat/rv-chat.js` + `chat/rv-chat.css` — chỉ đổi system prompt, ngữ cảnh
  trang và màu sắc; cơ chế Groq/Gemini/429/rate-limit giữ nguyên.
- File nghiên cứu gốc đã chuyển ra `~/workspace/david-english-site-study/`
  (không nằm trong thư mục deploy).
