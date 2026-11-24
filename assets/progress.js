/* assets/progress.js — Tiến độ học của David English.
   Lưu trên chính trình duyệt của bạn (localStorage), không cần tài khoản,
   không gửi gì về máy chủ. Khóa dùng chung với trang flashcards:
   localStorage "de-progress-v1" = {"done": [đường dẫn trang bài học],
   "words": {"<từ>": {"known": true/false, "lesson": "<đường dẫn>",
   "level": "a1"|"a2"|"b1"|"b2"}}, "streak": {"last": "YYYY-MM-DD",
   "days": <số nguyên>}}.
   Trang bài học nào cũng có nút "Đánh dấu đã học xong" (data-de-done);
   hộp "Tiến độ của bạn" (data-de-progress-box) trên trang chủ và trang
   /trinh-do/ được điền hoàn toàn bằng JS từ dữ liệu này. */
(function () {
  'use strict';

  var KEY = 'de-progress-v1';

  /* Thứ tự học thật: A1 Bài 1–5 → A2 Bài 1–5 → B1 Bài 1–12 → B2 Bài 1–6.
     Đường dẫn + tên bài lấy từ tai-lieu/src/*.json (không bịa slug). */
  var LESSON_ORDER = [
    { path: '/trinh-do/a1/chao-hoi-gioi-thieu.html', title: 'Chào hỏi và giới thiệu bản thân', level: 'a1' },
    { path: '/trinh-do/a1/so-dem-ngay-gio.html', title: 'Số đếm, ngày và giờ', level: 'a1' },
    { path: '/trinh-do/a1/gia-dinh-cua-toi.html', title: 'Gia đình của tôi — My Family', level: 'a1' },
    { path: '/trinh-do/a1/mon-an-va-do-uong.html', title: 'Món ăn và đồ uống — Food and Drink', level: 'a1' },
    { path: '/trinh-do/a1/nha-cua-toi.html', title: 'Nhà của tôi — My Home', level: 'a1' },
    { path: '/trinh-do/a2/everyday-english.html', title: 'Everyday English — Tiếng Anh hằng ngày', level: 'a2' },
    { path: '/trinh-do/a2/mua-sam-hoi-gia.html', title: 'Đi mua sắm và hỏi giá', level: 'a2' },
    { path: '/trinh-do/a2/du-lich-va-ky-nghi.html', title: 'Du lịch và kỳ nghỉ — Travel and Holidays', level: 'a2' },
    { path: '/trinh-do/a2/suc-khoe-va-co-the.html', title: 'Sức khỏe và cơ thể — Health and Body', level: 'a2' },
    { path: '/trinh-do/a2/thoi-tiet-va-mua.html', title: 'Thời tiết và các mùa — Weather and Seasons', level: 'a2' },
    { path: '/trinh-do/b1/b1-lesson-01-sermon-on-the-mount.html', title: 'Bài 1: Bài Giảng Trên Núi', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-02-life-of-david.html', title: 'Bài 2: Cuộc Đời Đa-vít', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-03-prophets-isaiah.html', title: 'Bài 3: Các Tiên Tri: Ê-sai', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-04-wisdom-proverbs-psalms.html', title: 'Bài 4: Sự Khôn Ngoan: Châm Ngôn & Thi Thiên', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-05-romans-justification.html', title: 'Bài 5: Rô-ma: Được Xưng Công Chính Bởi Đức Tin', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-06-parables-kingdom.html', title: 'Bài 6: Các Dụ Ngôn Về Nước Thiên Đàng', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-07-holy-spirit-acts.html', title: 'Bài 7: Đức Thánh Linh Trong Sách Công Vụ Các Sứ Đồ', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-08-prayer-worship.html', title: 'Bài 8: Cầu Nguyện Và Thờ Phượng', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-09-church-one-body.html', title: 'Bài 9: Hội Thánh: Một Thân Thể', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-10-money-work-contentment.html', title: 'Bài 10: Tiền Bạc, Công Việc & Sự Thỏa Lòng', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-11-mission-nations.html', title: 'Bài 11: Sứ Mạng Đến Với Muôn Dân', level: 'b1' },
    { path: '/trinh-do/b1/b1-lesson-12-revelation-hope.html', title: 'Bài 12: Khải Huyền và Hy Vọng Sống Động — Ôn Tập Tổng Kết', level: 'b1' },
    { path: '/trinh-do/b2/b2-lesson-01-living-as-exiles.html', title: 'Bài 1: Sống Như Khách Lạ Trên Đất', level: 'b2' },
    { path: '/trinh-do/b2/b2-lesson-02-suffering-and-hope.html', title: 'Bài 2: Đau Khổ và Hy Vọng', level: 'b2' },
    { path: '/trinh-do/b2/b2-lesson-03-wisdom-for-decisions.html', title: 'Bài 3: Sự Khôn Ngoan Cho Quyết Định', level: 'b2' },
    { path: '/trinh-do/b2/b2-lesson-04-the-christian-mind.html', title: 'Bài 4: Tâm Trí Của Cơ Đốc Nhân', level: 'b2' },
    { path: '/trinh-do/b2/b2-lesson-05-leadership-and-serving.html', title: 'Bài 5: Lãnh Đạo và Phục Vụ', level: 'b2' },
    { path: '/trinh-do/b2/b2-lesson-06-evangelism-in-a-pluralist-world.html', title: 'Bài 6: Truyền Giáo Trong Thế Giới Đa Nguyên', level: 'b2' }
  ];
  var TOTAL = LESSON_ORDER.length; /* 28 */
  var LEVEL_TOTALS = { a1: 5, a2: 5, b1: 12, b2: 6 };

  function emptyState() {
    return { done: [], words: {}, streak: { last: null, days: 0 } };
  }

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) { return emptyState(); }
      var data = JSON.parse(raw);
      if (!data || typeof data !== 'object') { return emptyState(); }
      return {
        done: Array.isArray(data.done) ? data.done.filter(function (p) { return typeof p === 'string'; }) : [],
        words: (data.words && typeof data.words === 'object') ? data.words : {},
        streak: (data.streak && typeof data.streak === 'object')
          ? { last: typeof data.streak.last === 'string' ? data.streak.last : null,
              days: parseInt(data.streak.days, 10) || 0 }
          : { last: null, days: 0 }
      };
    } catch (e) {
      return emptyState();
    }
  }

  function save(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) { /* Bộ nhớ đầy hoặc bị chặn: tiến độ chỉ không lưu được. */ }
  }

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function todayStr(offsetDays) {
    var d = new Date();
    if (offsetDays) { d.setDate(d.getDate() + offsetDays); }
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }

  function isDone(path) {
    return load().done.indexOf(path) !== -1;
  }

  /* Cập nhật chuỗi ngày học: hôm nay đã tính rồi thì giữ nguyên; hôm qua
     có học thì +1; bỏ cách ngày thì tính lại từ 1. Trả về số ngày. */
  function touchStreak() {
    var state = load();
    var today = todayStr(0);
    if (state.streak.last === today) { return state.streak.days; }
    if (state.streak.last === todayStr(-1)) {
      state.streak.days = (state.streak.days || 0) + 1;
    } else {
      state.streak.days = 1;
    }
    state.streak.last = today;
    save(state);
    return state.streak.days;
  }

  function toggleDone(path) {
    var state = load();
    var i = state.done.indexOf(path);
    var nowDone;
    if (i === -1) {
      state.done.push(path);
      nowDone = true;
    } else {
      state.done.splice(i, 1);
      nowDone = false;
    }
    save(state);
    if (nowDone) { touchStreak(); }
    refreshUI();
    return nowDone;
  }

  function nextLesson() {
    var state = load();
    for (var i = 0; i < LESSON_ORDER.length; i++) {
      if (state.done.indexOf(LESSON_ORDER[i].path) === -1) {
        return LESSON_ORDER[i];
      }
    }
    return null;
  }

  function getStats() {
    var state = load();
    var perLevel = { a1: 0, a2: 0, b1: 0, b2: 0 };
    var totalDone = 0;
    LESSON_ORDER.forEach(function (lesson) {
      if (state.done.indexOf(lesson.path) !== -1) {
        totalDone += 1;
        perLevel[lesson.level] += 1;
      }
    });
    return {
      totalDone: totalDone,
      perLevel: perLevel,
      streakDays: state.streak.days || 0,
      nextLesson: nextLesson()
    };
  }

  /* API từ vựng cho trang flashcards (cùng khóa localStorage):
     setWord('apple', true, '/trinh-do/a1/...html', 'a1'). */
  function setWord(word, known, lesson, level) {
    var key = String(word || '').trim().toLowerCase();
    if (!key) { return; }
    var state = load();
    state.words[key] = {
      known: !!known,
      lesson: lesson || '',
      level: level || ''
    };
    save(state);
  }

  function getWord(word) {
    var key = String(word || '').trim().toLowerCase();
    return load().words[key] || null;
  }

  window.DEProgress = {
    isDone: isDone,
    toggleDone: toggleDone,
    getStats: getStats,
    touchStreak: touchStreak,
    nextLesson: nextLesson,
    setWord: setWord,
    getWord: getWord
  };

  /* ---- Giao diện ---- */

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function renderProgressBoxes() {
    var boxes = document.querySelectorAll('[data-de-progress-box]');
    if (!boxes.length) { return; }
    var stats = getStats();
    var html = '<h2>Tiến độ của bạn</h2>';
    if (stats.totalDone === 0 && stats.streakDays === 0) {
      html += '<p>Chưa có tiến độ — đánh dấu bài đã học để theo dõi.</p>';
    }
    html += '<p>Đã học xong ' + stats.totalDone + '/' + TOTAL + ' bài'
      + ' · A1 ' + stats.perLevel.a1 + '/' + LEVEL_TOTALS.a1
      + ' · A2 ' + stats.perLevel.a2 + '/' + LEVEL_TOTALS.a2
      + ' · B1 ' + stats.perLevel.b1 + '/' + LEVEL_TOTALS.b1
      + ' · B2 ' + stats.perLevel.b2 + '/' + LEVEL_TOTALS.b2 + '</p>';
    html += '<p>Chuỗi ngày học: ' + stats.streakDays + ' ngày</p>';
    if (stats.nextLesson) {
      html += '<p>Tiếp tục: <a href="' + esc(stats.nextLesson.path) + '">'
        + esc(stats.nextLesson.level.toUpperCase()) + ' — '
        + esc(stats.nextLesson.title) + ' →</a></p>';
    } else {
      html += '<p>Bạn đã học xong tất cả 28 bài!</p>';
    }
    html += '<p><a href="/ke-hoach-hoc.html">Xem kế hoạch học →</a></p>';
    for (var i = 0; i < boxes.length; i++) {
      boxes[i].innerHTML = html;
    }
  }

  function paintDoneButton(btn) {
    var done = isDone(btn.getAttribute('data-de-done'));
    btn.classList.toggle('is-done', done);
    btn.setAttribute('aria-pressed', done ? 'true' : 'false');
    btn.textContent = done
      ? '✓ Đã học xong — bấm để bỏ đánh dấu'
      : 'Đánh dấu đã học xong';
  }

  function wireDoneButtons() {
    var buttons = document.querySelectorAll('[data-de-done]');
    for (var i = 0; i < buttons.length; i++) {
      (function (btn) {
        paintDoneButton(btn);
        btn.addEventListener('click', function () {
          toggleDone(btn.getAttribute('data-de-done'));
          paintDoneButton(btn);
        });
      })(buttons[i]);
    }
  }

  function refreshUI() {
    renderProgressBoxes();
  }

  function init() {
    wireDoneButtons();
    renderProgressBoxes();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
