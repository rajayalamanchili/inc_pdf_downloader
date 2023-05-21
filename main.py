import json
import re
import os
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

outputDir = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(outputDir):
    os.mkdir(outputDir)

##########################
def getAuthPage(page, url):

    # open page click login
    page.goto(url)
    with page.expect_popup() as page1_info:
        page.get_by_role("banner").get_by_role("link", name="Log in").click()
    page1 = page1_info.value

    print("Page login .... started")

    # enter login info and click submit
    page1.get_by_placeholder("Email").click()
    page1.get_by_placeholder("Email").fill(usrname)
    page1.get_by_placeholder("Email").press("Tab")
    page1.get_by_placeholder("Password").fill(passwd)
    page1.get_by_role("button", name="Log in").click()

    # TODO: add functionality to wait for page to completely load
    page1.get_by_role("heading").filter(has_text=re.compile("Policies", re.IGNORECASE)).wait_for()
    
    print("Page login .... done")

    return page1

##########################
def getPolicyDetails(auth_home_page):

    print("Extracting homepage data .... started")

    # extract policy numbers
    policy_numbers = auth_home_page.locator(".policy-number-title").all_inner_texts()
    
    # extract policy nicknames
    policy_nicknames = auth_home_page.locator(".policy-nickname").all_inner_texts()
    
    # extract premiums and periods
    policy_premiums_periods = auth_home_page.locator(".policy-info-value").all_inner_texts()
    
    # combine data
    policy_details = {"policy_numbers": policy_numbers, \
                      "policy_nicknames": [policy_nicknames[i].replace("\n","").replace(",","|") for i in range(len(policy_nicknames))], \
                      "policy_premiums": [policy_premiums_periods[i] for i in range(0,len(policy_premiums_periods),2)], \
                      "policy_periods": [policy_premiums_periods[i].replace("\xa0-\xa0","-") for i in range(1,len(policy_premiums_periods),2)]}
    
    print("Extracting homepage data .... done")

    return policy_details


##########################

def downloadPdf(auth_home_page, linkName, pdfName):
    
    ### land on polcy document page
    auth_home_page.get_by_role("link", name=linkName).click()

    ### wait till page loads
    auth_home_page.get_by_role("button", name="Policy documents").wait_for()

    ### click on document link
    with auth_home_page.expect_popup() as documentsPageInfo:
        auth_home_page.get_by_role("header")
        rowNames = auth_home_page.get_by_role("row").filter(has_text=re.compile("Effective", re.IGNORECASE)).all()
        
        # assuming only one link per row
        rowNames[0].get_by_role("link").click()
    
    documentsPage = documentsPageInfo.value
    documentsPage.get_by_role("button", name="Download").wait_for()

    ### download pdf from page
    with documentsPage.expect_download() as download_info:
        documentsPage.get_by_role("button", name="Download").click()
    
    download = download_info.value

    ### copy downloaded file to destination folder
    download.save_as(pdfName)


def downloadPolicyDetailsPDF(auth_home_page, policyDetailsDict):
    print("Downloading pdfs .... started")
    documentPageLinks = auth_home_page.get_by_label(re.compile("Get documents", re.IGNORECASE)).all()

    totalLinks = len(documentPageLinks)
    for i in range(totalLinks):
        linkName = documentPageLinks[i].get_attribute("aria-label")
        pdfName = (policyDetailsDict["policy_numbers"][i] + ".pdf").replace(" ", "_")
        pdfName = os.path.join(outputDir, pdfName)

        print("\tDownloading pdf {:d}/{:d}".format( i, totalLinks))
        downloadPdf(auth_home_page, linkName, pdfName)
    
    print("Downloading pdfs .... done")
   


##########################
def getAllPolicyDetailsDownloadPDF(page, url):

    # get autheticate page
    auth_home_page = getAuthPage(page, url)

    # extract policy details from homepage
    policyDetailsDict = getPolicyDetails(auth_home_page)

    # print(policyDetails)
    outputCSVFname = os.path.join(outputDir, "policy_details.csv")
    pd.DataFrame(policyDetailsDict).to_csv(outputCSVFname, index=False)


    # download policy details docs
    policyDetailsDict = downloadPolicyDetailsPDF(auth_home_page, policyDetailsDict)

##########################
with sync_playwright() as p:
    # browser = p.chromium.launch(downloads_path=outputDir)
    browser = p.chromium.launch()
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    getAllPolicyDetailsDownloadPDF(page, url)

    # ---------------------
    context.close()
    browser.close()