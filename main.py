import json
import re
import pandas as pd
from playwright.sync_api import sync_playwright, expect


## get config data
config_filename = "config.json"

def get_config(filename):

    try:
       with open(filename) as f:
           data = json.load(f)
           return data
    except Exception as e:
        print("Error: ", e)

config_data = get_config(config_filename)


url = config_data["settings"]["url"]
usrname = config_data["secrets"]["usrname"]
passwd = config_data["secrets"]["pwd"]

##########################
def getAuthPage(page, url):

    # open page click login
    page.goto(url)
    with page.expect_popup() as page1_info:
        page.get_by_role("banner").get_by_role("link", name="Log in").click()
    page1 = page1_info.value

    # enter login info and click submit
    page1.get_by_placeholder("Email").click()
    page1.get_by_placeholder("Email").fill(usrname)
    page1.get_by_placeholder("Email").press("Tab")
    page1.get_by_placeholder("Password").fill(passwd)
    page1.get_by_role("button", name="Log in").click()

    # TODO: add functionality to wait for page to completely load
    # expect(page1.get_by_role("heading").filter(has_text=re.compile("Hi there*", re.IGNORECASE))).to_have_count(1)
    # print("Page opened with welcome message")

    return page1

def getPolicyDetails(auth_home_page):

    # extract policy numbers
    policy_numbers = auth_home_page.locator(".policy-number-title").all_inner_texts()
    
    # extract policy nicknames
    policy_nicknames = auth_home_page.locator(".policy-nickname").all_inner_texts()
    
    # extract premiums and periods
    policy_premiums_periods = auth_home_page.locator(".policy-info-value").all_inner_texts()
    
    # combine data
    policy_details = {"policy_numbers": policy_numbers, \
                      "policy_nicknames": policy_nicknames, \
                      "policy_premiums": [policy_premiums_periods[i] for i in range(0,len(policy_premiums_periods),2)], \
                      "policy_periods": [policy_premiums_periods[i].replace("\xa0-\xa0","-") for i in range(1,len(policy_premiums_periods),2)]}

    return policy_details



# def downloadPolicyDetailsPDF(auth_home_page):
   


def getAllPolicyDetailsDownloadPDF(page, url):

    # get autheticate page
    auth_home_page = getAuthPage(page, url)

    # extract policy details from homepage
    policyDetailsDict = getPolicyDetails(auth_home_page)

    # print(policyDetails)
    pd.DataFrame(policyDetailsDict).to_csv("policy_details.csv")


    # # download policy details docs
    # policyDetailsDict = downloadPolicyDetailsPDF(auth_home_page)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()

    getAllPolicyDetailsDownloadPDF(page, url)

    # ---------------------
    context.close()
    browser.close()