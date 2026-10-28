# Mitternacht

```
███╗   ███╗██╗████████╗████████╗███████╗██████╗ ███╗   ██╗ █████╗  ██████╗██╗  ██╗████████╗
████╗ ████║██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔════╝██║  ██║╚══██╔══╝
██╔████╔██║██║   ██║      ██║   █████╗  ██████╔╝██╔██╗ ██║███████║██║     ███████║   ██║
██║╚██╔╝██║██║   ██║      ██║   ██╔══╝  ██╔══██╗██║╚██╗██║██╔══██║██║     ██╔══██║   ██║
██║ ╚═╝ ██║██║   ██║      ██║   ███████╗██║  ██║██║ ╚████║██║  ██║╚██████╗██║  ██║   ██║
╚═╝     ╚═╝╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝

                   Find the middle of the night between Maghrib and Fajr
```

![License: MIT](https://img.shields.io/badge/License-MIT-ffb81c.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-13265f.svg)
![Dependencies: none](https://img.shields.io/badge/Dependencies-none-34d1bf.svg)

---

## What is Mitternacht?

**Mitternacht** (German for "midnight") is a small local web app that finds the midpoint of the night between **Maghrib** and **Fajr**. It can also find the midpoint of the day, from Fajr to Maghrib.

Type two times in almost any format. A 24-hour dial animates as you type and shows the result. The app runs on your own computer, and nothing leaves it.

### Why?

The middle of the night is a useful reference point in the Islamic day. This tool does the arithmetic for you, including the tricky case where the night crosses midnight.

---

## Features

- **Live results:** the answer updates as you type
- **Flexible input:** accepts `530`, `5:30`, `05:30 am`, `17h42`, `05:30:15` and even `24:00`
- **Clear feedback:** the app shows how it read your input, explains errors in plain language, and warns about likely mistakes
- **Animated dial:** midnight at the bottom, noon at the top, and the midpoint marked by an eight-pointed star
- **Night or day mode:** find the middle of the night or the middle of the day with one click
- **Last third of the night:** night mode also shows when the last third begins
- **Midnight crossing:** handles spans such as Maghrib 18:00 to Fajr 05:30, and flags a result that falls on the next day
- **Keyboard nudging:** press ↑ or ↓ to change a time by one minute (hold Shift for ten)
- **Remembers your input:** your last times are stored in the browser
- **Exact to the second:** rounded half up
- **Local and locked down:** standard library only, bound to `127.0.0.1`

---

## Quick start

### Requirements

- Python 3.8 or newer
- A web browser

### Run it

```bash
python mitternacht.py
```

Your browser opens automatically. If it does not, open the address printed in the terminal (by default `http://127.0.0.1:8765`). On macOS and Linux you may need to type `python3` instead of `python`.

### Options

```bash
python mitternacht.py --port 9000        # use port 9000 instead of 8765
python mitternacht.py --no-browser       # do not open the browser automatically
```

If the chosen port is busy, the app picks the next free one. Stop it at any time with **Ctrl+C**.

---

## How to use

1. **Enter the Fajr time**, the dawn prayer time for your location.
2. **Enter the Maghrib time**, the sunset prayer time.
3. **Choose a mode:** "Middle of the night" (Maghrib to the next Fajr) or "Middle of the day" (Fajr to Maghrib).
4. **Read the dial.** The saffron star marks the result, and the same time is shown in the centre.

Accepted time formats:

- `530`, `5:30` or `05:30`
- `5:30 am`, `5:30pm` or `17:30`
- `5h30` or `5.30`
- `05:30:15`, with seconds

Handy controls:

- Clicking a field selects its whole content.
- **↑ / ↓** nudge the time by 1 minute, **Shift + ↑ / ↓** by 10 minutes.
- **Copy time** copies the result to the clipboard.
- **Swap Fajr and Maghrib** exchanges the two fields if you entered them the wrong way round.

---

## Design

The interface is lapis blue with saffron and turquoise, inspired by Islamic tilework:

- **Lapis** (`#13265f`) for the page
- **Saffron** (`#ffb81c`) for the midpoint star and focus states
- **Turquoise** (`#34d1bf`) for the last third of the night
- Responsive layout for desktop and phone
- Smooth dial animation, switched off if your system asks for reduced motion

No framework and no build step. It is plain HTML, CSS and JavaScript embedded in the Python file.

---

## Safety and privacy

- **Local only:** the server listens on `127.0.0.1`, so it is not reachable from your network.
- **Standard library only:** `http.server`, `json`, `re`, `argparse`, `secrets`, `threading` and `webbrowser`.
- **No tracking:** no analytics, no cookies, no external requests.
- **Hardened responses:** content-security policy with a per-run nonce, `nosniff` and no-referrer headers.
- **Host check:** requests with an unexpected `Host` header are rejected, which guards against DNS rebinding.

---

## The maths

Middle of the night:

```
midpoint = Maghrib + (Fajr - Maghrib) / 2
```

Middle of the day:

```
midpoint = Fajr + (Maghrib - Fajr) / 2
```

If the second time is earlier than the first, it is treated as the next day. Results are rounded half up to the nearest second.

---

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Empty field | Asks for the missing time |
| Unreadable time | Explains the problem and suggests formats that work |
| Hour above 23, minute above 59, or hour outside 1-12 with am/pm | Rejected with a clear message |
| Identical times | Rejected: there is nothing to halve |
| Span crosses midnight | Handled automatically; a result after 00:00 is flagged "next day" |
| Fajr after noon, or Maghrib before noon | Warns that the am/pm or the order may be wrong |
| Span shorter than 3 h or longer than 21 h | Warns that the span is unusual |

---

## Project structure

```
mitternacht.py     the whole app: calculation, server and web page
LICENSE.txt        MIT License
README.md          this file
```

The app is about 450 lines of Python, including the embedded page.

---

## For developers

The server is a small `BaseHTTPRequestHandler`:

- `GET /` serves the page
- `POST /api/calc` accepts JSON with `fajr`, `maghrib` and `mode` (`"night"` or `"day"`) and returns the result

The calculation lives in `calculate()` and can be used on its own:

```python
from mitternacht import calculate

result = calculate("05:30", "18:00", "night")
print(result["mid"])  # 23:45:00
```

The page is stored in `PAGE` as a raw string. Edit it, restart the script and reload the browser. There is no build step.

---

## License

MIT License, copyright (c) 2026 Servet. See `LICENSE.txt` for details.

---

```
 ◆ Runs locally   ◆ No dependencies   ◆ No tracking   ◆ MIT licensed
```
