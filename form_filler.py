"""
Google Form Auto-Filler
=======================
Fills a Google Form N times with randomized answers,
human-like delays, and stealth ChromeOptions.

HOW TO USE
----------
1. Install dependencies:
       pip install selenium webdriver-manager

2. Set your target URL and submission count below.
3. Run:  python form_filler.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import logging

# ──────────────────────────────────────────────
#  CONFIGURATION  ← Edit these values
# ──────────────────────────────────────────────
FORM_URL      = "https://docs.google.com/forms/d/e/1FAIpQLScYOZ0Zliwr61jRtkBRZE4krNZs0CqyejsXefGE9m9nU102mA/viewform"
NUM_RESPONSES = 20          # How many times to submit the form
MIN_DELAY     = 1.0         # Minimum seconds between clicks
MAX_DELAY     = 3.0         # Maximum seconds between clicks
THINK_MIN     = 2.0         # Minimum 'thinking' pause before submit
THINK_MAX     = 5.0         # Maximum 'thinking' pause before submit
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── Browser Setup ────────────────────────────────────────────────────────────

def crear_driver() -> webdriver.Chrome:
    """Build a stealthy ChromeDriver instance."""
    opciones = Options()

    # ── Stealth flags ──────────────────────────────────────────────────────
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option("useAutomationExtension", False)

    # ── Realistic User-Agent ───────────────────────────────────────────────
    opciones.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # ── Optional: run headless (comment out to watch the browser) ──────────
    # opciones.add_argument("--headless=new")
    opciones.add_argument("--window-size=1280,900")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=opciones)

    # Remove the 'navigator.webdriver' property to further avoid detection
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# ─── Helper Utilities ─────────────────────────────────────────────────────────

def pausa_humana(min_s: float = MIN_DELAY, max_s: float = MAX_DELAY) -> None:
    """Sleep for a random interval to simulate human reaction time."""
    t = random.uniform(min_s, max_s)
    time.sleep(t)


def pausa_pensando() -> None:
    """Longer pause before submitting — simulates reading the form."""
    t = random.uniform(THINK_MIN, THINK_MAX)
    log.info("  💭 Thinking for %.1f s before submitting…", t)
    time.sleep(t)


# ─── Core Form Logic ──────────────────────────────────────────────────────────

def seleccionar_opciones(driver: webdriver.Chrome) -> None:
    """
    Find every question container and randomly pick one option.

    Works for:
      • Single-choice (radio buttons)  → class 'freebirdFormviewerComponentsQuestionRadioChoice'
      • Multiple-choice (checkboxes)   → class 'freebirdFormviewerComponentsQuestionCheckboxChoice'
      • Linear scale                   → role='radio' inside a scale container
    """
    wait = WebDriverWait(driver, 15)

    # Wait until at least one question is present
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "[data-params]")
    ))

    # ── Radio / scale questions ────────────────────────────────────────────
    # Each question block groups its radio items; we must pick ONE per group.
    question_blocks = driver.find_elements(
        By.CSS_SELECTOR,
        "div[role='radiogroup']"
    )
    log.info("  Found %d radio group(s)", len(question_blocks))

    for bloque in question_blocks:
        opciones = bloque.find_elements(By.CSS_SELECTOR, "[role='radio']")
        if not opciones:
            continue
        elegida = random.choice(opciones)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elegida)
        pausa_humana(0.4, 1.2)
        elegida.click()
        log.info("    ✔ Picked radio option: '%s'", elegida.get_attribute("data-value") or "?")
        pausa_humana()

    # ── Checkbox questions ─────────────────────────────────────────────────
    # For checkboxes we pick 1-N random options per group.
    checkbox_groups = driver.find_elements(
        By.CSS_SELECTOR,
        "div[role='group']"
    )
    log.info("  Found %d checkbox group(s)", len(checkbox_groups))

    for grupo in checkbox_groups:
        opciones = grupo.find_elements(By.CSS_SELECTOR, "[role='checkbox']")
        if not opciones:
            continue
        # Pick at least 1 option, up to all of them
        cantidad = random.randint(1, len(opciones))
        elegidas = random.sample(opciones, cantidad)
        for caja in elegidas:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", caja)
            pausa_humana(0.3, 0.9)
            caja.click()
            log.info("    ✔ Checked option: '%s'", caja.get_attribute("aria-label") or "?")
        pausa_humana()

    # ── Dropdown questions ─────────────────────────────────────────────────
    dropdowns = driver.find_elements(
        By.CSS_SELECTOR,
        "div[role='listbox']"
    )
    log.info("  Found %d dropdown(s)", len(dropdowns))

    for lista in dropdowns:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", lista)
        pausa_humana(0.5, 1.0)
        lista.click()          # open the dropdown
        pausa_humana(0.5, 1.0)
        opciones = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
        if not opciones:
            continue
        # Skip the first placeholder option if present
        validas = [o for o in opciones if o.get_attribute("data-value") not in ("", None)]
        if not validas:
            validas = opciones
        elegida = random.choice(validas)
        elegida.click()
        log.info("    ✔ Selected dropdown: '%s'", elegida.text or "?")
        pausa_humana()


def enviar_formulario(driver: webdriver.Chrome) -> None:
    """Scroll to and click the Submit button."""
    wait = WebDriverWait(driver, 15)
    boton = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "[role='button'][jsname='M2UYVd']")
    ))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
    pausa_pensando()
    boton.click()
    log.info("  ✅ Form submitted!")


def click_submit_another(driver: webdriver.Chrome) -> bool:
    """
    After a successful submission Google shows a
    'Submit another response' link. Click it to reuse the same session.
    Returns True if found and clicked, False otherwise.
    """
    try:
        wait = WebDriverWait(driver, 10)
        enlace = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(., 'Submit another response')]"
                       " | //a[contains(., 'Enviar otra respuesta')]")
        ))
        enlace.click()
        log.info("  🔄 Clicked 'Submit another response'")
        return True
    except Exception:
        return False


# ─── Main Loop ────────────────────────────────────────────────────────────────

def llenar_encuesta() -> None:
    """Open the browser once and submit the form NUM_RESPONSES times."""
    log.info("🚀 Starting — %d responses to submit", NUM_RESPONSES)
    driver = crear_driver()

    try:
        # Load the form for the first time
        driver.get(FORM_URL)
        pausa_humana(2.0, 4.0)   # Wait for page JS to settle

        for intento in range(1, NUM_RESPONSES + 1):
            log.info("── Response %d / %d ──────────────────────", intento, NUM_RESPONSES)
            try:
                seleccionar_opciones(driver)
                enviar_formulario(driver)

                # Try to reuse the session; fall back to a full reload
                if not click_submit_another(driver):
                    log.warning("  ⚠ 'Submit another' not found — reloading form URL")
                    driver.get(FORM_URL)

                pausa_humana(2.0, 4.0)  # Settle before next iteration

            except Exception as err:
                log.error("  ❌ Submission %d failed: %s — skipping", intento, err)
                # Try to recover by navigating back to the form
                try:
                    driver.get(FORM_URL)
                    pausa_humana(2.0, 4.0)
                except Exception:
                    pass  # If recovery also fails, the next loop iteration will handle it

    finally:
        log.info("🏁 All done. Closing browser.")
        driver.quit()


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    llenar_encuesta()
