# sudo apt-get update
# sudo apt install python3-pip -y
# sudo pip install pytest-playwright
# sudo playwright install
# sudo playwright install-deps

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://playwright.dev")
    print(page.title())
    browser.close()

    