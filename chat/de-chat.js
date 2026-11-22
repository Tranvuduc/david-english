// de-chat.js — Widget chat AI cho David English.
// Port từ chat/rv-chat.js của Reformed Vietnam (mẫu đã kiểm chứng live):
//   - Không framework, không script bên ngoài, không thu thập dữ liệu cá nhân.
//   - API: POST /api/chat { question, history:[{q,a}], mode? } -> { answer, source, ... }
//   - GET /api/chat để biết function đã deploy + đã có key chưa.
//   - Chưa có key: chỉ hiện ghi chú "đang được chuẩn bị", vẫn cho nhập;
//     câu cần AI thì server trả 503 và widget hiện đúng thông báo.
//   - Mọi câu trả lời AI đều kèm nhãn "AI, chưa duyệt".
// Cách dùng: chèn 2 dòng vào cuối <body> của mọi trang:
//   <link rel="stylesheet" href="/chat/de-chat.css">  (trong <head>)
//   <script src="/chat/de-chat.js" defer></script>    (cuối <body>)
// Chế độ trang riêng: nếu trang có <div id="deChatPage"></div> thì chat
// hiển thị trong khung đó thay vì nút nổi (dùng cho /tro-chuyen-ai.html).
(function () {
  'use strict';

  var API = '/api/chat';
  var MAX_LEN = 500;
  var DISCLAIMER = 'Câu trả lời do AI soạn — AI, chưa duyệt.';
  var SUGGESTIONS = [
    'Phân biệt “a” và “the” như thế nào?',
    'Học từ vựng thế nào cho nhớ lâu?',
    'IELTS Speaking Part 1 thường hỏi gì?',
  ];

  var state = { open: false, ready: null, quotaHit: false, sending: false, history: [] };

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  function svgIcon() {
    return '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>';
  }

  function build() {
    var pageHost = document.getElementById('deChatPage');
    var isPage = !!pageHost;

    var root = el('div', 'de-chat');
    root.id = 'deChat';
    if (isPage) root.classList.add('de-chat-page');

    // Nút tròn nổi góc dưới-phải (chỉ ở chế độ widget).
    var fab = el('button', 'de-chat-fab');
    fab.type = 'button';
    fab.setAttribute('aria-label', 'Hỏi AI');
    fab.setAttribute('aria-expanded', 'false');
    fab.innerHTML = svgIcon();
    fab.appendChild(el('span', 'de-chat-fab-label', 'Hỏi AI'));

    // Panel chat.
    var panel = el('div', 'de-chat-panel');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Hỏi AI — David English');
    if (!isPage) panel.hidden = true;

    var head = el('div', 'de-chat-head');
    var titleWrap = el('div', 'de-chat-titles');
    titleWrap.appendChild(el('strong', null, 'Hỏi AI — David English'));
    titleWrap.appendChild(el('span', 'de-chat-sub', 'AI trả lời bằng tiếng Việt. AI, chưa duyệt.'));
    var closeBtn = el('button', 'de-chat-close', '✕');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'Đóng chat');
    head.appendChild(titleWrap);
    head.appendChild(closeBtn);

    var body = el('div', 'de-chat-body');
    body.setAttribute('aria-live', 'polite');

    var suggest = el('div', 'de-chat-suggest');
    SUGGESTIONS.forEach(function (s) {
      var b = el('button', 'de-chat-chip', s);
      b.type = 'button';
      b.addEventListener('click', function () { send(s); });
      suggest.appendChild(b);
    });
    body.appendChild(suggest);

    var foot = el('div', 'de-chat-foot');
    var input = document.createElement('input');
    input.type = 'text';
    input.maxLength = MAX_LEN;
    input.placeholder = 'Hỏi về học tiếng Anh, từ vựng, ngữ pháp, luyện thi…';
    input.setAttribute('aria-label', 'Câu hỏi của bạn');
    var sendBtn = el('button', 'de-chat-send', 'Gửi');
    sendBtn.type = 'button';
    foot.appendChild(input);
    foot.appendChild(sendBtn);

    var links = el('div', 'de-chat-links');
    var place = document.createElement('a');
    place.href = '/bai-xep-lop.html';
    place.textContent = 'Làm bài xếp lớp';
    links.appendChild(place);
    links.appendChild(document.createTextNode(' · '));
    var vocab = document.createElement('a');
    vocab.href = '/cong-cu/tu-vung.html';
    vocab.textContent = 'Tra từ bằng AI';
    links.appendChild(vocab);

    panel.appendChild(head);
    panel.appendChild(body);
    panel.appendChild(foot);
    panel.appendChild(links);
    root.appendChild(fab);
    root.appendChild(panel);
    if (isPage) pageHost.appendChild(root);
    else document.body.appendChild(root);

    function toggle(open) {
      state.open = open;
      panel.hidden = !open;
      fab.setAttribute('aria-expanded', String(open));
      if (open) {
        if (state.ready === null) checkReady();
        input.focus();
      }
    }
    if (isPage) {
      state.open = true;
      closeBtn.style.display = 'none';
      checkReady();
    } else {
      fab.addEventListener('click', function () { toggle(!state.open); });
      closeBtn.addEventListener('click', function () { toggle(false); });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && state.open) toggle(false);
      });
    }

    function setInputEnabled(on) {
      input.disabled = !on;
      sendBtn.disabled = !on;
    }

    // Kiểm tra function đã deploy + đã có key chưa (GET /api/chat).
    function checkReady() {
      fetch(API, { method: 'GET' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (d && d.ok) {
            state.ready = !!d.ready;
            if (!d.ready) showPreparing();
          } else {
            state.ready = false;
            showPreparing();
          }
        })
        .catch(function () {
          state.ready = false;
          showPreparing();
        });
    }
    function showPreparing() {
      // Chỉ hiện ghi chú, vẫn cho hỏi; câu nào cần AI thì server trả 503.
      var n = el('div', 'de-chat-notice', 'Trả lời bằng AI đang được chuẩn bị — bạn vẫn có thể xem các mục khác của trang.');
      body.appendChild(n);
      body.scrollTop = body.scrollHeight;
    }

    function escapeHtml(s) {
      return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    // Câu trả lời AI có thể chứa link tới các mục của trang (server chỉ đưa
    // link thật trong TÀI LIỆU TRÊN TRANG). Escape trước rồi mới biến link
    // nội bộ thành <a> — chỉ link bắt đầu bằng "/" mới được biến thành thẻ
    // <a>; câu hỏi của người dùng vẫn giữ text thuần.
    function renderAnswer(text) {
      var safe = escapeHtml(text);
      safe = safe.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      return safe.replace(/(^|[\s(])(\/[a-z0-9\-./#?=&%]+)/g, function (m, pre, url) {
        var clean = url.replace(/[.,;:!?]+$/, '');
        var tail = url.slice(clean.length);
        return pre + '<a href="' + clean + '">' + clean + '</a>' + tail;
      });
    }

    function addMsg(kind, text) {
      var m = el('div', 'de-chat-msg de-chat-' + kind);
      var bubble = el('div', 'de-chat-bubble');
      if (kind === 'ai') bubble.innerHTML = renderAnswer(text);
      else bubble.textContent = text;
      m.appendChild(bubble);
      if (kind === 'ai') {
        m.appendChild(el('div', 'de-chat-disclaimer', DISCLAIMER));
      }
      body.appendChild(m);
      body.scrollTop = body.scrollHeight;
      return m;
    }

    function addLinkCard(url, label, sub) {
      var a = document.createElement('a');
      a.className = 'de-chat-card';
      a.href = url;
      var b = el('strong', null, label);
      a.appendChild(b);
      if (sub) a.appendChild(el('span', null, sub));
      body.appendChild(a);
      body.scrollTop = body.scrollHeight;
    }

    function typing() {
      var m = el('div', 'de-chat-msg de-chat-ai');
      var b = el('div', 'de-chat-bubble de-chat-typing');
      b.appendChild(el('span'));
      b.appendChild(el('span'));
      b.appendChild(el('span'));
      m.appendChild(b);
      body.appendChild(m);
      body.scrollTop = body.scrollHeight;
      return m;
    }

    function send(text, mode) {
      var q = (text !== undefined ? text : input.value).trim();
      if (!q || state.sending || state.quotaHit) return;
      input.value = '';
      state.sending = true;
      setInputEnabled(false);
      addMsg('user', q);
      var t = typing();
      fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          history: state.history.slice(-2),
          mode: mode || 'chat',
        }),
      })
        .then(function (r) { return r.json().then(function (d) { return { status: r.status, d: d }; }); })
        .then(function (res) {
          t.remove();
          var d = res.d || {};
          if (res.status === 200 && d.answer) {
            addMsg('ai', d.answer);
            if (d.link) addLinkCard(d.link, d.link_label || 'Xem thêm', 'David English');
            state.history.push({ q: q, a: d.answer });
            if (state.history.length > 4) state.history = state.history.slice(-4);
          } else if (res.status === 429 && d.error === 'quota') {
            state.quotaHit = true;
            addMsg('ai', d.message || 'Hôm nay đã hết lượt trả lời miễn phí, mời bạn quay lại sau 0:00 giờ.');
          } else if (res.status === 429) {
            addMsg('ai', d.message || 'Bạn hỏi hơi nhanh, mời thử lại sau ít phút nhé.');
          } else if (res.status === 503) {
            state.ready = false;
            addMsg('ai', d.message || 'Tính năng chat AI đang được chuẩn bị, mời bạn quay lại sau.');
          } else {
            addMsg('ai', (d && d.message) || 'Có lỗi xảy ra, mời thử lại sau.');
          }
        })
        .catch(function () {
          t.remove();
          addMsg('ai', 'Không kết nối được, thử lại sau.');
        })
        .finally(function () {
          state.sending = false;
          if (!state.quotaHit) setInputEnabled(true);
          input.focus();
        });
    }

    sendBtn.addEventListener('click', function () { send(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') send();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
