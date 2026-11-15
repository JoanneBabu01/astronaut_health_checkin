"""The HTML for the Calm Break page: catch falling stars and follow a breathing circle.

A stress buster, not a challenge: no timer, no score to beat, no game over.
Plain Python that returns one self-contained HTML string (no internet needed).
pages/6_Calm_Break.py shows it with st.components.v1.html.

For education and demonstration, not medical advice.
"""
import json

# Soft space colours. Change these to match THEME in core/charts.py.
DEFAULT_PALETTE = {
    "text": "#dfe6ff",
    "bg_top": "#0b1026",
    "bg_bottom": "#1c1650",
    "star": "#ffe9a8",
    "star_alt": "#cdb8ff",
    "star_soft": "#9fdcff",
    "ring_a": "#7fd4ff",
    "ring_b": "#8a6cff",
}

_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  html, body { margin: 0; height: 100%; background: transparent; color: __TEXT__;
               font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  .wrap { height: 100vh; box-sizing: border-box; display: flex; flex-direction: column;
          padding: 8px 10px 12px; background: rgba(11, 16, 38, 0.78); border-radius: 18px; }
  .row { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
         padding: 6px 4px 10px; font-size: 14px; opacity: .92; }
  #sky { display: block; width: 100%; flex: 1 1 0; min-height: 200px; border-radius: 16px;
         background: linear-gradient(180deg, __BG_TOP__, __BG_BOTTOM__);
         touch-action: manipulation; }
  .breath { display: flex; flex-direction: column; align-items: center; margin-top: 10px; }
  #ringSpace { height: 184px; display: flex; align-items: center; justify-content: center; }
  #ring { width: 100px; height: 100px; border-radius: 50%;
          background: radial-gradient(circle at 35% 30%, __RING_A__, __RING_B__);
          box-shadow: 0 0 28px __RING_B__; will-change: transform; }
  #cue { font-size: 20px; margin-top: 6px; min-height: 28px; }
  .hint { font-size: 13px; opacity: .75; margin-top: 4px; }
  #fs { background: rgba(255,255,255,.12); color: inherit; border: 1px solid rgba(255,255,255,.3);
        border-radius: 999px; padding: 4px 14px; font-size: 13px; cursor: pointer; }
  #fs:hover { background: rgba(255,255,255,.22); }
  .wrap:fullscreen { border-radius: 0; padding: 12px 18px 16px;
                     background: linear-gradient(180deg, __BG_TOP__, __BG_BOTTOM__); }
</style>
</head>
<body>
<div class="wrap">
  <div class="row">
    <span id="count" aria-live="polite">Stars caught: 0</span>
    <span>Click a star when you like. No timer, no score to beat.</span>
    <button id="fs" type="button">Full screen</button>
  </div>
  <canvas id="sky" role="img" aria-label="Soft stars falling slowly. Click a star to catch it."></canvas>
  <div class="breath">
    <div id="ringSpace"><div id="ring"></div></div>
    <div id="cue" aria-live="off">Breathe in</div>
    <div class="hint">Breathe in for 4 seconds, out for 6.</div>
  </div>
</div>
<script>
(function () {
  "use strict";
  var COLORS = __STAR_COLORS__;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SPEED = reduce ? 0.5 : 1;
  var canvas = document.getElementById("sky");
  var ctx = canvas.getContext("2d");
  var countEl = document.getElementById("count");
  var ring = document.getElementById("ring");
  var cue = document.getElementById("cue");
  var W = 0, H = 340, caught = 0;
  var stars = [], sparks = [], dust = [];

  function rand(a, b) { return a + Math.random() * (b - a); }

  function resize() {
    var dpr = window.devicePixelRatio || 1;
    W = canvas.clientWidth || 600;
    H = canvas.clientHeight || 340;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    dust = [];
    for (var i = 0; i < 70; i++) {
      dust.push({ x: rand(0, W), y: rand(0, H), r: rand(0.5, 1.5), p: rand(0, 6.28) });
    }
  }

  function newStar(fromTop) {
    return {
      x: rand(30, Math.max(60, W - 30)),
      y: fromTop ? rand(-40, -10) : rand(20, Math.max(40, H - 60)),
      r: rand(11, 18),
      vy: rand(14, 30),
      sway: rand(0.4, 1.2),
      phase: rand(0, 6.28),
      rot: rand(0, 6.28),
      color: COLORS[Math.floor(Math.random() * COLORS.length)]
    };
  }

  function fadeAt(y) {
    var edge = 60;
    return Math.max(0, Math.min(1, (y + 20) / edge, (H - y) / edge));
  }

  function drawStar(s, t) {
    var glow = (0.75 + 0.25 * Math.sin(t * 1.5 + s.phase)) * fadeAt(s.y);
    ctx.save();
    ctx.translate(s.x, s.y);
    ctx.rotate(s.rot + (reduce ? 0 : Math.sin(t * 0.6 + s.phase) * 0.15));
    ctx.globalAlpha = glow;
    ctx.fillStyle = s.color;
    ctx.shadowColor = s.color;
    ctx.shadowBlur = 14;
    ctx.beginPath();
    for (var i = 0; i < 10; i++) {
      var radius = i % 2 === 0 ? s.r : s.r * 0.45;
      var a = (Math.PI / 5) * i - Math.PI / 2;
      ctx.lineTo(Math.cos(a) * radius, Math.sin(a) * radius);
    }
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function catchAt(x, y) {
    var best = -1, bestD = 1e9;
    for (var i = 0; i < stars.length; i++) {
      var d = Math.hypot(stars[i].x - x, stars[i].y - y);
      if (d < stars[i].r + 14 && d < bestD) { best = i; bestD = d; }
    }
    return best;
  }

  canvas.addEventListener("pointerdown", function (e) {
    var box = canvas.getBoundingClientRect();
    var x = (e.clientX - box.left) * (W / box.width);
    var y = (e.clientY - box.top) * (H / box.height);
    var i = catchAt(x, y);
    if (i < 0) return;
    var s = stars[i];
    if (!reduce) {
      for (var k = 0; k < 8; k++) {
        var ang = (Math.PI * 2 * k) / 8;
        sparks.push({ x: s.x, y: s.y, vx: Math.cos(ang) * 40, vy: Math.sin(ang) * 40, life: 0.7, color: s.color });
      }
    }
    stars[i] = newStar(true);
    caught += 1;
    countEl.textContent = "Stars caught: " + caught;
  });

  canvas.addEventListener("pointermove", function (e) {
    var box = canvas.getBoundingClientRect();
    var i = catchAt((e.clientX - box.left) * (W / box.width), (e.clientY - box.top) * (H / box.height));
    canvas.style.cursor = i >= 0 ? "pointer" : "default";
  });

  function breathe(t) {
    var cycle = t % 10;
    var scale, text;
    if (cycle < 4) {
      var p = cycle / 4;
      scale = 1 + 0.6 * (0.5 - 0.5 * Math.cos(Math.PI * p));
      text = "Breathe in \\u00b7 " + Math.ceil(4 - cycle);
    } else {
      var q = (cycle - 4) / 6;
      scale = 1.6 - 0.6 * (0.5 - 0.5 * Math.cos(Math.PI * q));
      text = "Breathe out \\u00b7 " + Math.ceil(10 - cycle);
    }
    if (reduce) {
      ring.style.transform = "none";
      ring.style.opacity = String(0.55 + 0.45 * (scale - 1) / 0.6);
    } else {
      ring.style.transform = "scale(" + scale.toFixed(3) + ")";
    }
    if (cue.textContent !== text) cue.textContent = text;
  }

  var last = null, start = null;
  function frame(now) {
    if (start === null) { start = now; last = now; }
    var dt = Math.min(0.05, (now - last) / 1000);
    var t = (now - start) / 1000;
    last = now;

    ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < dust.length; i++) {
      var d = dust[i];
      ctx.globalAlpha = reduce ? 0.55 : 0.35 + 0.3 * Math.sin(t * 0.8 + d.p);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(d.x, d.y, d.r, d.r);
    }
    ctx.globalAlpha = 1;

    for (var j = 0; j < stars.length; j++) {
      var s = stars[j];
      s.y += s.vy * SPEED * dt;
      s.x += Math.sin(t * s.sway + s.phase) * 8 * SPEED * dt;
      if (s.y > H - 4) stars[j] = newStar(true);
      drawStar(stars[j], t);
    }

    for (var k = sparks.length - 1; k >= 0; k--) {
      var p = sparks[k];
      p.life -= dt;
      if (p.life <= 0) { sparks.splice(k, 1); continue; }
      p.x += p.vx * dt; p.y += p.vy * dt;
      ctx.globalAlpha = Math.max(0, p.life / 0.7);
      ctx.fillStyle = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, 2.5, 0, 6.2832); ctx.fill();
    }
    ctx.globalAlpha = 1;

    breathe(t);
    window.requestAnimationFrame(frame);
  }

  var fsButton = document.getElementById("fs");
  var wrap = document.querySelector(".wrap");
  if (!(document.fullscreenEnabled && wrap.requestFullscreen)) {
    fsButton.style.display = "none";
  }
  fsButton.addEventListener("click", function () {
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else { wrap.requestFullscreen(); }
  });
  document.addEventListener("fullscreenchange", function () {
    fsButton.textContent = document.fullscreenElement ? "Exit full screen" : "Full screen";
    setTimeout(resize, 50);
  });
  window.addEventListener("resize", resize);
  resize();
  for (var n = 0; n < 12; n++) stars.push(newStar(false));
  window.__calm = { stars: stars, caught: function () { return caught; } };
  window.requestAnimationFrame(frame);
})();
</script>
</body>
</html>
"""


def calm_break_html(palette=None):
    """Return the full HTML page as a string. palette overrides DEFAULT_PALETTE keys."""
    colors = {**DEFAULT_PALETTE, **(palette or {})}
    html = _TEMPLATE.replace(
        "__STAR_COLORS__",
        json.dumps([colors["star"], colors["star_alt"], colors["star_soft"]]),
    )
    for key in ("text", "bg_top", "bg_bottom", "ring_a", "ring_b"):
        html = html.replace(f"__{key.upper()}__", colors[key])
    return html
