# David English — README triển khai (khung sườn v1)

Trang học tiếng Anh miễn phí cho người Việt. Khung sườn v1: toàn bộ mục đã có
trang thật, nội dung bài học sẽ thêm sau. Không dùng tài liệu dạy học cũ nào
trong v1 (không Kingdom English, không workbook, không đề thi thử cũ).

## Cấu trúc

- `index.html` — trang chủ
- `bai-xep-lop.html` — bài xếp lớp (demo 3 câu mẫu, chấm tạm tính, ghi rõ "đang hoàn thiện")
- `trinh-do/` — A1–C2 (index + 6 trang)
- `ky-nang/` — Nghe / Nói / Đọc / Viết (index + 4 trang)
- `luyen-thi/` — IELTS / TOEIC / PTE / TOEFL / VSTEP (index + 5 trang)
- `tre-em.html`, `cong-viec.html`, `du-hoc.html`, `tai-nguyen.html` — trang "Sắp có"
- `tro-chuyen-ai.html` — trang chat AI riêng
- `cong-cu/tu-vung.html` — tra từ bằng AI
- `cong-cu/viet.html` — chữa bài viết bằng AI
- `chat/de-chat.js` + `chat/de-chat.css` — widget chat nổi (mọi trang) + chế độ trang riêng
- `api/chat.js` — Vercel Serverless Function: Groq chính + Gemini dự phòng (port từ
  Reformed Vietnam `api/chat.js`, đã kiểm chứng live)
- `assets/style.css` — CSS chính (mobile-first, không font ngoài, không tracker)
- `_build.py` — sinh lại toàn bộ HTML từ một mẫu chung (chạy `python3 _build.py`)

## Biến môi trường (đặt trong Vercel Dashboard → Settings → Environment Variables)

| Biến | Bắt buộc | Ghi chú |
|---|---|---|
| `GROQ_API_KEY` | Có (chính) | Key Groq free tier. Không có key này thì chỉ còn Gemini; không có key nào thì chat trả 503 "đang được chuẩn bị". |
| `GEMINI_API_KEY` | Không (dự phòng) | Key Gemini free tier, model `gemini-flash-latest`. |

**Không bao giờ ghi key vào file hay commit lên repo.** Key chỉ sống trong
Vercel env vars.

## Cách AI hoạt động (giống trang Reformed)

- Groq trước: `openai/gpt-oss-120b`, lỗi HTTP thì thử `openai/gpt-oss-20b`.
- Gemini dự phòng: `gemini-flash-latest`.
- Timeout Groq 8 giây thì dừng luôn (không thử tiếp); Gemini 25 giây.
- Hết quota (429) ở nhà này thì thử nhà kia; cả hai hết mới trả 429
  "Hôm nay đã hết lượt trả lời miễn phí, mời bạn quay lại sau 0:00 giờ."
- Rate limit theo IP: 10 tin/giờ, 50 tin/ngày (bộ nhớ trong từng instance —
  chỉ là phanh chống spam; lớp bảo vệ $0 thật sự là quota free tier).
- Mọi câu trả lời AI đều kèm nhãn "AI, chưa duyệt" trên giao diện.
- LLM chỉ được dẫn link trong danh sách các mục của trang (đường dẫn tương
  đối) — không bịa link, không bịa bài học chưa có.

Lưu ý: David viết "Grok chat" — ở đây dùng **Groq** (nhà cung cấp của trang
Reformed). Nếu David muốn xAI Grok thì chỉ cần đổi `GROQ_URL` + `GROQ_MODELS`
+ tên key trong `api/chat.js`; cấu trúc fallback giữ nguyên.

## Triển khai lên Vercel (mẫu git-push như trang Reformed)

1. Tạo repo GitHub mới (ví dụ `david-english`), push toàn bộ thư mục này lên
   nhánh `main`.
2. Vercel Dashboard → Add New Project → Import repo → Deploy.
   Vercel tự nhận diện: trang tĩnh + `api/chat.js` thành Serverless Function.
3. Settings → Environment Variables: thêm `GROQ_API_KEY` (và `GEMINI_API_KEY`
   nếu có) cho cả Production + Preview, rồi Redeploy.
4. Kiểm tra live: mở trang chủ, bấm nút "Hỏi AI" góc dưới-phải, hỏi thử
   một câu. Nếu chưa đặt key, chat hiện "đang được chuẩn bị" — đúng thiết kế.
5. Gắn tên miền sau (khi đã chọn): Vercel Dashboard → Domains → Add.
   Tên miền đang cân nhắc: `davidenglish.vn` (chưa kiểm chứng dứt điểm còn
   trống hay không — kiểm tra ở VNNIC / nhà đăng ký .vn trước khi mua).
   `davidenglish.com` đã có chủ (trang cá nhân, từ 1997) — không dùng được.

## Chạy thử local

```sh
python3 -m http.server 8000
# mở http://localhost:8000 — xem trang tĩnh + widget chat
# (api/chat.js cần Node/Vercel runtime nên local chỉ kiểm tra giao diện;
#  xem DEPLOY-NOTE.md để biết cách kiểm tra API bằng Node)
```
