/* ==========================================================================
   Sân khấu rút gọn cho MÀN NGƯỜI CHƠI.

   Dựng đúng khung cảnh của màn quản trị — toàn bộ người chơi đứng trên bục
   pha lê, bảng xếp hạng bên phải — nhưng không có hoạt ảnh đòn đánh, vì dữ
   liệu gửi cho người chơi đã giấu danh tính người ra đòn.
   ========================================================================== */

(function (global) {
  'use strict';

  var charEls = {};
  var rosterSig = '';

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function fmt(x) { return Number.isInteger(x) ? x : Math.round(x * 10) / 10; }
  function hpCls(h) { return h > 60 ? 'high' : h > 30 ? 'mid' : 'low'; }

  var lastCorrect = {};

  function mountScene() {
    var sc = document.getElementById('pa-scene');
    if (sc && !sc.dataset.drawn) {
      sc.innerHTML = BattleHero.sceneMarkup() +
        '<div class="trophy">' + BattleHero.trophySvg() + '<span>ĐÍCH</span></div>';
      sc.dataset.drawn = '1';
    }
  }

  /* Mọi người chạy trên cùng mặt đường, xếp thành nhiều hàng cho đỡ che nhau */
  function buildRoster(players, teams, myPid) {
    var layer = document.getElementById('pa-players');
    if (!layer) return;
    layer.innerHTML = '';
    charEls = {};
    lastCorrect = {};
    if (global.BattleAnim) BattleAnim.reset();

    var n = players.length;
    var stage = layer.parentNode;
    BattleHero.watchStage(stage, function () {
      // tính lại cỡ nhân vật khi sân khấu đổi cỡ (xem BattleHero.fitScale)
      var els = stage.querySelectorAll('.char');
      if (!els.length) return;
      var sc = BattleHero.fitScale(stage, els.length);
      var ns = Math.max(0.9, Math.min(1.6, 1 / sc)).toFixed(3);
      Array.prototype.forEach.call(els, function (el) {
        el.dataset.sl = sc.toFixed(3);
        el.style.setProperty('--s', sc.toFixed(3));
        el.style.setProperty('--ns', ns);
      });
    });
    var layout = BattleHero.fitScale(stage, n);
    var looks = global.BattleAnimals ? BattleAnimals.assignColors(players) : {};

    var groups = (teams && teams.length)
      ? teams.slice().sort(function (a, b) { return a.team_id.localeCompare(b.team_id); })
          .map(function (t) { return { team: t, members: t.members }; })
      : [{ team: null, members: players }];

    var lane = 0;
    groups.forEach(function (g) {
      g.members.forEach(function (p, mi) {
        var top = BattleHero.rowY(lane, n);   // chỉ số toàn cục: hai đội sát điểm vẫn khác hàng
        var look = looks[p.player_id] || { animal: p.avatar, variant: 0 };
        var el = document.createElement('div');
        el.className = 'char' + (p.player_id === myPid ? ' is-me' : '');
        el.style.setProperty('--x', BattleHero.RUN_START);
        el.style.top = top + '%';
        el.dataset.sl = layout.toFixed(3);
        el.style.setProperty('--s', layout.toFixed(3));
        el.style.zIndex = Math.round(top * 10);
        lane++;
        // Sân nhỏ: chỉ hiện biểu tượng đội cho đỡ che nhau, tên đội nằm ở bảng xếp hạng
        var tag = g.team
          ? '<span class="char-teamdot" title="' + esc(g.team.name) + '" style="background:' +
            g.team.color + '">' + g.team.emoji + '</span>'
          : '';
        el.innerHTML =
          '<div class="char-shadow"></div>' +
          '<div class="char-nameplate">' + tag +
            '<span class="cn-name">' + (p.player_id === myPid ? '★ ' : '') + esc(p.name) + '</span>' +
            '<span class="cn-score" data-score>' + Math.round(p.hp) + '</span>' +
          '</div>' +
          '<div class="char-figure">' +
            BattleAnimals.animalSvg(look.animal, look.variant) + '</div>';
        layer.appendChild(el);
        charEls[p.player_id] = el;
        if (global.BattleAnim) BattleAnim.startRun(p.player_id, el, 0.9 + Math.random() * 0.25);
      });
    });
  }

  function syncPlayers(players, teams) {
    // Chế độ đồng đội: cả đội đứng chụm, vị trí do TỔNG ĐIỂM ĐỘI quyết định
    if (teams && teams.length) {
      var tBase = BattleHero.teamBaseX(teams);
      var tRange = BattleHero.scoreRange(teams.map(function (t) { return t.hp; }));
      var tTop = teams.slice().sort(function (a, b) { return b.hp - a.hp; })[0];
      teams.forEach(function (t) {
        var m = (t.members || []).length;
        (t.members || []).forEach(function (mem, mi) {
          var e = charEls[mem.player_id];
          if (!e) return;
          e.style.setProperty('--x', BattleHero.teamX(tBase[t.team_id], mi, m).toFixed(2));
          e.classList.toggle('leader', !!tTop && !tRange.flat && t.team_id === tTop.team_id);
        });
      });
    }
    var range = BattleHero.scoreRange(players.map(function (p) { return p.hp; }));
    var top = players.slice().sort(function (a, b) { return b.hp - a.hp; })[0];
    var theoDoi = !!(teams && teams.length);
    players.forEach(function (p) {
      var el = charEls[p.player_id];
      if (!el) return;
      var s = parseFloat(el.dataset.sl || '1');   // mọi nhân vật cùng một cỡ
      var cleared = p.correct_count || 0;
      if (!theoDoi) {
        el.style.setProperty('--x', BattleHero.runX(p.hp, range).toFixed(2));
        el.classList.toggle('leader', !!top && !range.flat && p.player_id === top.player_id);
      }
      el.style.setProperty('--s', s.toFixed(3));
      el.style.setProperty('--ns', Math.max(0.9, Math.min(1.6, 1 / s)).toFixed(3));
      var scEl = el.querySelector('[data-score]');
      if (scEl) scEl.textContent = Math.round(p.hp);
      var wasDead = el.classList.contains('dead');
      var isDead = p.hp <= 0 || p.alive === false;
      el.classList.toggle('dead', isDead);
      if (global.BattleAnim && isDead !== wasDead) {
        if (isDead) BattleAnim.freeze(p.player_id, el);
        else BattleAnim.startRun(p.player_id, el, 0.9 + Math.random() * 0.25);
      }
      el.classList.toggle('ghost', !!p.hide_active);
      // Vừa trả lời đúng → nhảy qua rào
      if (lastCorrect[p.player_id] != null && cleared > lastCorrect[p.player_id]) {
        if (global.BattleAnim && BattleAnim.available) {
          BattleAnim.jump(p.player_id, el);
        } else {
          el.classList.remove('jump'); void el.offsetWidth; el.classList.add('jump');
          setTimeout(function () { el.classList.remove('jump'); }, 950);
        }
      }
      lastCorrect[p.player_id] = cleared;
    });
  }

  function renderRank(players, myPid, teamOf) {
    var box = document.getElementById('pa-rank');
    if (!box) return;
    var medal = ['🥇', '🥈', '🥉'];
    var sorted = players.slice().sort(function (a, b) { return b.hp - a.hp; });
    box.innerHTML = sorted.map(function (p, i) {
      var h = p.hp, cls = hpCls(h);
      var col = cls === 'high' ? '#4FE0A6' : cls === 'mid' ? '#FFC46B' : '#FF6B8A';
      var w = Math.max(0, Math.min(100, h));
      var team = teamOf ? teamOf(p) : '';
      return '<div class="rank-row' + (i === 0 ? ' lead' : '') + (p.player_id === myPid ? ' me' : '') + '">' +
        '<div class="rank-pos">' + (medal[i] || (i + 1)) + '</div>' +
        '<div class="rank-main">' +
          '<div class="rank-name">' + (p.player_id === myPid ? '★ ' : '') + esc(p.name) +
            (team ? ' <span class="rank-team">' + esc(team) + '</span>' : '') + '</div>' +
          '<div class="rank-bar-bg"><div class="rank-bar ' + cls + '" style="width:' + w + '%"></div></div>' +
        '</div>' +
        '<div class="rank-hp" style="color:' + col + '">' + fmt(h) + '</div>' +
      '</div>';
    }).join('');
  }

  /* players: mảng người chơi công khai; opts: {myPid, teams, totalQuestions} */
  function render(players, opts) {
    players = players || [];
    opts = opts || {};
    if (!players.length) return;
    mountScene();
    var teams = opts.teams || null;
    var sig = (teams && teams.length
      ? teams.map(function (t) { return t.team_id + '#' + t.members.map(function (m) { return m.player_id; }).join(','); }).join('|')
      : players.map(function (p) { return p.player_id + ':' + p.name; }).join('|'));
    if (sig !== rosterSig) { rosterSig = sig; buildRoster(players, teams, opts.myPid); }
    syncPlayers(players, teams);
    renderRank(players, opts.myPid, teamOfFn(teams));
  }

  function teamOfFn(teams) {
    if (!teams || !teams.length) return null;
    var byPid = {};
    teams.forEach(function (t) {
      t.members.forEach(function (m) { byPid[m.player_id] = t.emoji; });
    });
    return function (p) { return byPid[p.player_id] || ''; };
  }

  global.BattleArena = { render: render };
})(window);
