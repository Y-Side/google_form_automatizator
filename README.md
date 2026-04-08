# 🤖 Google Form Auto-Filler

A stealthy Python automation script that fills and submits Google Forms multiple times using **Selenium WebDriver** — with randomized answers, human-like delays, and anti-bot detection measures.

---

## ✨ Features

- 🔁 **Multi-submission loop** — Submit the same form N times in a single run
- 🎲 **Randomized answers** — Picks random options for radio buttons, checkboxes, dropdowns, and linear scales
- 🧠 **Human-like timing** — Configurable random delays between interactions and a "thinking" pause before each submit
- 🥷 **Stealth mode** — Hides automation fingerprints by:
  - Disabling `AutomationControlled` Blink features
  - Removing the `navigator.webdriver` property via JavaScript
  - Using a realistic Chrome User-Agent string
  - Suppressing the "Chrome is being controlled" banner
- ♻️ **Session reuse** — Clicks "Submit another response" to reuse the browser session instead of reloading
- 🛡️ **Error handling** — Automatically recovers from failed submissions and continues the loop
- 📋 **Detailed logging** — Timestamped console output for every step

---

## 📋 Requirements

- Python **3.8+**
- Google Chrome installed

### Python dependencies

```bash
pip install selenium webdriver-manager
```

> `webdriver-manager` automatically downloads and manages the correct `chromedriver` version for your Chrome installation — no manual setup needed.

---

## 🚀 Quick Start

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. **Install dependencies**

   ```bash
   pip install selenium webdriver-manager
   ```

3. **Configure the script**

   Open `form_filler.py` and edit the configuration block at the top:

   ```python
   FORM_URL      = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
   NUM_RESPONSES = 20    # Number of times to submit the form
   MIN_DELAY     = 1.0   # Minimum seconds between clicks
   MAX_DELAY     = 3.0   # Maximum seconds between clicks
   THINK_MIN     = 2.0   # Minimum pause before submitting
   THINK_MAX     = 5.0   # Maximum pause before submitting
   ```

4. **Run the script**

   ```bash
   python form_filler.py
   ```

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `FORM_URL` | *(your form URL)* | Full URL of the Google Form to fill |
| `NUM_RESPONSES` | `20` | Number of form submissions to perform |
| `MIN_DELAY` | `1.0` | Minimum seconds between individual field clicks |
| `MAX_DELAY` | `3.0` | Maximum seconds between individual field clicks |
| `THINK_MIN` | `2.0` | Minimum "thinking" pause before the submit button is clicked |
| `THINK_MAX` | `5.0` | Maximum "thinking" pause before the submit button is clicked |

---

## 🧩 How It Works

```
Start
  └─ Open Chrome (stealthy mode)
       └─ Load form URL
            └─ For each response (1 → NUM_RESPONSES):
                 ├─ Select random radio option per question group
                 ├─ Check random checkbox(es) per checkbox group
                 ├─ Pick random option from each dropdown
                 ├─ Pause (human "thinking" delay)
                 ├─ Click Submit
                 └─ Click "Submit another response" (or reload form)
  └─ Close browser
```

### Supported question types

| Type | Strategy |
|---|---|
| **Radio / Linear Scale** | Picks one random option per `radiogroup` |
| **Checkboxes** | Picks 1–N random options per `group` |
| **Dropdowns** | Opens the list and picks a random valid option (skips placeholder) |

---

## 🔇 Running Headless

To run in the background without a visible browser window, uncomment the following line inside `crear_driver()`:

```python
# opciones.add_argument("--headless=new")
```

---

## 📝 Sample Output

```
17:02:01  [INFO]  🚀 Starting — 20 responses to submit
17:02:05  [INFO]  ── Response 1 / 20 ──────────────────────
17:02:05  [INFO]    Found 3 radio group(s)
17:02:07  [INFO]      ✔ Picked radio option: 'Option A'
17:02:09  [INFO]      ✔ Picked radio option: 'Strongly Agree'
17:02:11  [INFO]      ✔ Picked radio option: '4'
17:02:11  [INFO]    Found 1 checkbox group(s)
17:02:13  [INFO]      ✔ Checked option: 'Python'
17:02:13  [INFO]    Found 0 dropdown(s)
17:02:13  [INFO]    💭 Thinking for 3.7 s before submitting…
17:02:17  [INFO]    ✅ Form submitted!
17:02:17  [INFO]    🔄 Clicked 'Submit another response'
...
17:08:44  [INFO]  🏁 All done. Closing browser.
```

---

## ⚠️ Disclaimer

This tool is intended for **educational and testing purposes only** (e.g., stress-testing your own forms, QA automation, or research). Use it responsibly and only on forms you own or have explicit permission to automate. Misuse to manipulate surveys or violate platform Terms of Service is your own responsibility.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
