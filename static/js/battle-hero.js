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

  /* Cỡ nhân vật: co theo bề cao một hàng, để các hàng không chèn kín nhau. */
  function fitScale(stageEl, n) {
    var h = (stageEl && stageEl.clientHeight) || 480;
    var rowPx = (ROW_BOTTOM - ROW_TOP) / 100 * h / rowCount(n);
    return Math.max(0.78, Math.min(1.3, rowPx / 30));
  }

  /* Báo bề ngang sân khấu cho CSS (biến --stage-w) và giữ nó khớp khi cửa sổ
     đổi cỡ hoặc vào/ra toàn màn hình. Nhờ biến này mà vị trí nhân vật tính
     được bằng transform thay vì thuộc tính left.                          */
  function watchStage(stageEl, onResize) {
    if (!stageEl) return;
    if (onResize) stageEl._stageCb = onResize;   // tính lại cỡ nhân vật, xem fitScale
    var apply = function () {
      stageEl.style.setProperty('--stage-w', (stageEl.clientWidth || 1000) + 'px');
      if (stageEl._stageCb) stageEl._stageCb();
    };
    apply();
    if (stageEl._stageRO || !global.ResizeObserver) return;
    stageEl._stageRO = new global.ResizeObserver(apply);
    stageEl._stageRO.observe(stageEl);
  }

  /* Một đám mây tròn mập, có mắt và má hồng như trong tranh thiếu nhi.
     s là hệ số thu nhỏ để mây xa trông nhỏ hơn mây gần.                  */
  /* Mây tích: đáy gần phẳng, đỉnh vồng thành nhiều cụm to nhỏ khác nhau.
     Ba lớp — bóng xám dưới bụng, thân trắng, mảng nắng trên đỉnh — cho mây
     có khối thay vì là một mảng trắng dẹt. v chọn một trong hai dáng để ba
     đám mây trên trời không giống hệt nhau.                               */
  function cloudSvg(cx, cy, s, v) {
    var lumps = v
      ? '<ellipse cx="-52" cy="4" rx="28" ry="19"/><ellipse cx="-20" cy="-14" rx="36" ry="28"/>' +
        '<ellipse cx="16" cy="-4" rx="30" ry="23"/><ellipse cx="46" cy="8" rx="24" ry="16"/>'
      : '<ellipse cx="-46" cy="6" rx="24" ry="16"/><ellipse cx="-16" cy="-6" rx="32" ry="24"/>' +
        '<ellipse cx="18" cy="-18" rx="34" ry="27"/><ellipse cx="52" cy="2" rx="28" ry="20"/>';
    var base = v ? '<rect x="-78" y="2" width="152" height="22" rx="11"/>'
                 : '<rect x="-68" y="0" width="150" height="22" rx="11"/>';
    return '<g transform="translate(' + cx + ',' + cy + ') scale(' + s + ')">' +
      // bụng mây: hơi xám, lệch xuống dưới
      '<g fill="#BFD6E6" transform="translate(0,7)">' + lumps + base + '</g>' +
      '<g fill="#FFFFFF">' + lumps + base + '</g>' +
      // mảng nắng trên đỉnh
      '<g fill="#FFFFFF" opacity=".9" transform="translate(-4,-7) scale(.82)">' + lumps + '</g>' +
    '</g>';
  }

  /* Tán cây dựng bằng nhiều cụm lá chồng nhau, nên viền ngoài lồi lõm tự
     nhiên chứ không phải vài hình bầu dục trơn.                          */
  function leaves(list, fill) {
    return '<g fill="' + fill + '">' + list.map(function (c) {
      return '<circle cx="' + c[0] + '" cy="' + c[1] + '" r="' + c[2] + '"/>';
    }).join('') + '</g>';
  }

  /* Chùm hoa phượng: vài chấm nhỏ sát nhau, cỡ bằng một cụm lá nên nhìn như
     hoa nở lẫn trong tán chứ không phải chấm tròn dán lên.               */
  function blossom(x, y, r) {
    return '<g transform="translate(' + x + ',' + y + ')" fill="#DF5137">' +
      '<circle cx="0" cy="0" r="' + r + '"/>' +
      '<circle cx="' + (r * 1.25) + '" cy="' + (r * 0.45) + '" r="' + (r * 0.72) + '"/>' +
      '<circle cx="' + (-r * 0.6) + '" cy="' + (-r * 0.95) + '" r="' + (r * 0.6) + '"/>' +
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
  '<circle cx="762" cy="58" r="44" fill="#FFDF72"/>' +
  '<circle cx="756" cy="52" r="34" fill="#FFF0AC" opacity=".85"/>' +

  /* mây tròn mập có mặt cười */
  cloudSvg(292, 62, 1, 0) + cloudSvg(560, 42, .82, 1) + cloudSvg(120, 108, .6, 1) +

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

  /* cây phượng bên trái: gốc to, thân chia cành, tán lá nhiều lớp */
  // thân cây: gốc loe ra bám đất, thuôn dần lên chỗ chia cành
  '<path d="M76 316 q2 -8 7 -12 q2 -38 4 -58 q1 -14 6 -26 l16 4 q-6 12 -7 24 ' +
    'q-2 22 0 56 q6 4 8 12 Z" fill="#7C5538"/>' +
  // cành chính toả ra, nhỏ dần về đầu cành
  '<g stroke="#7C5538" fill="none" stroke-linecap="round">' +
    '<path d="M100 214 q-28 -10 -48 -32" stroke-width="12"/>' +
    '<path d="M104 206 q26 -16 52 -24" stroke-width="11"/>' +
    '<path d="M104 198 q8 -26 4 -48" stroke-width="10"/>' +
    '<path d="M58 186 q-14 -12 -26 -16" stroke-width="6.5"/>' +
    '<path d="M150 184 q18 -10 34 -10" stroke-width="6.5"/>' +
    '<path d="M106 156 q-12 -18 -26 -26" stroke-width="5.5"/>' +
  '</g>' +
  // vân thân
  '<g stroke="#5E3F28" stroke-width="2.4" fill="none" opacity=".5" stroke-linecap="round">' +
    '<path d="M82 300 q6 -42 10 -72"/><path d="M98 300 q2 -40 5 -66"/>' +
  '</g>' +
  /* Tán lá ba lớp. Lớp nền vẽ đủ dày để các vòng tròn dính lại thành một
     khối, hai lớp sau nhỏ hơn và nằm hẳn bên trong nên mép tròn chỉ thấy ở
     trong tán, đọc ra là cụm lá chứ không phải mấy quả bóng rời.         */
  leaves([[26,152,60],[78,128,62],[134,114,62],[188,128,56],[236,152,46],
          [-8,180,48],[48,186,50],[104,174,54],[160,176,50],[214,188,40],
          [112,148,66]], '#357539') +
  leaves([[34,140,44],[84,116,46],[136,104,46],[186,118,40],[228,142,32],
          [52,172,34],[106,160,40],[158,162,34],[6,168,30]], '#43893F') +
  leaves([[36,122,26],[88,98,28],[136,88,28],[182,102,22],[62,152,18],
          [114,140,22],[220,126,16]], '#549B47') +
  // hoa phượng nở rải trên tán, dồn về phía ngọn
  blossom(34, 104, 5) + blossom(74, 84, 5) + blossom(126, 74, 5) +
  blossom(172, 86, 4.5) + blossom(214, 112, 4.5) + blossom(10, 140, 4.5) +
  blossom(58, 132, 4) + blossom(106, 118, 4.5) + blossom(154, 126, 4) +
  blossom(196, 146, 4) + blossom(242, 142, 4) + blossom(84, 158, 4) +
  blossom(140, 160, 4) + blossom(30, 176, 4) +

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
