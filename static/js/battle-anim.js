/* ==========================================================================
   Hoạt ảnh nhân vật trên đường đua (GSAP).

   Mỗi khủng long là một rig SVG có khớp (xem heroSvg trong battle-hero.js).
   Tệp này xoay các khớp đó theo thời gian để tạo:
     - chu kỳ chạy: hai chân guồng so le, thân nhún, đuôi vẫy, đầu gật
     - động tác nhảy rào: thu chân, bật lên, ngả người, tiếp đất
     - trạng thái đứng im khi người chơi đã bị loại

   GSAP được nạp từ static/js/vendor/gsap.min.js nên vẫn chạy khi mất mạng.
   Nếu vì lý do nào đó GSAP không nạp được, mọi hàm ở đây lặng lẽ không làm
   gì — nhân vật vẫn hiển thị, chỉ là không cử động.
   ========================================================================== */

(function (global) {
  'use strict';

  var G = global.gsap || null;
  var runners = {};          // player_id -> timeline chu kỳ chạy

  function part(el, name) {
    return el ? el.querySelector('[data-part="' + name + '"]') : null;
  }

  /* ---- Nhịp thở tại chỗ -------------------------------------------------
     TAY VÀ CHÂN GIỮ NGUYÊN, không guồng, không vẫy — khớp tay chân xoay
     trông rất xấu ở cỡ nhỏ. Chuyển động chỉ còn cả người nhún lên xuống
     thật nhẹ như đang thở, đủ để nhân vật không bị cứng đơ.             */
  function startRun(pid, el, speed) {
    if (!G || !el) return;
    stopRun(pid);
    var body = part(el, 'body');
    if (!body) return;

    var dur = 1.15 / (speed || 1);          // một nhịp thở
    var tl = G.timeline({ repeat: -1, defaults: { ease: 'sine.inOut' } });
    tl.fromTo(body, { y: 0 }, { y: -2, duration: dur }, 0)
      .to(body, { y: 0, duration: dur }, dur);

    tl.seek(Math.random() * dur * 2);       // lệch pha để cả lớp không thở giống hệt nhau
    runners[pid] = tl;
  }

  function stopRun(pid) {
    var tl = runners[pid];
    if (tl) { tl.kill(); delete runners[pid]; }
  }

  /* Người chơi bị loại: dừng guồng chân, về tư thế đứng */
  function freeze(pid, el) {
    stopRun(pid);
    if (!G || !el) return;
    ['head'].forEach(function (n) {
      var p = part(el, n);
      if (p) G.to(p, { rotate: 0, duration: 0.3, ease: 'power2.out' });
    });
    var body = part(el, 'body');
    if (body) G.to(body, { y: 0, duration: 0.3 });
  }

  /* ---- Nhảy mừng khi trả lời đúng ---------------------------------------
     Trả về Promise để nơi gọi có thể chờ animation xong nếu cần.
     Cả thân bật lên theo cung rồi tiếp đất; chân không gập để tránh xấu.  */
  function jump(pid, el) {
    return new Promise(function (resolve) {
      if (!G || !el) return resolve();
      var fig = el.querySelector('.char-figure') || el;
      var head = part(el, 'head');   // tay không xoay, xem ghi chú ở startRun
      var tl = runners[pid];
      if (tl) tl.pause();

      var jumpTl = G.timeline({
        onComplete: function () {
          if (tl) tl.play();
          resolve();
        }
      });

      jumpTl
        // lấy đà: khuỵu xuống
        .to(fig, { y: 4, scaleY: 0.92, duration: 0.12, ease: 'power2.in' }, 0)
        // bật lên, ngả người ra sau một chút
        .to(fig, { y: -46, scaleY: 1.04, rotate: -12, duration: 0.3, ease: 'power2.out' }, 0.12)
        // qua đỉnh, chúi về trước
        .to(fig, { y: -34, rotate: 8, duration: 0.22, ease: 'sine.inOut' }, 0.42)
        // tiếp đất
        .to(fig, { y: 0, rotate: 0, scaleY: 1, duration: 0.24, ease: 'power2.in' }, 0.64)
        // nhún nhẹ khi chạm đất
        .to(fig, { scaleY: 0.9, duration: 0.08, ease: 'power2.out' }, 0.88)
        .to(fig, { scaleY: 1, duration: 0.16, ease: 'elastic.out(1,0.45)' }, 0.96);

      if (head) {
        jumpTl.to(head, { rotate: -10, duration: 0.3 }, 0.12)
              .to(head, { rotate: 0, duration: 0.3 }, 0.5);
      }
    });
  }

  /* Reo mừng khi về đích */
  function cheer(pid, el) {
    if (!G || !el) return;
    var head = part(el, 'head');
    if (head) G.fromTo(head, { rotate: -12 }, { rotate: 12, duration: 0.26, yoyo: true, repeat: 5, ease: 'sine.inOut' });
  }

  /* Dọn sạch khi dựng lại danh sách người chơi */
  function reset() {
    Object.keys(runners).forEach(stopRun);
  }

  global.BattleAnim = {
    available: !!G,
    startRun: startRun,
    stopRun: stopRun,
    freeze: freeze,
    jump: jump,
    cheer: cheer,
    reset: reset
  };
})(window);
