"""script to start the application
    input: .json file
    output: files saved to "data" folder
"""

import sys
import asyncio
from provider_site_Info import ProviderSiteInfo


async def main(config_file_name):
    """main function to start app"""
    # create borwser and browser context
    provider_obj = ProviderSiteInfo(config_file_name)

    # navigate to login from homepage
    lgin_page = await provider_obj.get_homepage_login_page()
    await provider_obj.get_policy_data(lgin_page)

    provider_obj.extract_save_policy_details()

    # close browser and browser context
    await provider_obj.close_browser_context()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(main(sys.argv[1]))
    else:
        print("Provide an input .json file with format mentioned in document")
