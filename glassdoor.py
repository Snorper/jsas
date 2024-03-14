from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup as bs
import json
import sys

import logging
logger = logging.getLogger(__name__)

with open('myConfig.json') as j:
    jsn = j.read()

try:
    cfg = json.loads(jsn)
except Exception:
    logger.exception("Error in loading json configuration")

gdUser = cfg['gdUser']
gdPass = cfg['gdPass']

import logging
logger = logging.getLogger(__name__)

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.add_argument("--window-size=1920,1080")
options.add_argument('headless')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--whitelisted-ips")

class gJobs:
    def __init__(self, city, radius, state, term: str):
        self.city = city
        self.radius = radius
        self.state = state
        self.term = term.replace(' ', '-')

    def get(self):
        def checkPopup():
            try:
                #closePopup1 = driver.find_element(By.XPATH, '//*[@id="qual_ol"]/div[1]')
                closePopup1 = driver.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/span/svg')
                closePopup2 = driver.find_element(By.XPATH, '//*[@id="JAModal"]/div/div[2]/span')
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(closePopup1)).click()
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(closePopup2)).click()
            except NoSuchElementException:
                pass

        driver = webdriver.Chrome(options=options)

        # https://www.glassdoor.com/Job/remote-software-engineer-jobs-SRCH_IL.0,6_IS11047_KO7,24.htm?fromAge=1
        glassUrl=f"https://www.glassdoor.com/Job/remote-{self.term}-jobs-SRCH_IL.0,6_IS11047_KO7,24.htm?fromAge=1"
        try:
            driver.get(glassUrl)
            checkPopup()
        except Exception:
            logger.exception('Unable to reach Glassdoor. Either Glassdoor is down or there is no internet connection')
            sys.exit(1)

        try:
            # clicking the button to show more jobs 10 times as a random estimate
            nextButton = driver.find_element(By.CSS_SELECTOR, 'button[data-test="load-more"]')
            for i in range(10):
                nextButton.click()
        except Exception:
            logger.info('Reached end of results')
        
        # Parse each page and add results to list
        glassdoor_jobs = []
        while True:
            try:
                page = driver.page_source
                page_jobs = self.__parse_index(page)
                glassdoor_jobs.extend(page_jobs)
                driver.quit()
            except Exception:
                logger.exception('Error downloading webpage')
                driver.quit()
                sys.exit(1)
            
            return glassdoor_jobs

    def __parse_index(self, htmlcontent):
        soup = bs(htmlcontent, 'lxml')

        # Find all jobs on page
        try:
            jobs_container = soup.find(attrs={"aria-label": "Jobs List"})
        except Exception:
            logger.error("Error finding jobs_container, returning empty list")
            return []

        try:
            job_items = [item.find('div') for item in jobs_container.find_all('div', class_="jobCard")]
        except Exception:
            logger.error("Error finding job items, returning empty list")
            return []

        # Get all job data from current page
        all_jobs = []
        for job_elem in job_items:
            title_elem_raw = job_elem.find('a')
            company_elem_raw = job_elem.find('div').find_all('div')[-1].find('span')
            loc_elem_raw = job_elem.find(attrs={"data-test": "emp-location"})
            url_elem_raw = job_elem.find('a')

            # Skip invalid jobs
            if None in (title_elem_raw, company_elem_raw, loc_elem_raw, url_elem_raw):
                logger.info('Skipped invalid job')
                continue

            # Clean data
            title_elem = title_elem_raw.text.strip()
            company_elem = company_elem_raw.text.strip()
            loc_elem = loc_elem_raw.text.strip()
            url_elem = url_elem_raw.get('href')

            # Append job to list as dictionary
            item = {
                "title": title_elem,
                "company": company_elem,
                "location": loc_elem,
                "href": url_elem
            }
            all_jobs.append(item)

        return all_jobs
