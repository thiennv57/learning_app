/* ==========================================================================
   ĐƯỜNG ĐUA TRƯỚC CỔNG TRƯỜNG

   Dựng khung cảnh và tính chỗ đứng cho từng người chơi.

   Luật chạy: ai CAO ĐIỂM chạy trước (gần chiếc cúp vàng ở đích), ai thấp
   điểm chạy sau. Trên mặt đường không đánh số — chỉ có tên và điểm nổi trên
   đầu mỗi nhân vật.
   ========================================================================== */

(function (global) {
  'use strict';

  var RUN_START = 8;    // % chiều ngang: mép trái của mặt đường
  var RUN_FINISH = 82;  // % chiều ngang: chỗ đặt chiếc cúp

  /* Khoảng điểm hiện có trên đường đua */
  function scoreRange(scores) {
    var vals = (scores || []).map(Number).filter(function (v) { return isFinite(v); });
    if (!vals.length) return { lo: 0, hi: 0, flat: true };
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    return { lo: lo, hi: hi, flat: hi - lo < 0.5 };
  }

  /* Chỗ đứng theo điểm. Mọi người bằng điểm (đầu trận) → cùng vạch xuất phát. */
  function runX(score, range) {
    if (!range || range.flat) return RUN_START;
    var t = (Number(score) - range.lo) / (range.hi - range.lo);
    t = Math.max(0, Math.min(1, t));
    return RUN_START + (RUN_FINISH - RUN_START) * t;
  }

  /* ---- Chế độ ĐỒNG ĐỘI ------------------------------------------------
     Vị trí trên đường do TỔNG ĐIỂM CỦA ĐỘI quyết định, nên cả đội đứng
     chụm lại một chỗ và các đội cách nhau theo điểm cao → thấp.
     Trong một đội, mỗi thành viên lệch nhau một chút cho khỏi che nhau.   */
  var MATE_GAP = 2.4;   // % chiều ngang giữa hai thành viên cùng đội
  var MIN_X = 9;        // lề trái tối thiểu, chừa chỗ cho biển tên

  /* Chỗ đứng của từng ĐỘI trên đường đua.

     Chỉ chia theo điểm thì hai đội sát điểm nhau (ví dụ 555 và 550) sẽ nằm
     đè lên nhau và các thành viên xen kẽ, nhìn như một đám lộn xộn. Nên sau
     khi xếp theo điểm, ta ép mỗi đội cách đội trên nó một khoảng tối thiểu
     đủ chứa trọn một cụm — thứ tự vẫn đúng theo điểm, mà mỗi đội vẫn là một
     khối riêng.                                                            */
  function teamBaseX(teams) {
    var list = (teams || []).slice().sort(function (a, b) { return b.hp - a.hp; });
    var range = scoreRange(list.map(function (t) { return t.hp; }));
    var widest = 0;
    list.forEach(function (t) {
      widest = Math.max(widest, ((t.members || []).length - 1) * MATE_GAP);
    });
    var gap = widest + MATE_GAP * 1.6;   // bề ngang một cụm, cộng khoảng hở
    var out = {};
    var prev = null;
    list.forEach(function (t) {
      var x = runX(t.hp, range);
      if (prev !== null && x > prev - gap) x = prev - gap;
      prev = x;
      out[t.team_id] = x;
    });
    // Nếu đẩy xuống quá mép trái thì dồn cả bảng sang phải cho cân
    var lowest = prev;
    var floor = MIN_X + widest;
    if (lowest !== null && lowest < floor) {
      var shift = floor - lowest;
      Object.keys(out).forEach(function (k) {
        out[k] = Math.min(RUN_FINISH, out[k] + shift);
      });
    }
    return out;
  }

  function teamX(baseX, mateIndex, mateCount) {
    // Người điểm cao nhất của đội đứng đúng mốc của đội, các bạn còn lại xếp
    // lùi về sau — nhờ vậy đội dẫn đầu không bị dồn cục ở vạch đích.
    var off = -(mateIndex || 0) * MATE_GAP;
    return Math.max(MIN_X, Math.min(RUN_FINISH, baseX + off));
  }

  /* Hàng chạy thứ i trên mặt đường (tính theo % chiều cao của sân khấu).
     Mặt đường chiếm khoảng 58%–96%; người ở hàng dưới đứng gần người xem.  */
  var ROW_TOP = 74;     // % chiều cao: hàng trong cùng, ngay dưới mép vỉa hè
  var ROW_BOTTOM = 96;  // % chiều cao: hàng ngoài cùng, gần người xem
  var MAX_ROWS = 4;     // nhiều người thì xếp vòng lại, đừng chia thêm hàng

  function rowCount(n) { return Math.max(1, Math.min(MAX_ROWS, n)); }

  /* Hàng đứng của người thứ i. Quá 4 người thì xếp vòng về hàng đầu — vị trí
     trên đường vẫn khác nhau vì điểm khác nhau, nên không bị chồng lên nhau. */
  function rowY(i, n) {
    var rows = rowCount(n);
    if (rows === 1) return (ROW_TOP + ROW_BOTTOM) / 2;
    return ROW_TOP + (ROW_BOTTOM - ROW_TOP) * ((i % rows) / (rows - 1));
  }

  /* Cỡ nhân vật: co lại cho vừa số hàng, để không ai chèn lên ai */
  function fitScale(stageEl, n) {
    var h = (stageEl && stageEl.clientHeight) || 480;
    var rowPx = (ROW_BOTTOM - ROW_TOP) / 100 * h / rowCount(n);
    return Math.max(0.78, Math.min(1.3, rowPx / 30));
  }

  /* Báo bề ngang sân khấu cho CSS (biến --stage-w) và giữ nó khớp khi cửa sổ
     đổi cỡ hoặc vào/ra toàn màn hình. Nhờ biến này mà vị trí nhân vật tính
     được bằng transform thay vì thuộc tính left.                          */
  function watchStage(stageEl) {
    if (!stageEl) return;
    var apply = function () {
      stageEl.style.setProperty('--stage-w', (stageEl.clientWidth || 1000) + 'px');
    };
    apply();
    if (stageEl._stageRO || !global.ResizeObserver) return;
    stageEl._stageRO = new global.ResizeObserver(apply);
    stageEl._stageRO.observe(stageEl);
  }

  /* Một đám mây tròn mập, có mắt và má hồng như trong tranh thiếu nhi.
     s là hệ số thu nhỏ để mây xa trông nhỏ hơn mây gần.                  */
  function cloudSvg(cx, cy, s) {
    return '<g transform="translate(' + cx + ',' + cy + ') scale(' + s + ')">' +
      '<g fill="#FFFFFF" stroke="#D8ECF6" stroke-width="3" stroke-linejoin="round">' +
        '<ellipse cx="-46" cy="6" rx="34" ry="22"/><ellipse cx="46" cy="6" rx="34" ry="22"/>' +
        '<ellipse cx="-14" cy="-10" rx="40" ry="30"/><ellipse cx="22" cy="-6" rx="34" ry="26"/>' +
        '<rect x="-74" y="2" width="148" height="26" rx="13"/>' +
      '</g>' +
      '<g fill="#7D93A3">' +
        '<path d="M-20 2 a4 5 0 0 1 8 0"/><path d="M10 2 a4 5 0 0 1 8 0"/>' +
      '</g>' +
      '<g fill="#FFB6C1" opacity=".75">' +
        '<ellipse cx="-30" cy="12" rx="7" ry="4"/><ellipse cx="28" cy="12" rx="7" ry="4"/>' +
      '</g>' +
    '</g>';
  }

  /* ---- Khung cảnh: trời, cây phượng, dãy nhà vàng, cổng đỏ, mặt đường ---- */
  function sceneMarkup() {
    return '' +
'<svg class="street" viewBox="0 0 1000 560" preserveAspectRatio="xMidYMax slice">' +
  '<defs>' +
    '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0" stop-color="#3CA9EE"/><stop offset=".62" stop-color="#8FD6F7"/>' +
      '<stop offset="1" stop-color="#CCEEFB"/>' +
    '</linearGradient>' +
    '<linearGradient id="road" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0" stop-color="#B4B4BA"/><stop offset="1" stop-color="#90909A"/>' +
    '</linearGradient>' +
    '<radialGradient id="sunGlow" cx=".5" cy=".5" r=".5">' +
      '<stop offset=".45" stop-color="#FFE98A" stop-opacity=".9"/>' +
      '<stop offset="1" stop-color="#FFE98A" stop-opacity="0"/>' +
    '</radialGradient>' +
    '<linearGradient id="hillFar" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0" stop-color="#8FD08C"/><stop offset="1" stop-color="#6FBE74"/>' +
    '</linearGradient>' +
    '<linearGradient id="hillNear" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0" stop-color="#75C277"/><stop offset="1" stop-color="#55A95F"/>' +
    '</linearGradient>' +
  '</defs>' +

  /* bầu trời */
  '<rect width="1000" height="330" fill="url(#sky)"/>' +

  /* mặt trời tươi cười ở góc phải */
  '<circle cx="762" cy="58" r="92" fill="url(#sunGlow)"/>' +
  '<circle cx="762" cy="58" r="42" fill="#FFE071" stroke="#F0B93C" stroke-width="4"/>' +
  '<g fill="#5A4036">' +
    '<path d="M746 50 a5 6 0 0 1 10 0" /><path d="M768 50 a5 6 0 0 1 10 0"/>' +
  '</g>' +
  '<path d="M752 66 q10 9 20 0" stroke="#5A4036" stroke-width="3.4" fill="none" stroke-linecap="round"/>' +
  '<g fill="#FFAFA0" opacity=".75">' +
    '<ellipse cx="740" cy="64" rx="7" ry="4"/><ellipse cx="784" cy="64" rx="7" ry="4"/>' +
  '</g>' +

  /* mây tròn mập có mặt cười */
  cloudSvg(292, 62, 1) + cloudSvg(560, 42, .82) + cloudSvg(120, 108, .62) +

  /* dây điện vắt ngang */
  '<g stroke="#3A3F47" stroke-width="2" fill="none" opacity=".75">' +
    '<path d="M0 96 Q500 124 1000 92"/><path d="M0 110 Q500 140 1000 106"/>' +
    '<path d="M0 124 Q500 156 1000 120"/><path d="M0 138 Q500 170 1000 134"/>' +
  '</g>' +
  '<rect x="868" y="92" width="13" height="250" fill="#A4A9B0"/>' +
  '<rect x="856" y="110" width="37" height="7" rx="3" fill="#8D939B"/>' +

  /* đồi xanh thoai thoải phía sau trường */
  '<path d="M-40 268 q130 -96 270 -40 q120 48 250 -14 q140 -66 280 -6 q120 48 280 10 l0 120 l-1080 0 Z" ' +
    'fill="url(#hillFar)"/>' +
  '<path d="M-40 300 q160 -70 310 -18 q150 50 290 -10 q160 -62 300 0 q90 36 180 20 l0 100 l-1080 0 Z" ' +
    'fill="url(#hillNear)"/>' +

  /* dãy nhà vàng của trường */
  '<rect x="120" y="150" width="760" height="180" rx="8" fill="#F6C94F" ' +
    'stroke="#C98F28" stroke-width="4"/>' +
  '<rect x="120" y="150" width="760" height="16" rx="8" fill="#E0AE2C"/>' +
  '<g fill="#BFE3F5" stroke="#8FC8E4" stroke-width="3">' +
    '<rect x="168" y="186" width="52" height="62" rx="3"/>' +
    '<rect x="246" y="186" width="52" height="62" rx="3"/>' +
    '<rect x="628" y="186" width="52" height="62" rx="3"/>' +
    '<rect x="706" y="186" width="52" height="62" rx="3"/>' +
  '</g>' +
  '<g fill="#F7F7F2" stroke="#D9D4C4" stroke-width="3">' +
    '<circle cx="250" cy="206" r="15"/><circle cx="790" cy="206" r="15"/>' +
  '</g>' +

  /* cổng sắt đỏ ở giữa */
  '<rect x="430" y="214" width="150" height="116" fill="#C62828"/>' +
  '<g stroke="#8E1B1B" stroke-width="4">' +
    '<path d="M430 240 L580 300 M580 240 L430 300"/>' +
  '</g>' +
  '<g fill="#C62828">' +
    '<rect x="432" y="206" width="10" height="124" rx="4"/>' +
    '<rect x="568" y="206" width="10" height="124" rx="4"/>' +
  '</g>' +
  '<rect x="376" y="190" width="30" height="140" fill="#D13A2B"/>' +
  '<rect x="604" y="190" width="30" height="140" fill="#D13A2B"/>' +

  /* Biển tên vắt ngang phía trên cổng. Vẽ SAU hai trụ cổng để không bị che. */
  '<rect x="314" y="150" width="372" height="58" rx="9" fill="#FFFDF5" stroke="#C62828" stroke-width="5"/>' +
  '<rect x="314" y="150" width="372" height="13" rx="6" fill="#C62828"/>' +
  // textLength ép chữ luôn vừa khung biển, dù font tải về hay chưa
  '<text class="school-sign" x="500" y="193" text-anchor="middle" ' +
    'textLength="336" lengthAdjust="spacingAndGlyphs">LÝ HÓA THẦY THIỆN</text>' +

  /* hàng rào xanh hai bên */
  '<g fill="#7CC36A">' +
    '<rect x="142" y="256" width="212" height="56" rx="4"/>' +
    '<rect x="656" y="256" width="206" height="56" rx="4"/>' +
  '</g>' +
  '<g fill="#5FA94F">' +
    '<rect x="160" y="262" width="7" height="44"/><rect x="190" y="262" width="7" height="44"/>' +
    '<rect x="220" y="262" width="7" height="44"/><rect x="250" y="262" width="7" height="44"/>' +
    '<rect x="280" y="262" width="7" height="44"/><rect x="310" y="262" width="7" height="44"/>' +
    '<rect x="676" y="262" width="7" height="44"/><rect x="706" y="262" width="7" height="44"/>' +
    '<rect x="736" y="262" width="7" height="44"/><rect x="766" y="262" width="7" height="44"/>' +
    '<rect x="796" y="262" width="7" height="44"/><rect x="826" y="262" width="7" height="44"/>' +
  '</g>' +

  /* cây phượng bên trái, hoa đỏ rụng đầy vỉa hè */
  '<rect x="86" y="186" width="20" height="120" fill="#8B5A3C"/>' +
  '<g fill="#4FA64B">' +
    '<ellipse cx="78" cy="118" rx="96" ry="60"/><ellipse cx="186" cy="100" rx="78" ry="52"/>' +
    '<ellipse cx="252" cy="134" rx="58" ry="38"/><ellipse cx="18" cy="168" rx="70" ry="44"/>' +
  '</g>' +
  '<g fill="#E8402F">' +
    '<circle cx="36" cy="86" r="9"/><circle cx="86" cy="64" r="8"/><circle cx="134" cy="88" r="9"/>' +
    '<circle cx="182" cy="62" r="8"/><circle cx="226" cy="100" r="9"/><circle cx="62" cy="130" r="8"/>' +
    '<circle cx="116" cy="142" r="7"/><circle cx="166" cy="128" r="9"/><circle cx="214" cy="146" r="7"/>' +
    '<circle cx="12" cy="116" r="8"/><circle cx="256" cy="120" r="7"/><circle cx="148" cy="46" r="7"/>' +
  '</g>' +

  /* vỉa hè */
  '<rect x="0" y="330" width="1000" height="44" fill="#E9E6DE"/>' +
  '<g stroke="#D3CFC4" stroke-width="3">' +
    '<path d="M0 352 H1000"/><path d="M120 330 V374 M300 330 V374 M480 330 V374 M660 330 V374 M840 330 V374"/>' +
  '</g>' +
  '<g fill="#E8402F" opacity=".85">' +
    '<ellipse cx="54" cy="344" rx="5" ry="3"/><ellipse cx="96" cy="358" rx="5" ry="3"/>' +
    '<ellipse cx="146" cy="340" rx="4" ry="2.5"/><ellipse cx="196" cy="362" rx="5" ry="3"/>' +
    '<ellipse cx="252" cy="346" rx="4" ry="2.5"/>' +
  '</g>' +

  /* mặt đường — chỗ các bạn chạy đua */
  '<rect x="0" y="374" width="1000" height="186" fill="url(#road)"/>' +
  '<rect x="0" y="374" width="1000" height="7" fill="#7C7C86" opacity=".45"/>' +
  // vạch kẻ đứt giữa đường, mờ để không át nhân vật
  '<g stroke="#FFF6D8" stroke-width="7" stroke-linecap="round" opacity=".5" ' +
    'stroke-dasharray="54 46">' +
    '<path d="M0 436 H1000"/>' +
  '</g>' +
  '<g stroke="#80808A" stroke-width="2" opacity=".35" fill="none">' +
    '<path d="M60 476 q40 -8 84 2"/><path d="M420 516 q50 -10 96 4"/><path d="M700 462 q44 -8 88 4"/>' +
  '</g>' +
  // hoa phượng rụng trên đường, rải rác cho đỡ trống
  '<g fill="#E8402F" opacity=".5">' +
    '<ellipse cx="128" cy="414" rx="5" ry="3"/><ellipse cx="316" cy="446" rx="4" ry="2.5"/>' +
    '<ellipse cx="208" cy="498" rx="5" ry="3"/><ellipse cx="548" cy="410" rx="4" ry="2.5"/>' +
    '<ellipse cx="640" cy="486" rx="5" ry="3"/><ellipse cx="862" cy="430" rx="4" ry="2.5"/>' +
    '<ellipse cx="930" cy="508" rx="5" ry="3"/><ellipse cx="406" cy="540" rx="4" ry="2.5"/>' +
  '</g>' +
'</svg>';
  }

  /* ---- Chiếc cúp vàng ở đích ---- */
  function trophySvg() {
    return '' +
'<svg viewBox="0 0 100 120" role="img" aria-label="Cúp vô địch">' +
  '<ellipse cx="50" cy="114" rx="30" ry="6" fill="rgba(0,0,0,.18)"/>' +
  '<rect x="30" y="100" width="40" height="11" rx="3" fill="#C9962C"/>' +
  '<rect x="36" y="90" width="28" height="12" rx="3" fill="#E0AE3A"/>' +
  '<rect x="44" y="72" width="12" height="20" fill="#E8BC4C"/>' +
  '<path d="M24 20 h52 v22 a26 26 0 0 1 -52 0 Z" fill="#F6C83C"/>' +
  '<path d="M24 20 h52 v8 h-52 Z" fill="#FFE9A8"/>' +
  '<path d="M24 26 q-16 0 -16 12 q0 12 16 14 l0 -8 q-8 -2 -8 -7 q0 -4 8 -4 Z" fill="#E8BC4C"/>' +
  '<path d="M76 26 q16 0 16 12 q0 12 -16 14 l0 -8 q8 -2 8 -7 q0 -4 -8 -4 Z" fill="#E8BC4C"/>' +
  '<path d="M44 34 l6 12 l6 -12 l-4 16 h-4 Z" fill="#FFF3CE" opacity=".8"/>' +
'</svg>';
  }

  global.BattleHero = {
    sceneMarkup: sceneMarkup,
    trophySvg: trophySvg,
    scoreRange: scoreRange,
    runX: runX,
    teamX: teamX,
    teamBaseX: teamBaseX,
    rowY: rowY,
    rowCount: rowCount,
    fitScale: fitScale,
    watchStage: watchStage,
    RUN_START: RUN_START,
    RUN_FINISH: RUN_FINISH
  };
})(window);
