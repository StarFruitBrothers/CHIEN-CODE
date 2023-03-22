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


SESSIONS_URL = "https://ca.indeed.com/"

def run():
    # Obtain the version of ChromeDriver compatible with the browser being used
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    get_job_page(driver, "data","Canada")
    sleep(2)

    #Get the data for the first page
    job_posting_data = get_links(driver)

    # Click on the "Next page" button 10 times and get data for each page
    while True:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="css-tvvxwd ecydgvn1"]/a[contains(@aria-label,"Next Page")]'))).click()
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            sleep(3)
            data = get_links(driver)
            print(f'- Num records: {len(data.index)}')
            job_posting_data = pd.concat([job_posting_data, data])
        except:
            print('We have reached to the end!!!')
            break
    driver.close()
    print(len(job_posting_data.index))
    job_posting_data.reset_index(inplace = True, drop = True)

    # Export to an Excel file
    job_posting_data.to_excel("output.xlsx", sheet_name='Job Posting')


def get_job_page(driver, job_title, job_location):

    # Open the website to be scraped
    driver.get(SESSIONS_URL)
    wait = WebDriverWait(driver, 10)
    get_url = driver.current_url
    wait.until(EC.url_to_be(SESSIONS_URL))
    if get_url == SESSIONS_URL:
        # Put the job title, keywords, or company in to the search bars
        what_search = driver.find_element(By.ID,"text-input-what")
        what_search.clear()
        what_search.send_keys(job_title)
        what_search.send_keys(Keys.TAB)
        # Input where search bar
        where_search = driver.find_element(By.XPATH, '// *[ @ id = "text-input-where"]')
        where_search.send_keys(Keys.CONTROL, 'a')
        where_search.send_keys(Keys.DELETE)
        where_search.send_keys(job_location)
        where_search.send_keys(Keys.TAB)
        # Press the "Find jobs" button
        driver.find_element(By.XPATH, '//*[@id="jobsearch"]/button').click()

    # Maximize window
    driver.maximize_window()




# Get preliminary job infos and links
def get_links(driver):
    root = html.fromstring(driver.page_source)
    result_nodes = root.xpath('//ul[@class="jobsearch-ResultsList css-0"]/li')
    result = []
    for result_node in result_nodes:
        company_name = result_node.xpath("string(.//span[@class = 'companyName'])").strip()
        job_link = result_node.xpath("string(.//td[@class = 'resultContent']/div/h2/a/@href)")
        job_title = result_node.xpath("string(.//td[@class = 'resultContent']/div/h2/a)").strip()
        job_location = result_node.xpath("string(.//div[@class = 'companyLocation'])").strip()
        job_datetime = result_node.xpath("string(.//span[@class = 'date']/text())").strip()

        if company_name!="":
            result.append({
                "JOB TITLE": job_title,
                "COMPANY NAME": company_name,
                "JOB LINK": f"https://ca.indeed.com{job_link}",
                "LOCATION": job_location,
                "JOB LIST DATE" : job_datetime
            })
        df_result = pd.DataFrame.from_dict(result)
    return df_result


if __name__ == '__main__':
    run()
