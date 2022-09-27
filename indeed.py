from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as bs
import sys

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

class iJobs:
    def __init__(self, city, radius, state, term):
        self.city = city
        self.radius = radius
        self.state = state
        self.term = term

    def get(self):
        def checkPopup():
            try:
                closePopup = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/button')
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(closePopup)).click()
            except NoSuchElementException:
                pass

        driver = webdriver.Chrome(options=options)
        
        try:
            logger.info('Getting Indeed homepage')
            driver.get("https://indeed.com")
            checkPopup()
        except Exception:
            logger.exception('Unable to reach Indeed. Either Indeed is down or there is no internet connection')
            sys.exit(1)

        attempts = 10
        for k in range(attempts):
            logger.info("""Attempting Indeed job search with the following criteria:
                                 Search Term: {term}
                                 Location: {city}, {state}
                                 Radius: {radius} miles""".format(term=self.term, city=self.city, state=self.state, radius=self.radius))
            try:
                # Search for current job term
                termInputArea = driver.find_element(By.XPATH, '//*[@id="text-input-what"]')
                termInputArea.send_keys(Keys.CONTROL, "a")
                termInputArea.send_keys(self.term)
                termInputArea.send_keys(Keys.ENTER)
                checkPopup()
                logger.info(f'Searched for {self.term}')

                # Search for current job location
                cityInput = self.city + ", " + self.state
                cityInputArea = driver.find_element(By.XPATH, '//*[@id="text-input-where"]')
                cityInputArea.send_keys(Keys.CONTROL, "a")
                cityInputArea.send_keys(cityInput)
                cityInputArea.send_keys(Keys.ENTER)
                checkPopup()
                logger.info(f'Filtered for {self.city}, {self.state}')

                # Filter for remote only
                
                remote = driver.find_element(By.XPATH, '//*[@id="filter-remotejob"]')
                remote.click()
                checkPopup()
                remoteYes = driver.find_element(By.XPATH, '//*[@id="filter-remotejob-menu"]/li[1]')
                remoteYes.click()
                checkPopup()
                logger.info('Filtered for remote jobs only')

                # Apply radius filter, only get results from last day
                current_url = driver.current_url
                new_url = current_url + "&radius=" + self.radius + "&fromage=1"

                driver.get(new_url)
                checkPopup()
                logger.info(f'Filtered for radius of {self.radius} miles and jobs posted in last day')
            except Exception:
                if k < attempts - 1:
                    logger.warning(f'Selenium error: failed attempt {k + 1} of {attempts}, trying again')
                    continue
                else:
                    logger.exception('Failed to navigate website using Selenium, XPATH of one or more elements has likely changed')
                    print('Failed to navigate website using Selenium, XPATH of one or more elements has likely changed.')
                    sys.exit(1)
            break

        # Parse each page and add results to list
        indeed_jobs = []
        while True:
            try:
                page = driver.page_source
                page_jobs = self.__parse_index(page)
                indeed_jobs.extend(page_jobs)
            except Exception:
                logger.exception('Error downloading webpage')
                sys.exit(1)

            try:
                nextButton = driver.find_element(By.XPATH, '//*[@id="resultsCol"]/nav/div/ul/li[4]/a')
                nextButton.click()
                logger.info(f'Clicked button {nextButton} to reach next page')
            except Exception:
                logger.info('Reached end of results')
                driver.quit()
                return indeed_jobs

    def __parse_index(self, htmlcontent):
        soup = bs(htmlcontent, 'lxml')

        # Find all jobs on page
        try:
            jobs_container = soup.find(attrs={"id": "mosaic-provider-jobcards"})
            logger.info(f'jobs_container: {jobs_container}')
        except Exception:
            logger.error("Error finding jobs_container, returning empty list")
            return []

        try:
            job_items = jobs_container.find_all('div', class_='resultWithShelf')
            logger.info(f'job_items: {job_items}')
        except Exception:
            logger.error("Error finding job items, returning empty list")
            return []

        # Get all job data from current page
        all_jobs = []
        for job_elem in job_items:
            title_elem_raw = job_elem.find('h2', class_='jobTitle')
            company_elem_raw = job_elem.find('span', class_='companyName')
            loc_elem_raw = job_elem.find('div', class_='companyLocation')
            url_elem_raw = job_elem.find('a', class_='jcs-JobTitle').get('href')
            logger.info("""Found raw job result:
                                 Position: {title}
                                 Company: {company}
                                 Location: {location}
                                 Link: {link}""".format(title=title_elem_raw,company=company_elem_raw,location=loc_elem_raw,link=url_elem_raw))

            # Skip invalid jobs
            if None in (title_elem_raw, company_elem_raw, loc_elem_raw, url_elem_raw):
                logger.info("Skipped invalid job")
                continue

            # Clean data
            title_elem = title_elem_raw.text.lstrip('full details of ')
            company_elem = company_elem_raw.text.strip()
            loc_elem = loc_elem_raw.text.strip()
            url_elem = f'https://indeed.com{url_elem_raw}'

            # Append job to list as dictionary
            item = {
                "title": title_elem,
                "company": company_elem,
                "location": loc_elem,
                "href": url_elem
            }
            all_jobs.append(item)
            logger.info(f'Added parsed job result to all_jobs: {item}')

        return all_jobs
