from selenium import webdriver
from bs4 import BeautifulSoup
import sys

from prep.helpers import HttpHelpers

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.add_argument('headless')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

class gJobs:
    def __init__(self, url):
        self.url = url
        self.helpers = HttpHelpers()

    def get(self):
        driver = webdriver.Chrome(options=options)
        html = driver.get(self.url)
        page = driver.page_source
        driver.quit()

        if page is None:
            sys.exit('Error downloading webpage')

        glassdoor_jobs = self.__parse_index(page)

        return glassdoor_jobs

    def __parse_index(self, htmlcontent):
        soup = BeautifulSoup(htmlcontent, 'lxml')
        jobs_container = soup.find(attrs={"data-test": "jlGrid"})
        if jobs_container is None:
            return []
        
        job_items = jobs_container.find_all(class_='react-job-listing')

        if job_items is None or len(job_items) == 0:
            return []

        all_jobs = []

        for job_elem in job_items:
            url_elem = job_elem.find('a', class_='jobLink')
            title_elem = job_elem.find('a', class_='jobLink job-search-key-1rd3saf eigr9kq1')
            company_elem = job_elem.find('a', class_='job-search-key-l2wjgv e1n63ojh0 jobLink')
            loc_elem = job_elem.find('span', class_='css-1buaf54 pr-xxsm job-search-key-iii9i8 e1rrn5ka4')

            if None in (title_elem, company_elem, url_elem, loc_elem):
                continue

            href = url_elem.get('href')
            if href is None:
                continue

            item = {
                "title" : title_elem.text.strip(),
                "company" : company_elem.text.strip(),
                "location" : loc_elem.text.strip(),
                "href" : f'https://www.glassdoor.com{href}'
            }
            all_jobs.append(item)

        return all_jobs
