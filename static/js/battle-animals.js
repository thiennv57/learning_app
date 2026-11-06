/* ==========================================================================
   NHÂN VẬT — học sinh, vẽ phẳng kiểu hoạt hình Việt Nam

   Mười bạn học sinh để người chơi chọn ở màn nhập tên. Tất cả dùng chung một
   dáng người và một bộ đồng phục (áo trắng, khăn quàng đỏ, quần/váy xanh
   than, dép quai hậu), chỉ khác kiểu tóc, phụ kiện và tông màu — nhờ vậy
   cả lớp trông cùng một bộ và không ai to nhỏ hơn ai.

   Hai người chọn trùng nhân vật vẫn phân biệt được: assignColors() phát cho
   mỗi người một tông phụ kiện khác nhau.
   ========================================================================== */

(function (global) {
  'use strict';

  var SKIN = '#F7C9A0';
  var SKIN_SHADE = '#E2A97E';
  var SHIRT = '#FFFFFF';
  var SHIRT_SHADE = '#E4E9F0';
  var NAVY = '#2B4B8C';
  var NAVY_DARK = '#1E3668';
  var SCARF = '#E53935';
  var SANDAL = '#4FA8E8';
  var LINE = '#2E2A37';

  /* kind: 'boy' | 'girl'
     hair: kiểu tóc; hairCol: màu tóc; extra: phụ kiện thêm               */
  var CHARACTERS = [
    { id: 'boy_short', name: 'Nam tóc ngắn', kind: 'boy',  hair: 'short',    hairCol: '#2B2B33', hue: 210 },
    { id: 'boy_glass', name: 'Nam đeo kính', kind: 'boy',  hair: 'short',    hairCol: '#3B2A1E', hue: 150, extra: 'glasses' },
    { id: 'boy_cap',   name: 'Nam đội mũ',   kind: 'boy',  hair: 'short',    hairCol: '#2B2B33', hue: 20,  extra: 'cap' },
    { id: 'boy_spiky', name: 'Nam tóc dựng', kind: 'boy',  hair: 'spiky',    hairCol: '#1F1F27', hue: 275 },
    { id: 'girl_tail', name: 'Nữ tóc đuôi',  kind: 'girl', hair: 'ponytail', hairCol: '#2B2B33', hue: 340 },
    { id: 'girl_two',  name: 'Nữ hai bím',   kind: 'girl', hair: 'twintail', hairCol: '#3B2A1E', hue: 300 },
    { id: 'girl_bob',  name: 'Nữ tóc ngang', kind: 'girl', hair: 'bob',      hairCol: '#2B2B33', hue: 180 },
    { id: 'girl_bow',  name: 'Nữ nơ cài',    kind: 'girl', hair: 'bob',      hairCol: '#4A2E1C', hue: 45,  extra: 'bow' },
    { id: 'boy_curly', name: 'Nam tóc xoăn', kind: 'boy',  hair: 'curly',    hairCol: '#33261B', hue: 95 },
    { id: 'girl_long', name: 'Nữ tóc dài',   kind: 'girl', hair: 'long',     hairCol: '#2B2B33', hue: 15 }
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
      accent: 'hsl(' + h + ',72%,58%)',
      accentDark: 'hsl(' + h + ',62%,42%)',
      fur: 'hsl(' + h + ',55%,55%)',
      furDark: 'hsl(' + h + ',50%,38%)',
      furPale: 'hsl(' + h + ',62%,86%)'
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

  /* ---------------------------- Bản vẽ ---------------------------------- */

  function hairSvg(c, pal) {
    switch (c.hair) {
      case 'spiky':
        return '<path d="M33 30 q0 -19 17 -19 q17 0 17 19 q-4 -7 -8 -2 q-4 -8 -9 -2 q-5 -6 -9 2 q-4 -5 -8 2 Z" fill="' + c.hairCol + '"/>';
      case 'ponytail':
        return '<path d="M30 34 q-9 2 -11 12 q-1 7 5 9 q3 -11 8 -14 Z" fill="' + c.hairCol + '"/>' +
               '<path d="M33 30 q0 -19 17 -19 q17 0 17 19 q-6 -9 -17 -9 q-11 0 -17 9 Z" fill="' + c.hairCol + '"/>' +
               '<circle cx="31" cy="36" r="3.4" fill="' + pal.accent + '"/>';
      case 'twintail':
        return '<ellipse cx="29" cy="40" rx="5" ry="9" fill="' + c.hairCol + '"/>' +
               '<ellipse cx="71" cy="40" rx="5" ry="9" fill="' + c.hairCol + '"/>' +
               '<path d="M33 30 q0 -19 17 -19 q17 0 17 19 q-6 -9 -17 -9 q-11 0 -17 9 Z" fill="' + c.hairCol + '"/>' +
               '<circle cx="29" cy="32" r="3" fill="' + pal.accent + '"/>' +
               '<circle cx="71" cy="32" r="3" fill="' + pal.accent + '"/>';
      case 'curly':
        return '<g fill="' + c.hairCol + '">' +
          '<circle cx="36" cy="22" r="9"/><circle cx="50" cy="14" r="10"/><circle cx="64" cy="22" r="9"/>' +
          '<circle cx="44" cy="16" r="8"/><circle cx="57" cy="16" r="8"/>' +
          '<path d="M33 30 q0 -14 17 -14 q17 0 17 14 q-6 -8 -17 -8 q-11 0 -17 8 Z"/></g>';
      case 'long':
        return '<path d="M30 30 q0 -21 20 -21 q20 0 20 21 l2 28 q-6 4 -9 -2 l-2 -20 q-11 5 -22 0 l-2 20 q-3 6 -9 2 Z" fill="' + c.hairCol + '"/>' +
               '<circle cx="36" cy="18" r="3.2" fill="' + pal.accent + '"/>';
      case 'bob':
        return '<path d="M31 32 q0 -21 19 -21 q19 0 19 21 l0 10 q-5 -3 -6 -10 q-7 4 -13 4 q-6 0 -13 -4 q-1 7 -6 10 Z" fill="' + c.hairCol + '"/>';
      default: /* short */
        return '<path d="M33 30 q0 -19 17 -19 q17 0 17 19 q-6 -10 -17 -10 q-11 0 -17 10 Z" fill="' + c.hairCol + '"/>';
    }
  }

  function extraSvg(c, pal) {
    if (c.extra === 'glasses') {
      return '<g fill="none" stroke="' + LINE + '" stroke-width="1.6">' +
             '<circle cx="43" cy="31" r="5.2"/><circle cx="57" cy="31" r="5.2"/>' +
             '<path d="M48.2 31 h3.6"/></g>';
    }
    if (c.extra === 'cap') {
      return '<path d="M31 24 q1 -14 19 -14 q18 0 19 14 Z" fill="' + pal.accent + '"/>' +
             '<path d="M67 24 q10 0 13 4 l-15 2 Z" fill="' + pal.accentDark + '"/>';
    }
    if (c.extra === 'bow') {
      return '<path d="M64 17 l7 -4 l0 8 Z" fill="' + pal.accent + '"/>' +
             '<path d="M64 17 l7 4 l0 -8 Z" fill="' + pal.accentDark + '"/>' +
             '<circle cx="64" cy="17" r="2.4" fill="' + pal.accent + '"/>';
    }
    return '';
  }

  /* Học sinh: áo trắng, khăn quàng đỏ, quần/váy xanh than, dép xanh.
     Dáng đang chạy, mặt hướng về bên phải.                               */
  function kidSvg(c, pal, cls) {
    var bottom = (c.kind === 'girl')
      ? '<path d="M38 66 l24 0 l5 14 l-34 0 Z" fill="' + NAVY + '"/>' +
        '<path d="M38 66 l24 0 l1.6 4.6 l-27.2 0 Z" fill="' + NAVY_DARK + '"/>'
      : '<path d="M39 66 h22 l1 12 h-9 l-3 -7 l-3 7 h-9 Z" fill="' + NAVY + '"/>';

    return '<svg class="' + (cls || 'char-body') + '" viewBox="0 0 100 100" role="img" aria-label="' + c.name + '">' +
      '<g data-part="body">' +
        '<g data-part="leg-far">' +
          '<path d="M44 78 L35 90" stroke="' + SKIN_SHADE + '" stroke-width="7" stroke-linecap="round" fill="none"/>' +
          '<path d="M29 88 h12 a3 3 0 0 1 0 6 h-12 a3 3 0 0 1 0 -6 Z" fill="' + pal.accentDark + '"/>' +
        '</g>' +
        '<path d="M44 54 L33 62" stroke="' + SKIN_SHADE + '" stroke-width="6.4" stroke-linecap="round" fill="none"/>' +
        '<path d="M38 46 q12 -4 24 0 l2 21 q-14 4 -28 0 Z" fill="' + SHIRT + '"/>' +
        '<path d="M38 46 q12 -4 24 0 l.6 6 q-12 -3 -25 0 Z" fill="' + SHIRT_SHADE + '"/>' +
        bottom +
        '<path d="M43 45 q7 5 14 0 l-1.5 5 q-5.5 3 -11 0 Z" fill="' + SCARF + '"/>' +
        '<path d="M50 50 l4 9 l-7 0 Z" fill="' + SCARF + '"/>' +
        '<g data-part="leg-near">' +
          '<path d="M55 78 L65 88" stroke="' + SKIN + '" stroke-width="7.4" stroke-linecap="round" fill="none"/>' +
          '<path d="M60 86 h13 a3.2 3.2 0 0 1 0 6.4 h-13 a3.2 3.2 0 0 1 0 -6.4 Z" fill="' + SANDAL + '"/>' +
        '</g>' +
        '<g data-part="head" style="transform-origin:50px 46px">' +
          '<circle cx="50" cy="31" r="18" fill="' + SKIN + '"/>' +
          hairSvg(c, pal) +
          '<ellipse cx="38" cy="36" rx="4" ry="2.6" fill="#FF9BB0" opacity=".55"/>' +
          '<ellipse cx="62" cy="36" rx="4" ry="2.6" fill="#FF9BB0" opacity=".55"/>' +
          '<path d="M40 30 q3 -3.4 6 0" stroke="' + LINE + '" stroke-width="2" fill="none" stroke-linecap="round"/>' +
          '<path d="M54 30 q3 -3.4 6 0" stroke="' + LINE + '" stroke-width="2" fill="none" stroke-linecap="round"/>' +
          '<path d="M46 37 q4 5 8 0 Z" fill="' + LINE + '"/>' +
          extraSvg(c, pal) +
        '</g>' +
        '<path d="M58 52 L70 44" stroke="' + SKIN + '" stroke-width="6.8" stroke-linecap="round" fill="none"/>' +
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
