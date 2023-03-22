# Import required modules
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
import pandas as pd
import numpy as np


INPUT_LINK_FILE = "output.xlsx"

# Open the link in the driver and get all info
def get_session_info(driver):
    # Open and load Excel file that contains link and some basic info for the session
    infos = pd.read_excel(INPUT_LINK_FILE, sheet_name = 0, header=0, index_col=False, keep_default_na=True)
    data = []
    # Loop through all links
    for i in range(len(infos.index)):
        url = infos.loc[i, "JOB LINK"]
        job_title = infos.loc[i, "JOB TITLE"]
        company_name = infos.loc[i, "COMPANY NAME"]
        location = infos.loc[i, "LOCATION"]
        job_listdate = infos.loc[i, "JOB LIST DATE"]
        driver.get(url)
        print(url)
        sleep(2)
        # Get main session data
        session_data = get_session_data(driver.page_source, url, job_title, company_name, location, job_listdate)
        data.append(session_data)
    return data

# Get main session data
def get_session_data(page_source, job_link, job_title, company_name, location, job_listdate):
    root = html.fromstring(page_source)
    job_type = root.xpath("string(.//div[@id='jobDetailsSection']/div/div[text()[contains(.,'Job type')]]/following-sibling::div)").strip()
    job_details = root.xpath("string(.//div[@id='jobDescriptionText'])").replace("\n", " ").strip()
    company_link = root.xpath("string(.//div[@data-company-name ='true']/a/@href)").strip()

    data = {
        "JOB TITLE": job_title,
        "JOB TYPE": job_type,
        'COMPANY': company_name,
        'COMPANY LINK': company_link,
        'LOCATION': location,
        'JOB DETAILS': job_details,
        'JOB LINK': job_link,
        'LIST DATE': job_listdate
    }
    return data


# Write data to excel files to avoid re rerunning the script multiple times
def output_session_to_file(data):
    df_result = pd.DataFrame.from_dict(data)
    # Export to an Excel file
    df_result.to_excel("job_posting_output.xlsx", sheet_name='Job Posting')




def run():
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    data = get_session_info(driver)
    print(f'- Num records: {len(data)}')
    output_session_to_file(data)
    driver.close()


if __name__ == '__main__':
    run()