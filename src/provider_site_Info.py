""" Module for provider site related information"""
import os
import json
from playwright.async_api import async_playwright


class ProviderSiteInfo:
    """
    Class to record provider site info

    """

    config_file_name = ""
    config_data = ""
    browser = ""
    browser_context = ""

    def __init__(self, config_file_name: str):
        if self.verify_file_name(config_file_name):
            self.config_file_name = config_file_name

        self.config_data = self.get_config_file_data()

    def verify_file_name(self, file_name):
        """verify file name exists and has .json extension"""

        return os.path.exists(file_name) and os.path.splitext(file_name)[-1] == ".json"

    def get_config_file_name(self):
        """method to return config file name of provider"""

        return self.config_file_name

    def get_config_file_data(self):
        """method to return config file contents"""

        with open(self.config_file_name) as config_file:
            data = json.load(config_file)

        return data

    async def set_browser_context(self):
        """method to create browser instance"""

        playwright_instance = await async_playwright().start()
        self.browser = await playwright_instance.chromium.launch()
        self.browser_context = await self.browser.new_context(accept_downloads=True)

        return self

    async def get_url_page(self, url: str):
        """method to navigates given url"""

        # create browser and context if not already set
        if self.browser == "" or self.browser_context == "":
            await self.set_browser_context()

        # navigate to homepage
        page = await self.browser_context.new_page()
        await page.goto(url)

        return page

    async def get_homepage_login_page(self):
        """method to navigate to login from homepage"""

        # navigate to homepage
        homepage_url = self.config_data["settings"]["url"]
        homepage = await self.get_url_page(homepage_url)

        async with homepage.expect_popup() as lgin_info:
            await homepage.get_by_role("banner").get_by_role(
                "link", name="Log in"
            ).click()

        lgin_page = await lgin_info.value
        await lgin_page.wait_for_load_state("domcontentloaded")

        return lgin_page

    async def close_browser_context(self):
        """method to close browser instance"""

        if self.browser != "" or self.browser_context != "":
            await self.browser_context.close()
            await self.browser.close()

        self.browser = ""
        self.browser_context = ""

        return self
