/* ==========================================================================
   NHÂN VẬT — học sinh chibi, vẽ bằng SVG

   Tỉ lệ chibi: đầu chiếm gần nửa chiều cao, thân và chân ngắn mập. Mắt to
   bóng có hai đốm sáng, má ửng hồng, viền nâu mềm thay vì đen — đúng kiểu
   hoạt hình dễ thương cho học sinh.

   Cả lớp dùng chung một dáng và một bộ đồng phục (áo trắng, khăn quàng đỏ,
   quần/váy xanh than, dép quai hậu), chỉ khác kiểu tóc, màu tóc, màu mắt và
   phụ kiện — nhờ vậy không ai to nhỏ hơn ai.

   Hai người chọn trùng nhân vật vẫn phân biệt được: assignColors() phát cho
   mỗi người một tông phụ kiện khác nhau.
   ========================================================================== */

(function (global) {
  'use strict';

  var SKIN       = '#FFD9B8';
  var SKIN_SHADE = '#F0B98E';
  var SHIRT      = '#FFFFFF';
  var SHIRT_SHADE= '#E7ECF4';
  var NAVY       = '#2F4F93';
  var NAVY_DARK  = '#21386B';
  var SCARF      = '#E8413A';
  var SCARF_DARK = '#BE2C27';
  var SANDAL     = '#4C4C58';
  var LINE       = '#5A4036';   // viền nâu mềm, không dùng đen
  var LASH       = '#3A2B33';
  var BLUSH      = '#FF9BB3';

  /* kind: 'boy' | 'girl' — hair: kiểu tóc — eye: màu mắt — extra: phụ kiện */
  var CHARACTERS = [
    { id: 'boy_short', name: 'Nam tóc ngắn', kind: 'boy',  hair: 'short',    hairCol: '#3A2A22', eye: '#5B4636', hue: 210 },
    { id: 'boy_glass', name: 'Nam đeo kính', kind: 'boy',  hair: 'short',    hairCol: '#4A3326', eye: '#3F7A52', hue: 150, extra: 'glasses' },
    { id: 'boy_cap',   name: 'Nam đội mũ',   kind: 'boy',  hair: 'short',    hairCol: '#2B2129', eye: '#4A5C7A', hue: 20,  extra: 'cap' },
    { id: 'boy_spiky', name: 'Nam tóc dựng', kind: 'boy',  hair: 'spiky',    hairCol: '#C4643A', eye: '#3F7A52', hue: 275 },
    { id: 'girl_tail', name: 'Nữ tóc đuôi',  kind: 'girl', hair: 'ponytail', hairCol: '#2B2129', eye: '#5B4636', hue: 340 },
    { id: 'girl_two',  name: 'Nữ hai bím',   kind: 'girl', hair: 'twintail', hairCol: '#4A3326', eye: '#7A4A3C', hue: 300 },
    { id: 'girl_bob',  name: 'Nữ tóc ngang', kind: 'girl', hair: 'bob',      hairCol: '#2B2129', eye: '#4A5C7A', hue: 180 },
    { id: 'girl_bow',  name: 'Nữ nơ cài',    kind: 'girl', hair: 'bob',      hairCol: '#8A5A3A', eye: '#5B4636', hue: 45,  extra: 'bow' },
    { id: 'boy_curly', name: 'Nam tóc xoăn', kind: 'boy',  hair: 'curly',    hairCol: '#3F2E22', eye: '#3F7A52', hue: 95 },
    { id: 'girl_long', name: 'Nữ tóc dài',   kind: 'girl', hair: 'long',     hairCol: '#2B2129', eye: '#7A4A3C', hue: 15 }
  ];

  var BY_ID = {};
  CHARACTERS.forEach(function (c) { BY_ID[c.id] = c; });

  function get(id) { return BY_ID[id] || CHARACTERS[0]; }

  /* Lệch tông phụ kiện cho người thứ 2, 3… chọn trùng nhân vật */
  var HUE_SHIFT = [0, 150, 75, 215, 40, 265, 110, 190, 300, 20];

  function paletteFor(id, variant) {
    var c = get(id);
    var h = (c.hue + HUE_SHIFT[(variant || 0) % HUE_SHIFT.length]) % 360;
    return {
      hue: h,
      accent: 'hsl(' + h + ',74%,60%)',
      accentDark: 'hsl(' + h + ',64%,44%)',
      fur: 'hsl(' + h + ',55%,55%)',
      furDark: 'hsl(' + h + ',50%,38%)',
      furPale: 'hsl(' + h + ',62%,88%)'
    };
  }

  function assignColors(players) {
    var seen = {}, out = {};
    (players || []).forEach(function (p) {
      var id = (p.avatar && BY_ID[p.avatar]) ? p.avatar : CHARACTERS[0].id;
      var v = seen[id] || 0;
      seen[id] = v + 1;
      out[p.player_id] = { animal: id, variant: v, palette: paletteFor(id, v) };
    });
    return out;
  }

  /* ------------------------------ Tóc -----------------------------------
     Đầu là ellipse tâm (50,36) bán kính 25 x 24, nên tóc phải phủ từ y≈12
     xuống hai bên thái dương y≈46. Mỗi kiểu kèm một dải sáng bóng.       */

  function gloss(d) {
    return '<path d="' + d + '" fill="#FFFFFF" opacity=".14"/>';
  }

  function hairSvg(c, pal) {
    var H = c.hairCol;
    switch (c.hair) {

      case 'spiky':
        return '<path d="M25 36 q-1 -25 25 -25 q26 0 25 25 q-3 -8 -7 -3 q-3 -10 -8 -4 q-4 -11 -10 -4 q-5 -9 -10 -1 q-4 -7 -8 4 q-4 -6 -7 8 Z" fill="' + H + '"/>' +
               gloss('M37 20 q7 -6 15 -4 q-8 2 -12 8 Z');

      case 'ponytail':
        return '<path d="M24 40 q-11 3 -13 15 q-1 9 7 11 q3 -14 10 -18 Z" fill="' + H + '"/>' +
               '<ellipse cx="22" cy="40" rx="5.5" ry="4" fill="' + pal.accent + '" stroke="' + LINE + '" stroke-width="1.6"/>' +
               '<path d="M25 36 q-1 -25 25 -25 q26 0 25 25 q-6 -13 -25 -13 q-19 0 -25 13 Z" fill="' + H + '"/>' +
               gloss('M38 18 q9 -5 18 -3 q-10 2 -15 8 Z');

      case 'twintail':
        return '<ellipse cx="20" cy="47" rx="7.5" ry="12" fill="' + H + '"/>' +
               '<ellipse cx="80" cy="47" rx="7.5" ry="12" fill="' + H + '"/>' +
               '<path d="M25 36 q-1 -25 25 -25 q26 0 25 25 q-6 -13 -25 -13 q-19 0 -25 13 Z" fill="' + H + '"/>' +
               '<ellipse cx="22" cy="36" rx="5" ry="3.8" fill="' + pal.accent + '" stroke="' + LINE + '" stroke-width="1.6"/>' +
               '<ellipse cx="78" cy="36" rx="5" ry="3.8" fill="' + pal.accent + '" stroke="' + LINE + '" stroke-width="1.6"/>' +
               gloss('M38 18 q9 -5 18 -3 q-10 2 -15 8 Z');

      case 'curly':
        return '<g fill="' + H + '">' +
                 '<circle cx="30" cy="26" r="11"/><circle cx="42" cy="16" r="12"/>' +
                 '<circle cx="58" cy="16" r="12"/><circle cx="70" cy="26" r="11"/>' +
                 '<circle cx="50" cy="20" r="12"/>' +
                 '<path d="M25 36 q-1 -20 25 -20 q26 0 25 20 q-6 -11 -25 -11 q-19 0 -25 11 Z"/>' +
               '</g>' +
               gloss('M36 14 q8 -5 16 -3 q-9 2 -13 8 Z');

      case 'long':
        return '<path d="M23 34 q0 -26 27 -26 q27 0 27 26 l3 34 q-8 6 -12 -2 l-2 -26 q-16 7 -32 0 l-2 26 q-4 8 -12 2 Z" fill="' + H + '"/>' +
               '<ellipse cx="30" cy="22" rx="5" ry="3.8" fill="' + pal.accent + '" stroke="' + LINE + '" stroke-width="1.6"/>' +
               gloss('M38 16 q9 -5 18 -3 q-10 2 -15 8 Z');

      case 'bob':
        return '<path d="M24 36 q-1 -26 26 -26 q27 0 26 26 l0 14 q-7 -4 -8 -14 q-9 6 -18 6 q-9 0 -18 -6 q-1 10 -8 14 Z" fill="' + H + '"/>' +
               gloss('M37 17 q9 -5 18 -3 q-10 2 -14 8 Z');

      default: /* short */
        return '<path d="M25 36 q-1 -25 25 -25 q26 0 25 25 q-7 -14 -25 -14 q-18 0 -25 14 Z" fill="' + H + '"/>' +
               gloss('M38 18 q9 -5 18 -3 q-10 2 -15 8 Z');
    }
  }

  function extraSvg(c, pal) {
    if (c.extra === 'glasses') {
      return '<g fill="#FFFFFF" fill-opacity=".18" stroke="' + LINE + '" stroke-width="2.2">' +
               '<rect x="31" y="31" width="17" height="15" rx="7"/>' +
               '<rect x="52" y="31" width="17" height="15" rx="7"/>' +
               '<path d="M48 38 h4" fill="none"/>' +
             '</g>';
    }
    if (c.extra === 'cap') {
      return '<path d="M24 28 q1 -19 26 -19 q25 0 26 19 Z" fill="' + pal.accent + '" stroke="' + LINE + '" stroke-width="2.2" stroke-linejoin="round"/>' +
             '<path d="M74 27 q13 1 16 6 q-9 3 -18 2 Z" fill="' + pal.accentDark + '" stroke="' + LINE + '" stroke-width="2.2" stroke-linejoin="round"/>' +
             '<circle cx="50" cy="10" r="3" fill="' + pal.accentDark + '" stroke="' + LINE + '" stroke-width="1.6"/>';
    }
    if (c.extra === 'bow') {
      return '<g stroke="' + LINE + '" stroke-width="1.8" stroke-linejoin="round">' +
               '<path d="M70 17 l10 -6 l0 12 Z" fill="' + pal.accent + '"/>' +
               '<path d="M70 17 l10 6 l0 -12 Z" fill="' + pal.accentDark + '"/>' +
               '<circle cx="70" cy="17" r="3.2" fill="' + pal.accent + '"/>' +
             '</g>';
    }
    return '';
  }

  /* ------------------------------ Mắt -----------------------------------
     Mắt to kiểu chibi: tròng tối, một đốm sáng lớn trên trái và một đốm nhỏ
     dưới phải, mí trên dày tạo cảm giác mi mắt.                          */
  function eyeSvg(cx, col) {
    return '<g>' +
      '<ellipse cx="' + cx + '" cy="40" rx="7" ry="8.4" fill="#FFFFFF"/>' +
      '<ellipse cx="' + cx + '" cy="41" rx="6.2" ry="7.6" fill="' + col + '"/>' +
      '<ellipse cx="' + cx + '" cy="43" rx="4" ry="4.6" fill="' + LASH + '"/>' +
      '<circle cx="' + (cx - 2.2) + '" cy="37.6" r="2.6" fill="#FFFFFF"/>' +
      '<circle cx="' + (cx + 2.4) + '" cy="45" r="1.3" fill="#FFFFFF" opacity=".8"/>' +
      '<path d="M' + (cx - 7.2) + ' 37 q7 -6 14.4 0" stroke="' + LASH + '" stroke-width="2.6" ' +
        'fill="none" stroke-linecap="round"/>' +
    '</g>';
  }

  /* Học sinh chibi: đầu to, thân ngắn, chân mập, mặt hướng thẳng ra trước. */
  function kidSvg(c, pal, cls) {
    var bottom = (c.kind === 'girl')
      ? '<path d="M33 77 h34 l6 11 q-23 5 -46 0 Z" fill="' + NAVY + '" stroke="' + LINE + '" ' +
        'stroke-width="2.2" stroke-linejoin="round"/>' +
        '<path d="M33 77 h34 l1.2 2.6 q-18 2.6 -36.4 0 Z" fill="' + NAVY_DARK + '"/>'
      : '<path d="M34 77 h32 l1 11 h-12 l-5 -5 l-5 5 h-12 Z" fill="' + NAVY + '" stroke="' + LINE + '" ' +
        'stroke-width="2.2" stroke-linejoin="round"/>';

    return '<svg class="' + (cls || 'char-body') + '" viewBox="0 0 100 100" role="img" ' +
        'aria-label="' + c.name + '">' +
      '<g data-part="body" stroke-linecap="round" stroke-linejoin="round">' +

        /* chân mập ngắn + dép quai hậu */
        '<path d="M43 86 v5" stroke="' + LINE + '" stroke-width="12"/>' +
        '<path d="M57 86 v5" stroke="' + LINE + '" stroke-width="12"/>' +
        '<path d="M43 86 v5" stroke="' + SKIN_SHADE + '" stroke-width="8.4"/>' +
        '<path d="M57 86 v5" stroke="' + SKIN + '" stroke-width="8.4"/>' +
        '<rect x="36" y="90" width="13" height="7.6" rx="3.8" fill="' + SANDAL + '" ' +
          'stroke="' + LINE + '" stroke-width="2.2"/>' +
        '<rect x="51" y="90" width="13" height="7.6" rx="3.8" fill="' + SANDAL + '" ' +
          'stroke="' + LINE + '" stroke-width="2.2"/>' +

        /* tay sau (bên xa người xem) — vẽ trước thân cho có chiều sâu */
        '<path d="M33 68 l-3.5 10" stroke="' + LINE + '" stroke-width="11"/>' +
        '<path d="M33 68 l-3.5 10" stroke="' + SKIN_SHADE + '" stroke-width="7.4"/>' +
        '<circle cx="29" cy="79" r="4.4" fill="' + SKIN_SHADE + '" stroke="' + LINE + '" stroke-width="2"/>' +

        /* thân áo trắng, có tay áo ngắn */
        '<path d="M33 60 q17 -6 34 0 l2 18 q-19 6 -38 0 Z" fill="' + SHIRT + '" ' +
          'stroke="' + LINE + '" stroke-width="2.2"/>' +
        '<path d="M33 60 q17 -6 34 0 l.6 5 q-17 -4 -35.2 0 Z" fill="' + SHIRT_SHADE + '"/>' +
        bottom +
        '<path d="M34 61 q-7 2 -7 8 q5 3 10 1 Z" fill="' + SHIRT + '" stroke="' + LINE + '" ' +
          'stroke-width="2.2"/>' +
        '<path d="M66 61 q7 2 7 8 q-5 3 -10 1 Z" fill="' + SHIRT + '" stroke="' + LINE + '" ' +
          'stroke-width="2.2"/>' +

        /* khăn quàng đỏ */
        '<path d="M42 59 q8 6 16 0 l-1.6 5 q-6.4 3.6 -12.8 0 Z" fill="' + SCARF + '" ' +
          'stroke="' + LINE + '" stroke-width="2"/>' +
        '<path d="M50 63 l3.6 9 l-7.2 0 Z" fill="' + SCARF_DARK + '" stroke="' + LINE + '" stroke-width="2"/>' +

        /* tay trước — nhóm "tail" để hiệu ứng vẫy nhẹ bám vào */
        '<g data-part="tail" style="transform-origin:67px 68px">' +
          '<path d="M67 68 l3.5 10" stroke="' + LINE + '" stroke-width="11"/>' +
          '<path d="M67 68 l3.5 10" stroke="' + SKIN + '" stroke-width="7.4"/>' +
          '<circle cx="71" cy="79" r="4.6" fill="' + SKIN + '" stroke="' + LINE + '" stroke-width="2"/>' +
        '</g>' +

        /* đầu to kiểu chibi */
        '<g data-part="head" style="transform-origin:50px 60px">' +
          '<ellipse cx="24" cy="42" rx="4.6" ry="5.4" fill="' + SKIN_SHADE + '" ' +
            'stroke="' + LINE + '" stroke-width="2"/>' +
          '<ellipse cx="76" cy="42" rx="4.6" ry="5.4" fill="' + SKIN + '" ' +
            'stroke="' + LINE + '" stroke-width="2"/>' +
          '<ellipse cx="50" cy="36" rx="25" ry="24" fill="' + SKIN + '" ' +
            'stroke="' + LINE + '" stroke-width="2.4"/>' +
          hairSvg(c, pal) +
          '<ellipse cx="28" cy="48" rx="6" ry="3.6" fill="' + BLUSH + '" opacity=".6"/>' +
          '<ellipse cx="72" cy="48" rx="6" ry="3.6" fill="' + BLUSH + '" opacity=".6"/>' +
          eyeSvg(36, c.eye) +
          eyeSvg(64, c.eye) +
          '<path d="M46.5 51.5 q3.5 4 7 0" stroke="' + LASH + '" stroke-width="2.4" fill="none" ' +
            'stroke-linecap="round"/>' +
          extraSvg(c, pal) +
        '</g>' +
      '</g></svg>';
  }

  function animalSvg(id, variant, cls) {
    return kidSvg(get(id), paletteFor(id, variant), cls);
  }

  global.BattleAnimals = {
    list: CHARACTERS,
    get: get,
    paletteFor: paletteFor,
    assignColors: assignColors,
    animalSvg: animalSvg
  };
})(window);
