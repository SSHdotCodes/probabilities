"use strict";

const COLORS = ["#8b7bff", "#46e6d0", "#6ff0a8", "#ffcf5c", "#ff6ea9", "#7aa2ff"];
const $ = (s, r = document) => r.querySelector(s);

let STATE = null;

/* ---------- helpers ---------- */
const pct = (x) => `${Math.round((x || 0) * 100)}%`;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function ago(iso) {
  if (!iso) return "—";
  const d = (Date.now() - new Date(iso).getTime()) / 1000;
  if (d < 60) return "just now";
  if (d < 3600) return `${Math.floor(d / 60)}m ago`;
  if (d < 86400) return `${Math.floor(d / 3600)}h ago`;
  return `${Math.floor(d / 86400)}d ago`;
}
function timeShort(iso) {
  if (!iso) return "";
  const dt = new Date(iso);
  return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* ---------- render ---------- */
function renderChips(meta) {
  const el = $("#meta-chips");
  el.innerHTML = [
    `<span class="chip">agent · <b>${esc(meta.model)}</b></span>`,
    `<span class="chip">reasoning · <b>${esc(meta.reasoning_effort)}</b></span>`,
    `<span class="chip">data · <b>Polymarket</b> · <b>X/web</b> · <b>ai-tracker</b></span>`,
    `<span class="chip">refresh · <b>${meta.refresh_hours}h</b></span>`,
  ].join("");
}

function renderRecord(s) {
  const acc = s.accuracy == null ? "—" : pct(s.accuracy);
  $("#record").innerHTML = `
    <div class="stat"><div class="stat__num ${s.accuracy != null ? "good" : ""}">${acc}</div><div class="stat__lbl">hit rate</div></div>
    <div class="stat"><div class="stat__num">${s.hits}/${s.resolved}</div><div class="stat__lbl">correct / resolved</div></div>
    <div class="stat"><div class="stat__num">±${s.tolerance_days}d</div><div class="stat__lbl">hit window</div></div>
  `;
}

function statusPill(m) {
  if (m.status === "released") return `<span class="pill pill--rel">RELEASED</span>`;
  if (m.prediction && m.prediction.released) return `<span class="pill pill--cand">LIKELY OUT</span>`;
  if (m.release_candidate) return `<span class="pill pill--cand">POSSIBLE</span>`;
  return `<span class="pill pill--up">UPCOMING</span>`;
}

function stackedBar(windows) {
  if (!windows || !windows.length) return "";
  const segs = windows.map((w, i) => `<div class="pbar__seg" style="width:${(w.prob * 100).toFixed(1)}%;background:${COLORS[i % COLORS.length]}"></div>`).join("");
  const legend = windows.map((w, i) => `<span style="--c:${COLORS[i % COLORS.length]}">${esc(w.label)} ${pct(w.prob)}</span>`).join("");
  return `<div class="pbar__wrap"><div class="pbar">${segs}</div><div class="pbar__legend">${legend}</div></div>`;
}

function card(m) {
  const p = m.prediction;
  const glow = m.status === "released" ? "#6ff0a822" : "#8b7bff22";
  let body;
  if (m.status === "released") {
    const hit = p && p.hit;
    const badge = p && p.hit != null
      ? `<span class="rel-badge ${hit ? "hit" : "miss"}">${hit ? "✅ called it" : `✗ off by ${Math.abs(p.error_days)}d`}</span>`
      : "";
    body = `<div class="likely"><div><div class="likely__lbl">Released</div><div class="likely__date">${esc(m.released_at || "—")}</div></div>${badge}</div>
            ${p ? `<div class="likely__lbl" style="margin-top:8px">Our estimate was</div><div class="likely__date" style="font-size:14px;color:var(--muted)">${esc(p.point_estimate_label || p.point_estimate || "—")}</div>` : ""}`;
  } else if (p && p.windows && p.windows.length) {
    body = `
      <div class="likely">
        <div><div class="likely__lbl">${p.released ? "agent says shipped" : "Most likely"}</div><div class="likely__date">${esc(p.point_estimate_label || p.point_estimate || "—")}</div></div>
        <div><div class="likely__lbl">confidence</div><div class="likely__conf">${pct(p.confidence)}</div></div>
      </div>
      ${stackedBar(p.windows)}`;
  } else {
    body = `<div class="card__pending">◌ estimating… (agent is gathering signals)</div>`;
  }
  return `
    <article class="card" style="--glow:${glow}" tabindex="0" data-id="${esc(m.id)}">
      <div class="card__top"><span class="tag">${esc(m.lab)}</span>${statusPill(m)}</div>
      <h3 class="card__name">${esc(m.name)}</h3>
      <p class="card__blurb">${esc(m.blurb)}</p>
      ${body}
      <div class="card__hint">click for full forecast →</div>
    </article>`;
}

function renderGrid(models) {
  $("#grid").innerHTML = models.map(card).join("") || `<div class="loading">No models tracked.</div>`;
}

function renderLog(log, s) {
  $("#log").innerHTML = (log || []).map((e) => `<li><time>${timeShort(e.ts)}</time>${esc(e.msg)}</li>`).join("")
    || `<li>No activity yet.</li>`;
  $("#foot").textContent =
    `last forecast refresh ${ago(s.last_predict_refresh)} · last release check ${ago(s.last_release_check)}`;
}

/* ---------- modal ---------- */
function distRows(windows) {
  return windows.map((w, i) => `
    <div class="dist__row">
      <div class="dist__lbl">${esc(w.label)}</div>
      <div class="dist__track"><div class="dist__fill" style="width:${(w.prob * 100).toFixed(1)}%;background:${COLORS[i % COLORS.length]}"></div></div>
      <div class="dist__pct">${pct(w.prob)}</div>
    </div>`).join("");
}

function openModal(m) {
  const p = m.prediction;
  const ev = (p && p.evidence) || {};
  let html = `
    <div class="m-head"><h2 class="m-title" id="m-title">${esc(m.name)}</h2><span class="tag">${esc(m.lab)}</span>${statusPill(m)}</div>
    <p class="m-blurb">${esc(m.blurb)}</p>`;

  if (m.status === "released") {
    const hit = p && p.hit;
    const line = p && p.hit != null
      ? (hit ? `We called it — within ±${STATE.scores.tolerance_days} days.` : `We were off by ${p.error_days > 0 ? "+" : ""}${p.error_days} days.`)
      : `No active estimate was on record at release.`;
    const evr = m.release_evidence || {};
    html += `<div class="m-rel ${hit === false ? "miss" : ""}">
      <b>Released ${esc(m.released_at)}.</b> ${esc(line)}
      ${p && p.point_estimate ? ` Our estimate: <b>${esc(p.point_estimate_label || p.point_estimate)}</b>.` : ""}
      ${evr.source ? `<br><span style="color:var(--dim)">detected via ai-tracker — ${esc(evr.source)}${evr.url ? ` · <a href="${esc(evr.url)}" target="_blank" rel="noopener">source ↗</a>` : ""}</span>` : ""}
    </div>`;
  }

  if (m.release_candidate && m.status !== "released") {
    const c = m.release_candidate;
    html += `<div class="m-rel"><b>Possible release signal.</b> ai-tracker text mentions this model${c.source ? ` (${esc(c.source)})` : ""} — awaiting a catalog confirmation before grading.${c.url ? ` <a href="${esc(c.url)}" target="_blank" rel="noopener">source ↗</a>` : ""}</div>`;
  }

  if (p && p.released && m.status !== "released") {
    html += `<div class="m-rel"><b>The agent believes this model has already shipped${p.point_estimate ? ` (~${esc(p.point_estimate_label || p.point_estimate)})` : ""}.</b> It stays "likely out" and ungraded until <a href="https://ai-tracker.ssh.codes" target="_blank" rel="noopener">ai-tracker</a> confirms it in a first-party model catalog.</div>`;
  }

  if (p && p.windows && p.windows.length) {
    html += `
      <div class="m-est">
        <div><div class="m-est__lbl">Point estimate</div><div class="m-est__big">${esc(p.point_estimate_label || p.point_estimate || "—")}</div></div>
        <div class="ring" style="--p:${Math.round((p.confidence || 0) * 100)}"><span>${pct(p.confidence)}</span></div>
        <div><div class="m-est__lbl">agent<br>confidence</div></div>
      </div>
      <div class="m-sec"><h3>Release-date distribution</h3><div class="dist">${distRows(p.windows)}</div></div>`;

    if (p.summary) html += `<div class="m-sec"><h3>Agent rationale</h3><p class="m-blurb" style="margin:0">${esc(p.summary)}</p></div>`;
    if (p.key_signals && p.key_signals.length)
      html += `<div class="m-sec"><h3>Key signals</h3><ul class="signals">${p.key_signals.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>`;

    // Polymarket
    html += `<div class="m-sec"><h3>Polymarket odds</h3><p class="src-note">${esc(p.polymarket_note || ev.polymarket_note || "")}</p><div class="src-list">`;
    (ev.polymarket || []).forEach((mk) => {
      const odds = (mk.odds || []).map((o) => `${esc(o.outcome)} ${o.prob != null ? pct(o.prob) : "?"}`).join(" · ");
      html += `<div><span class="q">${esc(mk.question)}</span><br>${esc(odds)}</div>`;
    });
    html += `</div></div>`;

    // X / web
    if ((ev.x_web || []).length) {
      html += `<div class="m-sec"><h3>X / web leaks &amp; posts</h3><p class="src-note">${esc(ev.x_web_note || "")}</p><div class="src-list">`;
      ev.x_web.slice(0, 6).forEach((r) => {
        html += `<a href="${esc(r.href)}" target="_blank" rel="noopener"><span class="q">${esc(r.title)}</span><br>${esc((r.body || "").slice(0, 160))}</a>`;
      });
      html += `</div></div>`;
    }

    // Cadence
    if ((ev.cadence || []).length) {
      html += `<div class="m-sec"><h3>Recent ${esc(m.lab)} cadence (ai-tracker)</h3><div class="src-list">`;
      ev.cadence.forEach((r) => { html += `<div>${esc(r.model)} — <span style="color:var(--dim)">${esc(r.detectedAt)}</span></div>`; });
      html += `</div></div>`;
    }

    html += `<div class="m-foot">
      <span>model · ${esc(p.model_used || STATE.meta.model)}</span>
      <span>reasoning · ${esc(p.reasoning_effort || STATE.meta.reasoning_effort)}</span>
      <span>updated ${ago(p.generated_at)}</span>
    </div>`;
  } else if (m.status !== "released") {
    html += `<div class="card__pending" style="padding:20px 0">◌ The agent hasn't produced a forecast yet — check back shortly.</div>`;
  }

  $("#modal-body").innerHTML = html;
  $("#modal").hidden = false;
  document.body.style.overflow = "hidden";
}

function closeModal() {
  $("#modal").hidden = true;
  document.body.style.overflow = "";
}

document.addEventListener("click", (e) => {
  const c = e.target.closest(".card");
  if (c) {
    const m = STATE?.models.find((x) => x.id === c.dataset.id);
    if (m) openModal(m);
    return;
  }
  if (e.target.closest("[data-close]")) closeModal();
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });
document.addEventListener("keypress", (e) => {
  if ((e.key === "Enter" || e.key === " ") && document.activeElement?.classList.contains("card")) {
    e.preventDefault();
    const m = STATE?.models.find((x) => x.id === document.activeElement.dataset.id);
    if (m) openModal(m);
  }
});

/* ---------- data ---------- */
async function tick() {
  try {
    const r = await fetch("/api/state", { cache: "no-store" });
    STATE = await r.json();
    renderChips(STATE.meta);
    renderRecord(STATE.scores);
    renderGrid(STATE.models);
    renderLog(STATE.log, STATE);
  } catch (e) {
    // keep last good render
  }
}
tick();
setInterval(tick, 30000);

/* ---------- ambient probability field ---------- */
(function field() {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cv = $("#field");
  const ctx = cv.getContext("2d");
  let w, h, pts;
  function resize() {
    w = cv.width = innerWidth * devicePixelRatio;
    h = cv.height = innerHeight * devicePixelRatio;
    cv.style.width = innerWidth + "px"; cv.style.height = innerHeight + "px";
    const n = Math.min(70, Math.floor(innerWidth / 22));
    pts = Array.from({ length: n }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.18 * devicePixelRatio,
      vy: (Math.random() - 0.5) * 0.18 * devicePixelRatio,
      r: (Math.random() * 1.6 + 0.5) * devicePixelRatio,
    }));
  }
  resize(); addEventListener("resize", resize);
  function draw() {
    ctx.clearRect(0, 0, w, h);
    for (const p of pts) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 7);
      ctx.fillStyle = "rgba(139,123,255,.5)"; ctx.fill();
    }
    for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
      const a = pts[i], b = pts[j], dx = a.x - b.x, dy = a.y - b.y, d = Math.hypot(dx, dy);
      if (d < 120 * devicePixelRatio) {
        ctx.strokeStyle = `rgba(70,230,208,${0.12 * (1 - d / (120 * devicePixelRatio))})`;
        ctx.lineWidth = devicePixelRatio; ctx.beginPath();
        ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();
