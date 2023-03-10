#import required modules
import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from lxml import html
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import openpyxl

#GET JOB POSTING DETAILS
# Obtain the version of ChromeDriver compatible with the browser being used
driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#URL for scraping
url = 'https://www.linkedin.com/jobs/search/?currentJobId=3480661601&geoId=101174742&keywords=Data%20Analyst&location=Canada'
driver.get(url)
driver.maximize_window()
sleep(2)
#Scroll down the page
for _ in range(6):
    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
    sleep(3)

# Click on the "See more jobs" button 10 times and scroll down after each click
for _ in range(10):
    driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/button').click()
    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
    sleep(3)
    
src = driver.page_source
driver.close()

# Get the html source
soup = BeautifulSoup(src, 'lxml')

result_nodes = soup.select('ul[class = "jobs-search__results-list"] li')
print("Number of jobs: ", len(result_nodes))

#Get the job posting detail and put it in a DataFrame
job_posting_data = pd.DataFrame(columns=["Job title", "Job link", "Company name", "Company link",
                                         "Job location", "Job list date", "Time elapsed"])

for idx, node in enumerate (result_nodes):
    # Extracting job link
    card_link = node.find('a', {'class': 'base-card__full-link'})
    try:
        job_link = card_link.get('href')
    except:
        print(idx)
        print(result_nodes[idx])
        continue
    
    # Extracting the job title
    card_title = node.find('h3')
    job_title = card_title.get_text().strip()

    # Extracting Company name and company link
    card_subtitle = node.find('a', {'class': 'hidden-nested-link'})

    company_name = card_subtitle.text.strip()
    company_link = card_subtitle.get('href')
  
    # Extracting job location
    card_location = node.find_all('span')
    job_location = card_location[1].get_text().strip()
    
    # Posting date
    card_list_date = node.find('time')
    job_datetime = card_list_date['datetime']
    time_elapsed = card_list_date.get_text().strip()
    
    df1 = pd.DataFrame.from_records([{"Job title": job_title,
                                      "Job link": job_link,
                                      "Company name": company_name,
                                      "Company link": company_link,
                                      "Job location": job_location,
                                      "Job list date": job_datetime,
                                      "Time elapsed": time_elapsed}])
    
    # Put the result into a DataFrame
    job_posting_data = pd.concat([job_posting_data, df1], ignore_index=True)
# Export to an Excel file
job_posting_data.to_excel("output.xlsx", sheet_name='Job Posting')

# Get more detail about the jobs (test for 10 companies)
df_10 = job_posting_data.head(10)
job_level = []
job_type = []
job_detail = []
for job_url in job_posting_data["Job link"].iloc[0:10]:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(job_url)
    driver.maximize_window()
    sleep(2)
    job_src = driver.page_source
    driver.close()
    # Now using beautiful soup
    job_soup = BeautifulSoup(job_src, 'lxml')
    job_nodes = job_soup.select('div[class = "decorated-job-posting__details"] section div')[0]
    # Get job level and job type
    card_level = job_nodes.find_all('span', {'class': 'description__job-criteria-text'})
    if len(card_level) < 2:
        j_level = "N/A"
        j_type = card_level[0].get_text().strip()
    else:
        j_level = card_level[0].get_text().strip()
        j_type = card_level[1].get_text().strip()
    job_level.append(j_level)
    job_type.append(j_type)
    # Get job detail
    j_detail = job_nodes.select('div[class= "show-more-less-html__markup show-more-less-html__markup--clamp-after-5"]')[0].get_text().strip()
    job_detail.append(j_detail)

# Add three columns into the result DataFrame
df_10["Job level"] = job_level
df_10["Job type"] = job_type
df_10["Job detail"] = job_detail
# Export to an Excel file
df_10.to_excel("output_first_10_companies.xlsx", sheet_name='Job Posting')
