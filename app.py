from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import re, time, threading, urllib.parse, random, os, datetime
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller

app = Flask(__name__)

contacts = []
running = False
next_time = 0

driver = None

# 🔥 MULTI ACCOUNT CONFIG
accounts = [1, 2, 3]
current_account_index = 0

# 🔥 DELAY (5–9 minutes)
MIN_DELAY = 5 * 60
MAX_DELAY = 9 * 60

MAX_RETRY = 2


# ---------------------
# SAVE DONE HISTORY
# ---------------------
def save_done_history(contact):

    data = {
        "phone": contact["phone"],
        "message": contact["message"],
        "status": contact["status"],
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    new_df = pd.DataFrame([data])

    file = "done_history.xlsx"

    if os.path.exists(file):
        old_df = pd.read_excel(file)
        combined = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined = new_df

    combined.to_excel(file, index=False)


# ---------------------
# CLEAN PHONE
# ---------------------
def clean_phone(val):
    val = str(val)
    val = re.sub(r'\D', '', val)

    if len(val) == 10:
        return "91" + val
    elif val.startswith("91") and len(val) == 12:
        return val
    return None


# ---------------------
# LOGIN ALL ACCOUNTS
# ---------------------
@app.route("/login_all")
def login_all():

    for acc in accounts:

        print(f"Opening login for account {acc}")

        options = Options()
        options.add_argument("--start-maximized")

        profile_path = os.path.abspath(f"./profiles/profile_{acc}")
        os.makedirs(profile_path, exist_ok=True)

        options.add_argument(f"--user-data-dir={profile_path}")

        chromedriver_autoinstaller.install()

        d = webdriver.Chrome(options=options)

        d.get("https://web.whatsapp.com")

        print(f"Scan QR for Account {acc}")

        WebDriverWait(d, 120).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id="pane-side"]')
            )
        )

        print(f"Account {acc} logged in")

        d.quit()

    return "All accounts logged in"


# ---------------------
# INIT DRIVER
# ---------------------
def init_driver():
    global driver, current_account_index

    try:
        if driver:
            driver.quit()
    except:
        pass

    driver = None

    account = accounts[current_account_index]

    options = Options()
    options.add_argument("--start-maximized")

    profile_path = os.path.abspath(f"./profiles/profile_{account}")
    os.makedirs(profile_path, exist_ok=True)

    options.add_argument(f"--user-data-dir={profile_path}")

    chromedriver_autoinstaller.install()

    driver = webdriver.Chrome(options=options)

    driver.get("https://web.whatsapp.com")

    print(f"Using Account {account}")

    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@id="pane-side"]')
        )
    )

    return True


# ---------------------
# SWITCH ACCOUNT
# ---------------------
def switch_account():
    global current_account_index

    current_account_index += 1

    if current_account_index >= len(accounts):
        print("All accounts used")
        return False

    print(f"Switching to account {accounts[current_account_index]}")

    return init_driver()


# ---------------------
# GET NEXT CONTACT
# ---------------------
def get_next_contact():

    for c in contacts:

        if c["status"] == "PENDING":
            return c

        if "RETRY" in c["status"]:
            return c

    return None


# ---------------------
# MAIN LOOP
# ---------------------
def start_sending():

    global running, next_time

    if not init_driver():
        running = False
        return

    while running:

        c = get_next_contact()

        if not c:
            print("All done")
            break

        print("Sending →", c["phone"])

        url = f"https://web.whatsapp.com/send?phone={c['phone']}&text={urllib.parse.quote(c['message'])}"

        driver.get(url)

        time.sleep(5)

        try:

            # 🔥 INVALID NUMBER CHECK
            page = driver.page_source.lower()

            invalid_texts = [
                "phone number shared via url is invalid",
                "not on whatsapp",
                "invalid phone number",
                "couldn't find this account"
            ]

            is_invalid = any(
                text in page for text in invalid_texts
            )

            if is_invalid:

                c["status"] = "INVALID"

                print("Invalid number → skipped")

                next_time = 0

                continue

            # 🔥 WAIT FOR CHAT BOX
            box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"]')
                )
            )

            time.sleep(2)

            box.send_keys(Keys.ENTER)

            c["status"] = "DONE"

            # 🔥 SAVE SUCCESS
            save_done_history(c)

            print("Message sent")

            # 🔥 ONLY DELAY AFTER SUCCESS
            delay = random.randint(MIN_DELAY, MAX_DELAY)

            start = time.time()

            while running:

                remain = delay - int(time.time() - start)

                if remain <= 0:
                    break

                next_time = remain

                time.sleep(1)

            next_time = 0

        except Exception as e:

            print("Error:", e)

            c["retry"] += 1
            c["error"] = str(e)

            # 🔥 RETRY REAL FAILURES
            if c["retry"] <= MAX_RETRY:

                c["status"] = f"RETRY {c['retry']}"

                print("Retrying...")

            else:

                c["status"] = "FAILED"

                print("Switching account...")

                if not switch_account():
                    running = False
                    break

    running = False
    next_time = 0


# ---------------------
# ROUTES
# ---------------------
@app.route("/", methods=["GET", "POST"])
def index():

    global contacts

    if request.method == "POST":

        file = request.files.get("file")

        df = pd.read_excel(file)

        contacts.clear()

        for _, row in df.iterrows():

            phone = clean_phone(row["Phone"])
            message = str(row["Message"])

            if phone:

                contacts.append({
                    "phone": phone,
                    "message": message,
                    "status": "PENDING",
                    "retry": 0
                })

        return render_template("index.html")

    return render_template("index.html")


@app.route("/start")
def start():

    global running

    if not running:

        running = True

        threading.Thread(target=start_sending).start()

    return "started"


@app.route("/resume")
def resume():

    global running

    if not running:

        running = True

        threading.Thread(target=start_sending).start()

    return "resumed"


@app.route("/stop")
def stop():

    global running, next_time

    running = False
    next_time = 0

    return "stopped"


@app.route("/status")
def status():

    done = sum(
        1 for c in contacts
        if c["status"] == "DONE"
    )

    return jsonify({
        "contacts": contacts,
        "total": len(contacts),
        "done": done,
        "next_time": next_time
    })


@app.route("/download")
def download():

    df = pd.DataFrame(contacts)

    output = BytesIO()

    df.to_excel(output, index=False)

    output.seek(0)

    return send_file(
        output,
        download_name="swap_report.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)