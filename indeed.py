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

        # https://www.indeed.com/jobs?q=software+engineer&l=Austin%2C+TX&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&fromage=1
        indeedUrl = f"https://www.indeed.com/jobs?q={self.term}&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&fromage=1"
        
        try:
            logger.info('Getting Indeed homepage')
            driver.get(indeedUrl)
            checkPopup()
        except Exception:
            logger.exception('Unable to reach Indeed. Either Indeed is down or there is no internet connection')
            sys.exit(1)

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
                nextButton = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
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
            jobs_container = soup.find(attrs={"id": "mosaic-jobResults"})
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
            company_elem_raw = job_elem.find('span', attrs={"data-testid": "company-name"})
            loc_elem_raw = job_elem.find('div', attrs={"data-testid": "text-location"})
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
