# sudo apt-get update
# sudo apt install python3-pip -y
# sudo pip install pytest-playwright
# sudo playwright install
# sudo playwright install-deps

from playwright.sync_api import sync_playwright

def get_prod_vals_from_page(page):
    page.goto("https://bstackdemo.com/")
    
    print(page.title())

    total_products = page.locator(".shelf-container").locator(".shelf-item").count()
    print("Total products: ", total_products)
    for prod in range(total_products):
        prod_title = page.locator(".shelf-container").locator(".shelf-item").locator(".shelf-item__title").nth(prod).all_inner_texts()[0]
        prod_price = page.locator(".shelf-container").locator(".shelf-item").locator(".shelf-item__price").nth(prod).locator(".val").all_inner_texts()[0]

        print(str(prod+1) + "\t" + str(prod_title) + "\t" + str(prod_price))

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    get_prod_vals_from_page(page)

    browser.close()

    