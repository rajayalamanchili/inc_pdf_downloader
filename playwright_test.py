# sudo apt-get update
# sudo apt install python3-pip -y
# sudo pip install pytest-playwright
# sudo playwright install
# sudo playwright install-deps
# sudo pip install pandas
import re
import asyncio
from playwright.async_api import async_playwright


async def handle_response(response):
    if "api/products" in response.url:
        print(await response.json())


async def get_prod_vals_from_page(page):
    await page.goto("https://bstackdemo.com/", wait_until="networkidle")

    await page.get_by_role("link", name="Sign In").click()
    await page.locator("div").filter(has_text=re.compile(r"^Select Username$")).nth(
        2
    ).click()
    await page.get_by_text("demouser", exact=True).click()
    await page.locator("div").filter(has_text=re.compile(r"^Select Password$")).nth(
        2
    ).click()
    await page.get_by_text("testingisfun99", exact=True).click()

    # # page.on("response", handle_response)

    async with page.expect_response(
        lambda request: "/api/products" in request.url
    ) as response_info:
        await page.get_by_role("button", name="Log In").click()
        await page.get_by_text("Logout").wait_for()

    response = await response_info.value

    print(await response.json())

    # # await page.get_by_role("button", name="Log In").click()

    print(await page.title())

    total_products = (
        await page.locator(".shelf-container").locator(".shelf-item").count()
    )
    print("Total products: ", total_products)
    for prod in range(total_products):
        prod_title = (
            await page.locator(".shelf-container")
            .locator(".shelf-item")
            .locator(".shelf-item__title")
            .nth(prod)
            .all_inner_texts()
        )
        prod_price = (
            await page.locator(".shelf-container")
            .locator(".shelf-item")
            .locator(".shelf-item__price")
            .nth(prod)
            .locator(".val")
            .all_inner_texts()
        )

        print(str(prod + 1) + "\t" + str(prod_title[0]) + "\t" + str(prod_price[0]))


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await get_prod_vals_from_page(page)

        await browser.close()


asyncio.run(main())
