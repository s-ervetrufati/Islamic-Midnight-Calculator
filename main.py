#!/usr/bin/env python3
"""
Mitternacht: find the middle of the night (Maghrib -> Fajr) or the middle of
the day (Fajr -> Maghrib). A local web app using only the Python standard library.

    python mitternacht.py              # opens your browser
    python mitternacht.py --port 9000 --no-browser

The server binds to 127.0.0.1 only, so nothing is reachable from your network.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, DAY, MAX_BODY = "127.0.0.1", 86400, 4096
NONCE = secrets.token_urlsafe(16)

# ───────────────────────── calculation ─────────────────────────

class InputError(ValueError):
    pass


# Accepts 5:30, 05.30, 530, 0530, 5h30, 17, 5 pm, 5:30 am, 05:30:15, 24:00 ...
TIME_RE = re.compile(
    r"^\s*(\d{1,2})(?:\s*[:.h]?\s*(\d{2}))?(?:\s*[:.]\s*(\d{2}))?\s*([ap]\.?\s*m\.?)?\s*$",
    re.I,
)


def parse_clock(raw: str, label: str) -> int:
    """Return seconds since 00:00, or raise InputError with a helpful message."""
    raw = (raw or "").strip()
    if not raw:
        raise InputError(f"Enter the {label} time, for example 05:30.")
    m = TIME_RE.match(raw)
    if not m:
        raise InputError(f"Can’t read “{raw[:16]}”. Try 05:30, 530 or 5:30 am.")
    h, mi, s = int(m[1]), int(m[2] or 0), int(m[3] or 0)
    if m[4]:  # 12-hour clock
        if not 1 <= h <= 12:
            raise InputError("With am/pm the hour must be between 1 and 12.")
        h = h % 12 + (12 if m[4][0].lower() == "p" else 0)
    elif (h, mi, s) == (24, 0, 0):
        h = 0
    if h > 23 or mi > 59 or s > 59:
        raise InputError("That isn’t a valid time. Hours go to 23, minutes to 59.")
    return h * 3600 + mi * 60 + s


def clock(sec: int) -> str:
    sec %= DAY
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def short(sec: int) -> str:
    return clock(sec)[:5] if sec % 60 == 0 else clock(sec)


def human(sec: int) -> str:
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    parts = [f"{h} h" if h else "", f"{m} min" if m or not (h or s) else "", f"{s} s" if s else ""]
    return " ".join(p for p in parts if p)


def calculate(fajr_raw: str, maghrib_raw: str, mode: str) -> dict:
    errors, secs, parsed = {}, {}, {}
    for key, raw, label in (("fajr", fajr_raw, "Fajr"), ("maghrib", maghrib_raw, "Maghrib")):
        try:
            secs[key] = parse_clock(raw, label)
            parsed[key] = short(secs[key])
        except InputError as exc:
            errors[key], parsed[key] = str(exc), None
    if errors:
        return {"ok": False, "errors": errors, "parsed": parsed}

    fajr, maghrib = secs["fajr"], secs["maghrib"]
    night = mode != "day"
    s, e = (maghrib, fajr) if night else (fajr, maghrib)
    if s == e:
        msg = "Same as the other time, so there is nothing to halve."
        return {"ok": False, "errors": {"fajr": msg, "maghrib": msg}, "parsed": parsed}
    if e < s:  # the span crosses midnight, e.g. Maghrib 18:00 -> Fajr 05:30
        e += DAY

    total = e - s
    mid = s + (total + 1) // 2                  # exact to the second, rounded half up
    nd = lambda v: " (next day)" if v >= DAY else ""
    hm = f"{total // 3600}h {total % 3600 // 60:02d}m"

    notes = []
    if fajr >= DAY // 2:
        notes.append("Fajr is normally before noon. Check am/pm.")
    if maghrib < DAY // 2:
        notes.append("Maghrib is normally in the afternoon or evening. Check am/pm.")
    if not 3 * 3600 <= total <= 21 * 3600:
        notes.append(f"A span of {human(total)} is unusual. Check the order of your times.")

    if night:
        third = e - (total + 1) // 3
        rows = [["Night length", human(total)], ["Half of the night", human((total + 1) // 2)],
                ["Last third begins", clock(third) + nd(third)]]
        extra = dict(caption="Middle of the night", sub=f"{hm} of night", labels={"s": "Maghrib", "e": "Fajr"})
    else:
        third = e
        rows = [["Day length", human(total)], ["Half of the day", human((total + 1) // 2)]]
        extra = dict(caption="Middle of the day", sub=f"{hm} Fajr to Maghrib", labels={"s": "Fajr", "e": "Maghrib"})

    return {"ok": True, "errors": {}, "parsed": parsed, "mid": clock(mid), "mid_next": mid >= DAY,
            "rows": rows, "notes": notes, "dial": {"s": s, "e": e, "m": mid, "t": third}, **extra}


# ───────────────────────── web page ─────────────────────────

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mitternacht</title>
<style>
:root{--lapis:#13265f;--deep:#0b1840;--moon:#eef1f7;--mist:#9db0dc;--line:#3a509a;--saffron:#ffb81c;--turq:#34d1bf;--coral:#ff7a6b;color-scheme:dark;
--sans:"Avenir Next","Segoe UI Variable","Segoe UI","Helvetica Neue",system-ui,sans-serif}
*{box-sizing:border-box;margin:0}
body{min-height:100vh;color:var(--moon);font:400 16px/1.5 var(--sans);
background:var(--lapis) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Cg fill='none' stroke='%23fff' stroke-opacity='.06'%3E%3Crect x='14' y='14' width='36' height='36'/%3E%3Crect x='14' y='14' width='36' height='36' transform='rotate(45 32 32)'/%3E%3C/g%3E%3C/svg%3E")}
.wrap{max-width:1240px;margin:0 auto;padding:clamp(18px,4vw,52px)}
h1{font:200 clamp(2.8rem,7vw,5.2rem)/1 var(--sans);letter-spacing:-.035em}
.lede{color:var(--mist);max-width:50ch;margin-top:.7rem}
.modes{display:inline-flex;margin-top:1.5rem;background:var(--deep);border-radius:999px;padding:4px}
.modes button{font:inherit;color:var(--mist);background:none;border:0;border-radius:999px;padding:.55rem 1.3rem;cursor:pointer;transition:background .2s,color .2s}
.modes button[aria-checked=true]{background:var(--moon);color:var(--deep);font-weight:600}
.board{display:grid;grid-template-columns:minmax(170px,1fr) minmax(320px,540px) minmax(170px,1fr);gap:clamp(16px,3vw,48px);align-items:center;margin-top:.5rem}
.side.l{text-align:right}
.side label{color:var(--mist);font-size:1.1rem}
.side input{display:block;width:100%;background:none;border:0;border-bottom:2px solid var(--line);color:var(--moon);
font:300 clamp(2.2rem,4.6vw,3.3rem)/1.15 var(--sans);font-variant-numeric:tabular-nums;padding:.1rem 0;outline:0;text-align:inherit;transition:border-color .2s}
.side input:focus{border-color:var(--saffron)}
.side input::placeholder{color:var(--line)}
.side.err input{border-color:var(--coral)}
.hint{min-height:3em;font-size:.88rem;color:var(--mist);margin-top:.3rem}
.err .hint{color:var(--coral)}
#dial{width:100%;display:block;overflow:visible}
.disc{fill:var(--deep);stroke:#2b3f84}
.tk{stroke:var(--line)}.tk.h{stroke:var(--mist)}
.num{fill:var(--mist);font-size:11px;text-anchor:middle;dominant-baseline:central}
.rest{fill:none;stroke:var(--line);stroke-width:1.5;stroke-dasharray:1 5;stroke-linecap:round}
.span{fill:none;stroke:#5f7bd0;stroke-width:14}
.third{fill:none;stroke:var(--turq);stroke-width:14}
.needle{stroke:var(--saffron);stroke-opacity:.7}
.star{fill:var(--saffron);filter:drop-shadow(0 0 7px rgba(255,184,28,.7))}
.end{fill:var(--moon)}
.lab{fill:var(--moon);font-size:12px;text-anchor:middle;dominant-baseline:central}
.cap,.sub{fill:var(--mist);font-size:13px;text-anchor:middle}
.big{fill:var(--moon);font-size:38px;font-weight:300;text-anchor:middle;font-variant-numeric:tabular-nums}
.flag{fill:var(--saffron);font-size:12px;font-weight:600;text-anchor:middle}
.stale .big,.stale .cap,.stale .sub,.stale .flag{opacity:.3}
.facts{display:flex;flex-wrap:wrap;justify-content:center;gap:1rem 3.5rem;margin-top:2rem}
.facts dt{color:var(--mist);font-size:.92rem}
.facts dd{font:300 1.7rem/1.2 var(--sans);font-variant-numeric:tabular-nums}
.actions{display:flex;flex-wrap:wrap;justify-content:center;gap:.8rem;margin-top:1.8rem}
.btn{font:inherit;color:var(--moon);background:none;border:1px solid var(--line);border-radius:8px;padding:.6rem 1.1rem;cursor:pointer;transition:border-color .2s}
.btn:hover{border-color:var(--saffron)}
.btn.pri{background:var(--saffron);border-color:var(--saffron);color:#2a1d00;font-weight:600}
.notes{list-style:none;padding:0;margin:1.2rem auto 0;max-width:62ch;text-align:center;color:var(--saffron);font-size:.95rem}
.notes .bad{color:var(--coral)}
.sr{position:absolute;left:-9999px}
footer{margin-top:3rem;color:#7389c6;font-size:.84rem;text-align:center}
:focus-visible{outline:2px solid var(--saffron);outline-offset:3px}
@media(max-width:900px){.board{grid-template-columns:1fr 1fr}.stage{grid-column:1/-1;order:-1}.side.l{text-align:left}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Mitternacht</h1>
    <p class="lede">Enter Fajr and Maghrib and read the middle of the night off the dial. Any format works: 530, 5:30 am, 17h42.</p>
    <div class="modes" role="radiogroup" aria-label="What to find">
      <button type="button" role="radio" data-mode="night">Middle of the night</button>
      <button type="button" role="radio" data-mode="day">Middle of the day</button>
    </div>
  </header>

  <main class="board">
    <div class="side l" id="f-fajr">
      <label for="fajr">Fajr</label>
      <input id="fajr" autocomplete="off" spellcheck="false" placeholder="05:30">
      <p class="hint" id="h-fajr"></p>
    </div>
    <div class="stage"><svg id="dial" viewBox="0 0 400 400" role="img" aria-label="24-hour dial showing the midpoint"></svg></div>
    <div class="side r" id="f-maghrib">
      <label for="maghrib">Maghrib</label>
      <input id="maghrib" autocomplete="off" spellcheck="false" placeholder="18:00">
      <p class="hint" id="h-maghrib"></p>
    </div>
  </main>

  <dl class="facts" id="facts"></dl>
  <div class="actions">
    <button type="button" class="btn pri" id="copy">Copy time</button>
    <button type="button" class="btn" id="swap">Swap Fajr and Maghrib</button>
  </div>
  <ul class="notes" id="notes"></ul>
  <p class="sr" id="sr" aria-live="polite"></p>
  <footer>Runs only on this computer. Press ↑ or ↓ in a field to nudge it by a minute (Shift for ten). Times are wall-clock, so a daylight-saving change during the night isn’t adjusted for.</footer>
</div>

<script nonce="__NONCE__">
(() => {
"use strict";
const $ = s => document.querySelector(s), NS = "http://www.w3.org/2000/svg";
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const kv = { get(k, d) { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
             set(k, v) { try { localStorage.setItem(k, v); } catch {} } };
const inputs = { fajr: $("#fajr"), maghrib: $("#maghrib") };
const state = { mode: kv.get("mode", "night") === "day" ? "day" : "night", parsed: {}, last: null };
inputs.fajr.value = kv.get("fajr", "05:30");
inputs.maghrib.value = kv.get("maghrib", "18:00");

/* ---- dial: noon at the top, midnight at the bottom, time runs clockwise ---- */
const svg = $("#dial"), C = 200, R = 134, TAU = Math.PI * 2, DAY = 86400;
const mk = (tag, a, parent = svg) => { const n = document.createElementNS(NS, tag); for (const k in a) n.setAttribute(k, a[k]); parent.appendChild(n); return n; };
const pt = (s, r) => { const a = ((s % DAY) - DAY / 2) / DAY * TAU; return [C + r * Math.sin(a), C - r * Math.cos(a)]; };
const arc = (a, b, r) => { const [x0, y0] = pt(a, r), [x1, y1] = pt(b, r); return `M${x0} ${y0}A${r} ${r} 0 ${b - a > DAY / 2 ? 1 : 0} 1 ${x1} ${y1}`; };

mk("circle", { cx: C, cy: C, r: 150, class: "disc" });
for (let i = 0; i < 96; i++) {
  const major = i % 4 === 0, [x0, y0] = pt(i * 900, 150), [x1, y1] = pt(i * 900, major ? 162 : 156);
  mk("line", { x1: x0, y1: y0, x2: x1, y2: y1, class: "tk" + (major ? " h" : "") });
}
for (let h = 0; h < 24; h += 3) {
  const [x, y] = pt(h * 3600, 180);
  mk("text", { x, y, class: "num" }).textContent = h === 0 ? "midnight" : h === 12 ? "noon" : String(h).padStart(2, "0");
}
const rest = mk("path", { class: "rest" }), span = mk("path", { class: "span" }), third = mk("path", { class: "third" });
const needle = mk("line", { class: "needle" });
const eS = mk("circle", { r: 5, class: "end" }), eE = mk("circle", { r: 5, class: "end" });
const lS = mk("text", { class: "lab" }), lE = mk("text", { class: "lab" });
const star = mk("polygon", { class: "star", points: Array.from({ length: 16 }, (_, i) => {
  const r = i % 2 ? 6.5 : 12, a = i * Math.PI / 8; return `${(r * Math.sin(a)).toFixed(2)},${(-r * Math.cos(a)).toFixed(2)}`; }).join(" ") });
const cap = mk("text", { x: C, y: 172, class: "cap" }), big = mk("text", { x: C, y: 213, class: "big" }),
      sub = mk("text", { x: C, y: 238, class: "sub" }), flag = mk("text", { x: C, y: 258, class: "flag" });

function draw(c) {
  rest.setAttribute("d", arc(c.e, c.s + DAY, R));
  span.setAttribute("d", arc(c.s, c.e, R));
  third.setAttribute("d", c.e - c.t > 1 ? arc(c.t, c.e, R) : "");
  const [a, b] = pt(c.m, 108), [x, y] = pt(c.m, R);
  for (const [k, v] of [["x1", a], ["y1", b], ["x2", x], ["y2", y]]) needle.setAttribute(k, v);
  star.setAttribute("transform", `translate(${x} ${y})`);
  for (const [dot, lab, s] of [[eS, lS, c.s], [eE, lE, c.e]]) {
    const [px, py] = pt(s, R), [tx, ty] = pt(s, 114);
    dot.setAttribute("cx", px); dot.setAttribute("cy", py); lab.setAttribute("x", tx); lab.setAttribute("y", ty);
  }
}
let cur = null, raf = 0;
function tween(target) {
  if (!cur) cur = { ...target };
  const from = { ...cur }, t0 = performance.now(), D = reduce ? 0 : 600;
  cancelAnimationFrame(raf);
  const step = now => {
    const k = D ? Math.min(1, (now - t0) / D) : 1, e = 1 - Math.pow(1 - k, 3);
    for (const key of ["s", "e", "m", "t"]) cur[key] = from[key] + (target[key] - from[key]) * e;
    draw(cur);
    if (k < 1) raf = requestAnimationFrame(step);
  };
  raf = requestAnimationFrame(step);
}

/* ---- talking to the Python server ---- */
function render(res) {
  for (const f of ["fajr", "maghrib"]) {
    const err = res.errors && res.errors[f], p = res.parsed && res.parsed[f];
    $("#f-" + f).classList.toggle("err", !!err);
    $("#h-" + f).textContent = err || (p ? "Read as " + p : "");
    state.parsed[f] = p || null;
  }
  svg.classList.toggle("stale", !res.ok);
  const notes = $("#notes"); notes.replaceChildren();
  const note = (t, bad) => { const li = document.createElement("li"); li.textContent = t; if (bad) li.className = "bad"; notes.appendChild(li); };
  if (res.fatal) note(res.fatal, true);
  if (!res.ok) return;
  state.last = res;
  cap.textContent = res.caption; big.textContent = res.mid; sub.textContent = res.sub;
  flag.textContent = res.mid_next ? "next day" : "";
  lS.textContent = res.labels.s; lE.textContent = res.labels.e;
  $("#facts").replaceChildren(...res.rows.map(([k, v]) => {
    const d = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
    dt.textContent = k; dd.textContent = v; d.append(dt, dd); return d; }));
  res.notes.forEach(n => note(n));
  $("#sr").textContent = `${res.caption}: ${res.mid}${res.mid_next ? ", next day" : ""}`;
  tween(res.dial);
}

let seq = 0, timer = 0;
async function calc() {
  const mine = ++seq;
  let res;
  try {
    const r = await fetch("/api/calc", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fajr: inputs.fajr.value, maghrib: inputs.maghrib.value, mode: state.mode }) });
    res = await r.json();
  } catch { res = { ok: false, fatal: "Can’t reach the local server. Is mitternacht.py still running?" }; }
  if (mine === seq) render(res);
}
const queue = () => { clearTimeout(timer); timer = setTimeout(calc, 120); };

/* ---- interactions ---- */
for (const [name, input] of Object.entries(inputs)) {
  input.addEventListener("input", () => { kv.set(name, input.value); queue(); });
  input.addEventListener("focus", () => input.select());
  input.addEventListener("keydown", e => {
    if (e.key !== "ArrowUp" && e.key !== "ArrowDown") return;
    const p = state.parsed[name]; if (!p) return;
    e.preventDefault();
    const [h, m] = p.split(":").map(Number), step = (e.key === "ArrowUp" ? 1 : -1) * (e.shiftKey ? 10 : 1);
    const t = (((h * 60 + m + step) % 1440) + 1440) % 1440;
    input.value = String(Math.floor(t / 60)).padStart(2, "0") + ":" + String(t % 60).padStart(2, "0");
    input.dispatchEvent(new Event("input"));
  });
}
const paintModes = () => document.querySelectorAll(".modes button")
  .forEach(b => b.setAttribute("aria-checked", String(b.dataset.mode === state.mode)));
document.querySelectorAll(".modes button").forEach(b => b.addEventListener("click", () => {
  state.mode = b.dataset.mode; kv.set("mode", state.mode); paintModes(); calc(); }));
$("#swap").addEventListener("click", () => {
  [inputs.fajr.value, inputs.maghrib.value] = [inputs.maghrib.value, inputs.fajr.value];
  kv.set("fajr", inputs.fajr.value); kv.set("maghrib", inputs.maghrib.value); calc(); });
$("#copy").addEventListener("click", async () => {
  if (!state.last) return;
  const b = $("#copy");
  try { await navigator.clipboard.writeText(state.last.mid); b.textContent = "Copied"; }
  catch { b.textContent = "Copy blocked by the browser"; }
  setTimeout(() => { b.textContent = "Copy time"; }, 1500);
});

paintModes(); calc();
})();
</script>
</body>
</html>
""".replace("__NONCE__", NONCE).encode("utf-8")

# ───────────────────────── server ─────────────────────────

class Handler(BaseHTTPRequestHandler):
    server_version = "Mitternacht"

    def log_message(self, *args):  # keep the terminal quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         f"default-src 'none'; script-src 'nonce-{NONCE}'; style-src 'unsafe-inline'; "
                         "connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict):
        self._send(code, json.dumps(obj).encode(), "application/json; charset=utf-8")

    def _host_ok(self) -> bool:  # blocks DNS-rebinding tricks from other websites
        return (self.headers.get("Host") or "").lower() in self.server.allowed_hosts

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, b"Forbidden", "text/plain")
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif path == "/favicon.ico":
            self._send(204, b"", "image/x-icon")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self):
        if not self._host_ok():
            return self._send(403, b"Forbidden", "text/plain")
        if self.path != "/api/calc":
            return self._send(404, b"Not found", "text/plain")
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self._json(415, {"ok": False, "fatal": "Unsupported content type."})
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if not 0 < length <= MAX_BODY:
                raise ValueError
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"ok": False, "fatal": "Bad request."})
        mode = "day" if data.get("mode") == "day" else "night"
        self._json(200, calculate(str(data.get("fajr", ""))[:40], str(data.get("maghrib", ""))[:40], mode))


def main():
    ap = argparse.ArgumentParser(description="Mitternacht: local midpoint calculator for Fajr and Maghrib")
    ap.add_argument("--port", type=int, default=8765, help="preferred port (default 8765)")
    ap.add_argument("--no-browser", action="store_true", help="don’t open the browser automatically")
    args = ap.parse_args()

    httpd = None
    for port in [args.port, *range(args.port + 1, args.port + 20), 0]:  # 0 = any free port
        try:
            httpd = ThreadingHTTPServer((HOST, port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        raise SystemExit("Could not open a local port.")

    port = httpd.server_address[1]
    httpd.allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    url = f"http://127.0.0.1:{port}/"
    print(f"Mitternacht is running at {url}\nPress Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()