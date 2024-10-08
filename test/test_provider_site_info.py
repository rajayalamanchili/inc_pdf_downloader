import os
import re
import pytest
import asyncio
import validators
from src.provider_site_Info import ProviderSiteInfo
from playwright.async_api import expect

CONFIG_FILE_NAME = os.path.join(os.getcwd(), "config.json")


@pytest.fixture
def test_verify_config_file_exists():
    """Test to verify if config file is exists and has .json extension"""

    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)
    provider_config_file = provider_obj.get_config_file_name()

    # verify file exists
    assert os.path.exists(provider_config_file)

    # verify file extension is .json
    assert os.path.splitext(provider_config_file)[-1] == ".json"

    return provider_obj


def test_verify_config_file_contents(test_verify_config_file_exists):
    """Test to verify config file has required contents"""

    assert test_verify_config_file_exists

    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)
    provider_config_data = provider_obj.config_data

    # verify if url fields exists and is valid
    assert validators.url(provider_config_data["settings"]["homepage_url"])

    # verify secrets available and not empty
    assert validators.url(provider_config_data["secrets"]["usrname"]) != ""
    assert validators.url(provider_config_data["secrets"]["pwd"]) != ""


async def test_browser_homepage():
    """Test to browser instance is created"""

    # create borwser and browser context
    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)
    homepage_url = provider_obj.config_data["settings"]["homepage_url"]

    # navigate to homepage
    page = await provider_obj.get_url_page(homepage_url)

    # verify if home page has correct title
    await expect(page).to_have_title(re.compile("Safeco.*"))

    # close browser and browser context
    await provider_obj.close_browser_context()


async def test_homepage_to_login():
    """Test to navigate to login from homepage"""

    # create borwser and browser context
    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)

    # navigate to login from homepage
    page = await provider_obj.get_homepage_login_page()

    # verify if login page has correct url
    await expect(page).to_have_url(re.compile("login.*"))

    # close browser and browser context
    await provider_obj.close_browser_context()


async def test_get_policy_data():
    """Test to navigate to login from homepage"""

    # create borwser and browser context
    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)

    # navigate to login from homepage
    lgin_page = await provider_obj.get_homepage_login_page()
    await provider_obj.get_policy_data(lgin_page)

    # verify if details are captured
    print(provider_obj.policy_details_json)

    # close browser and browser context
    await provider_obj.close_browser_context()


async def test_save_policy_data():
    """Test to navigate to login from homepage"""

    # create borwser and browser context
    provider_obj = ProviderSiteInfo(CONFIG_FILE_NAME)

    # navigate to login from homepage
    lgin_page = await provider_obj.get_homepage_login_page()
    await provider_obj.get_policy_data(lgin_page)

    provider_obj.extract_save_policy_details()

    assert os.path.exists(provider_obj.policy_details_fname)

    # close browser and browser context
    await provider_obj.close_browser_context()


# test_verify_config_file_contents(test_verify_config_file_exists)
asyncio.run(test_save_policy_data())
