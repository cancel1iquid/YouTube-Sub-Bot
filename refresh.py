from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time
import random
import os
import chromedriver_autoinstaller
from threading import Semaphore

sem = Semaphore(5) 
class cookies:
    def __init__(self, creds, index):
        self.driver = self._launch()
        self.creds = []
        for line in creds:
            if "|" in line:
                parts = line.split("|")
            else:
                parts = line.split(":")
            email = parts[0]
            password = parts[1] if len(parts) > 1 else ""
            recovery = parts[2] if len(parts) > 2 else None
            self.creds.append((email, password, recovery))

        self.index = index
        self.login()
        self.loopp()

    def _launch(self):
        import zipfile
        chromedriver_autoinstaller.install()

        try:
            with open("proxies.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            proxy = random.choice(proxies)
            print("Using proxy:", proxy)

            p = proxy.split("@")[-1]
            pp = proxy.split("@")[0]
            proxy_user, proxy_pass = pp.split(":")
            proxy_host, proxy_port = p.split(":")
    
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                    "background": {
                    "scripts": ["background.js"]
                }
            }
            """

            background_js = f"""
            var config = {{
                    mode: "fixed_servers",
                    rules: {{
                      singleProxy: {{
                        scheme: "http",
                        host: "{proxy_host}",
                        port: parseInt({proxy_port})
                      }},
                      bypassList: ["localhost"]
                    }}
                  }};
            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
            chrome.webRequest.onAuthRequired.addListener(
                function(details) {{
                    return {{
                        authCredentials: {{
                            username: "{proxy_user}",
                            password: "{proxy_pass}"
                        }}
                    }};
                }},
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );
            """
    
            plugin_file = f"plugin{random.randint(1000, 9999)}.zip"
            with zipfile.ZipFile(plugin_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
    
        except Exception as e:
            print("[WARN] Could not load proxy properly:", e)
            plugin_file = None
    
        options = Options()
        options.add_argument("--lang=en-US")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-first-run-ui")
        options.add_argument("--headless=new")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
    
        if plugin_file:
            options.add_extension(plugin_file)
    
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        })
    
        return driver

    def login(self):
        for email, password, recovery_email in self.creds:
            try:
                self.driver.get("https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3D%252F&hl=en&passive=false&service=youtube&uilel=0&ddm=1&flowName=GlifWebSignIn&flowEntry=AddSession")

                try:
                    email_input = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]'))
                    )
                    email_input.clear()
                    email_input.send_keys(email)
                    self.driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button').click()
                    print(f"Entered email: {email}")
                except Exception as e:
                    print(f"Failed to put email in {email}: {e}")
                    continue

                try:
                    pass_input = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
                    )
                    pass_input.clear()
                    pass_input.send_keys(password)
                    self.driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button').click()
                    print(f"Entered password for: {email}")
                except Exception as e:
                    print(f"Failed to put password in for {email}: {e}")
                    continue

                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div/div/form/span/section[2]/div/div/section/div/div/div/ul/li[3]/div/div[2]'))
                    ).click()
                    print(f"Recovery Step Needed {email}")

                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="knowledge-preregistered-email-response"]'))
                    ).send_keys(recovery_email)

                    self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[3]/div/div[1]/div/div/button').click()
                    print("Entered recovery email")
                except:
                    print("No recovery step")

                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="confirm"]'))
                    )
                    self.driver.find_element(By.XPATH, '//*[@id="confirm"]').click()
                except:
                    pass
                try:
                    WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/c-wiz[2]/div/div[3]/a'))
                    )
                    self.driver.find_element(By.XPATH, '/html/body/div[2]/main/c-wiz[2]/div/div[3]/a').click()
                except:
                    pass

                print(f"Logged in: {email}")

            except Exception as e:
                print(f"login error for {email}: {e}")
                continue

    def getcookies(self):
        cookies = self.driver.get_cookies()
        return "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    def loopp(self):
        def loop():
            while True:
                try:
                    new_cookie = self.getcookies()
                    self.rep(new_cookie)
                    print("Cookies refreshed.")
                except Exception as e:
                    print(e)
                time.sleep(180)

        threading.Thread(target=loop, daemon=True).start()

    def rep(self, new_cookie):
        try:
            with open("refresh.txt", "r") as f:
                l = f.readlines()
        except FileNotFoundError:
            l = []

        while len(l) <= self.index:
            l.append("\n")

        l[self.index] = new_cookie + "\n"

        with open("refresh.txt", "w") as f:
            f.writelines(l)

def split(l, n=10):
    return [l[i:i+n] for i in range(0, len(l), n)]

handled_accounts = set()
s = []

def start(group, index):
    return cookies(group, index)

def watch():
    global handled_accounts, s

    while True:
        try:
            with open("gmails.txt") as f:
                lines = [line.strip() for line in f if ":" in line or "|" in line]

            new_lines = [line for line in lines if line not in handled_accounts]

            if new_lines:
                print(f"New Acc. Logging in")
                for line in new_lines:
                    handled_accounts.add(line)

                new = split(new_lines)

                for group in new:
                    index = len(s)
                    obj = start(group, index)
                    s.append(obj)

            time.sleep(30)
        except:
            time.sleep(30)

if __name__ == "__main__":
    with open("gmails.txt") as f:
        l = [line.strip() for line in f if ":" in line or "|" in line]
    c = l
    handled_accounts.update(c)
    g = split(c)

    open("refresh.txt", "w").close()
    def threaded_cookie(group, i):
        with sem:
            obj = cookies(group, i)
            s.append(obj)


    threads = []
    for i, group in enumerate(g):
        t = threading.Thread(target=threaded_cookie, args=(group, i))
        t.start()
        threads.append(t)


    threading.Thread(target=watch, daemon=True).start()

    while True:
        time.sleep(1000000)
