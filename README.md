# Mitternacht

```
    ███╗   ███╗██╗████████╗████████╗███████╗██████╗ ██╗   ██╗ █████╗ ██╗  ██╗████████╗
    ████╗ ████║██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗██║   ██║██╔══██╗██║  ██║╚══██╔══╝
    ██╔████╔██║██║   ██║      ██║   █████╗  ██████╔╝██║   ██║███████║███████║   ██║   
    ██║╚██╔╝██║██║   ██║      ██║   ██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══██║██╔══██║   ██║   
    ██║ ╚═╝ ██║██║   ██║      ██║   ███████╗██║  ██║ ╚████╔╝ ██║  ██║██║  ██║   ██║   
    ╚═╝     ╚═╝╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
                                                                                          
              Find the middle of the night between Maghrib and Fajr
                    on an animated 24-hour dial, instantly.
```

![License: MIT](https://img.shields.io/badge/License-MIT-ffb81c.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-13265f.svg)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-34d1bf.svg)
![Status: Active](https://img.shields.io/badge/Status-Active-34d1bf.svg)

---

## What is Mitternacht?

**Mitternacht** (German for "midnight") is a fast, beautiful local web app that calculates the midpoint of the night between **Maghrib** and **Fajr** prayer times—or the midpoint of the fasting day if you prefer.

Enter two times in any format you like. Watch an animated 24-hour dial light up in real-time as you type. Get your answer instantly. No server, no network, no tracking. Everything runs on your machine.

### Why?

The exact midpoint of the night matters in Islamic tradition. This tool makes finding it instant and intuitive—no fumbling with your calculator, no mental math.

---

## ✨ Features

- **Live calculation** — results update as you type
- **Flexible input** — accepts `530`, `5:30`, `05:30 am`, `17h42`, `05:30:15`, even `24:00`
- **Smart validation** — helpful error messages for bad input, soft warnings for likely mistakes
- **Beautiful dial** — a 24-hour clock with midnight at bottom, noon at top; your midpoint marked by an animated star
- **Night or day mode** — find the middle of the night *or* the fasting day with one click
- **Keyboard shortcuts** — ↑/↓ to nudge times by a minute (Shift for ten)
- **Remembers you** — your last inputs are saved in the browser
- **Totally safe** — runs 100% locally, stdlib-only Python, content-security policy headers
- **Midnight crossing** — handles times that span midnight (e.g., Maghrib 18:00 → Fajr 05:30)
- **Precise** — accurate to the second, rounded half up

---

## 🚀 Quick Start

### Requirements
- Python 3.8 or later (comes with macOS, Linux, Windows)
- A web browser (you already have one)

### Run it

```bash
python mitternacht.py
```

That's it. Your browser opens automatically. If it doesn't, visit `http://127.0.0.1:8765`.

### Options

```bash
python mitternacht.py --port 9000        # use port 9000 instead of 8765
python mitternacht.py --no-browser       # don't auto-open the browser
```

Stop it anytime with **Ctrl+C**.

---

## 🎨 Design

The interface is built from scratch with a lapis-blue aesthetic inspired by Islamic tilework:
- **Lapis base** (#13265f) — deep, calm, traditional
- **Saffron accents** (#ffb81c) — the star, focus states
- **Turquoise details** (#34d1bf) — the last-third marker on the dial
- **Responsive** — looks sharp on desktop, tablet, phone
- **Smooth animations** — dial updates glide (disabled if you prefer reduced motion)

No framework bloat. No npm install. Just HTML, CSS, and vanilla JavaScript—all embedded in the Python file.

---

## 📖 How to Use

1. **Enter Fajr time** — the dawn prayer time in your area
2. **Enter Maghrib time** — the sunset prayer time  
3. **Pick your mode** — "Middle of the night" (Maghrib → next Fajr) or "Middle of the day" (Fajr → Maghrib)
4. **Read the dial** — the golden star shows your answer

Use any time format:
- `530` or `5:30` or `05:30`
- `5:30 am` or `5:30pm` or `17:30`
- `5h30` or `5.30`
- Even `05:30:15` with seconds

The app shows what it read, so if you see something wrong, you know immediately.

### Keyboard tricks
- **Click a time field** → it selects all your text
- **↑ or ↓** → nudge by 1 minute (great for fine-tuning)
- **Shift + ↑ or ↓** → nudge by 10 minutes

### Copy the result
Click **Copy time** to grab the midpoint to your clipboard.

### Swap the times
Click **Swap Fajr and Maghrib** to reverse them (useful if you entered them backwards).

---

## 🔒 Safety & Privacy

- **Local only** — the server listens on `127.0.0.1` only; nothing leaves your machine
- **No dependencies** — uses only Python's standard library (`http.server`, `datetime`, `json`, `re`, `argparse`)
- **No tracking** — no analytics, no cookies, no external requests
- **Security headers** — strict content-security policy, no-sniff, no-referrer
- **Host check** — blocks DNS-rebinding attacks

---

## 🧮 The Math

### Middle of the night
```
midpoint = Maghrib + (Fajr − Maghrib) / 2
```
(If Fajr is earlier than Maghrib, we treat Fajr as the next day.)

### Middle of the day
```
midpoint = Fajr + (Maghrib − Fajr) / 2
```

Both are rounded half up to the nearest second.

---

## 📋 Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| Empty input | Clear, friendly message |
| Malformed time | Suggests a format that works |
| Swapped times (day mode) | Warns: "Check the order of your times" |
| Fajr in afternoon | Warns: "Fajr is normally before noon. Check am/pm." |
| Span < 3h or > 21h | Warns: unusual duration |
| Identical times | Rejected: "Same as the other time, so there is nothing to halve." |
| Crossing midnight | Automatically handled; result flagged "next day" if needed |

---

## 📦 Project Structure

```
mitternacht.py          # The entire app (single file)
LICENSE.txt             # MIT License
README.md               # This file
```

That's genuinely all you need. The app is ~600 lines of Python: time parsing, server, and the embedded HTML/CSS/JS page.

---

## 🛠 For Developers

### Extending it

The server is a simple class `Handler(BaseHTTPRequestHandler)`:
- `GET /` serves the HTML page
- `POST /api/calc` accepts JSON with `fajr`, `maghrib`, `mode` and returns results

The Python function `calculate()` does all the heavy lifting. You can import and use it standalone:

```python
from mitternacht import calculate

result = calculate("05:30", "18:00", "night")
print(result["mid"])  # "12:00:00" or similar
```

### Modifying the UI

The page is embedded in `PAGE` as a raw string. Edit the `<style>` block for colors, the SVG for the dial, or the `<script>` for behavior. Changes take effect on reload (no build step).

---

## 🌍 Localization

Right now it's in English. If you want to translate the UI or add support for different calendars (Gregorian, Hijri, etc.), it's straightforward—just modify the HTML and the response JSON from `/api/calc`.

---

## 📝 License

MIT License © 2026 Servet

You're free to use, modify, and distribute this software. See `LICENSE.txt` for details.

---


## 💬 Feedback

If something doesn't work, feels clunky, or you want a feature, the entire app is one readable Python file. Fork it, tinker, and make it yours.

---

**Made with ❤️ — a tool for precision, clarity, and beauty.**

```
 ◆ Runs locally  ◆ No dependencies  ◆ Zero tracking  ◆ MIT licensed
```
