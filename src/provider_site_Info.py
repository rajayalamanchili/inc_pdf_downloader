""" Module for provider site related information"""
import os
import re
import json
import pandas as pd
from playwright.async_api import async_playwright


class ProviderSiteInfo:
    """
    Class to record provider site info

    """

    config_file_name = ""
    config_data = ""
    browser = ""
    browser_context = ""
    policy_details_json = ""
    doc_details_json = ""
    output_dir = os.path.join(os.getcwd(), "data")
    policy_details_fname = os.path.join(output_dir, "policy_details.csv")

    def __init__(self, config_file_name: str):
        if self.verify_file_name(config_file_name):
            self.config_file_name = config_file_name

        # read config data from input file
        self.config_data = self.get_config_file_data()

        # create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

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
        homepage_url = self.config_data["settings"]["homepage_url"]
        homepage = await self.get_url_page(homepage_url)

        async with homepage.expect_popup() as lgin_info:
            await homepage.get_by_role("banner").get_by_role(
                "link", name="Log in"
            ).click()

        lgin_page = await lgin_info.value
        await lgin_page.wait_for_load_state("domcontentloaded")

        return lgin_page

    async def get_api_data(self, page, api_url):
        """method to capture api data when login button is clicked"""

        async with page.expect_response(
            lambda request: api_url in request.url
        ) as response_info:
            await page.get_by_role("button", name="Log in").click()
            await page.get_by_role("heading").filter(
                has_text=re.compile("Policies", re.IGNORECASE)
            ).wait_for()

        response = await response_info.value

        print(await response.json())

        return await response.json()

    async def get_policy_data(self, lgin_page):
        """method to navigate to authenticated page capture api data"""

        await lgin_page.get_by_placeholder("Email").click()
        await lgin_page.get_by_placeholder("Email").fill(
            self.config_data["secrets"]["usrname"]
        )
        await lgin_page.get_by_placeholder("Email").press("Tab")
        await lgin_page.get_by_placeholder("Password").fill(
            self.config_data["secrets"]["pwd"]
        )

        # get api data
        self.policy_details_json = await self.get_api_data(
            lgin_page, self.config_data["settings"]["policy_details_api"]
        )

        return self

    async def close_browser_context(self):
        """method to close browser instance"""

        if self.browser != "" or self.browser_context != "":
            await self.browser_context.close()
            await self.browser.close()

        self.browser = ""
        self.browser_context = ""

        return self

    def extract_save_policy_details(self):
        """save selected policy details to csv file"""

        json_data = self.policy_details_json

        dwellings_data = [
            policy["dwellings"] for policy in json_data["result"]["policies"]
        ]

        output_dict = {
            "number": [policy["number"] for policy in json_data["result"]["policies"]],
            "nickName": [
                policy["nickName"] for policy in json_data["result"]["policies"]
            ],
            "annualPremium": [
                policy["annualPremium"] for policy in json_data["result"]["policies"]
            ],
            "term": [policy["term"] for policy in json_data["result"]["policies"]],
            "policyType": [
                policy["policyType"] for policy in json_data["result"]["policies"]
            ],
            "companyName": [
                policy["companyName"] for policy in json_data["result"]["policies"]
            ],
            "addressLine1": [address[0]["addressLine1"] for address in dwellings_data],
            "addressLine2": [address[0]["addressLine2"] for address in dwellings_data],
            "city": [address[0]["city"] for address in dwellings_data],
            "state": [address[0]["state"] for address in dwellings_data],
            "zipCode": [address[0]["zipCode"] for address in dwellings_data],
        }

        pd.DataFrame(output_dict).to_csv(self.policy_details_fname, index=False)
