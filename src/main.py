import os
import asyncio
from provider_site_Info import ProviderSiteInfo

CONFIG_FILE_NAME = os.path.join(os.getcwd(), "config.json")


async def main():
    """main function to start app"""
    # create borwser and browser context
    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)

    # navigate to login from homepage
    lgin_page = await provider_obj.get_homepage_login_page()
    await provider_obj.get_policy_data(lgin_page)

    provider_obj.extract_save_policy_details()


asyncio.run(main())
