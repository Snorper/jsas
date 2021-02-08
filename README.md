<div align="center">
  <a href="LICENSE"><img alt="License badge" src="https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge&logo=appveyor?logoWidth=0"></a>
  <a href="https://github.com/tzipor/jsas/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/tzipor/jsas?color=blueviolet&style=for-the-badge"></a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/tzipor/jsas?color=blueviolet&style=for-the-badge">
</div>

<br>

<div align="center">
  <img alt="Logo goes here" style="width: 25%; height: auto" src="logo.png">
</div>
<h1 align="center">Job Search Automation Software</h1>
<p align ="center">
  Stop wasting hours looking for a job every day!
</p>

#### Table of Contents
- [Background](#Background)
- [Requirements](#Requirements)
- [Usage](#Usage)
- [Issues and Ideas](#Issues-and-Ideas)
- [Contributing](#Contributing)
- [License](#License)
- [Terms of Service](#Terms-of-Service)

## Background
There are other projects floating around the internet which are similar to this, but none so far have provided everything I need out of a job search program. While looking for a program to use myself, I noticed a few problems:
- Nobody had automated Glassdoor searches. During my own search I discovered that Glassdoor is a bit more strict than other websites regarding automation, although I was able to get around this using Selenium.
- Available programs went no further than spewing out results in the terminal. Having the data saved for reference is a huge convenience.
- I needed to filter jobs in a specific manner due to my unique requirements. I would have to implement my own filtering method.

Thus, *JSAS* was born. Written in Python, *JSAS* currently searches Indeed, Glassdoor, and Monster for jobs. Duplicates are removed, with priority given to Indeed and then Glassdoor due to personal preference. Jobs are sorted, filtered, and returned in a CSV file. These websites tend to change their CSS and break the program, so there may be frequent updates.

## Requirements
- Requests
```
pip install requests
```
- Beautiful Soup using lxml parser
```
pip install beautifulsoup4
pip install lxml
```
- Selenium
```
pip install selenium
```
Selenium requires a driver to interface with web browsers. For Chrome, this is [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads). If you run into issues with Glassdoor and Selenium, try using ChromeDriver and following the first answer from [this Stack Overflow post](https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver).

## Usage
`jsas.py` is the only file that needs to be modified.

Searches are performed by taking terms from a list and plugging them into a URL for each website. Unfortunately and unsurprisingly, the terms must be formatted differently for all three of the currently supported websites. For indeed, terms containing multiple words must have the words separated by a plus symbol. For Monster, these terms must be hyphenated. Things get more annoying with Glassdoor. From what I've seen, the only way to make this work is for the search terms to be the entire URL, meaning a much longer list is necessary. This is because the URL sometimes changes unexpectedly once the program is run if using the method of inserting terms into a single URL. I recommend performing the searches manually once and copying the links into the list. The search terms for Indeed, Monster, and Glassdoor are respectively stored in `i_terms`, `m_terms`, and `g_terms`:
```python
i_terms=['oneword','two+words']
m_terms=['oneword','two-words']
g_terms=['https://www.glassdoor.com/Job/new-york-software-engineer-jobs-SRCH_IL.0,8_IC1132348_KO9,26.htm...']
```

By utilizing `blacklist`, jobs whose titles contain undesired terms can optionally be removed from consideration. The titles are strings, so this time terms containing multiple words can be written with spaces between those words:

```python
blacklist=['oneword', 'two words']
```

Filtering results by location, distance, and other site-specific job information is done by editing the URL before inserting the search term. This is done through `g_terms` in the case of Glassdoor, and `indeed_url` and `monster_url` for the others. I have elected to keep `glassdoor_url`, commented out, in case the complications with `g_terms` are resolved. The URL text is simple to modify due to the plain language used by these websites. Alternatively, you could perform a manual search to get a template for the URL corresponding to your needs.

```python
indeed_url='https://www.indeed.com/jobs?q='+term+'&l=Bethpage,+NY&radius=30&jt=fulltime&explvl=entry_level&fromage=1'
...
monster_url='https://www.monster.com/jobs/search/Full-Time_8?q='+term+'&intcid=skr_navigation_nhpso_searchMain&where=New-York__2c-NY&rad=50&tm=1'
...
#glassdoor_url='https://www.glassdoor.com/Job/bethpage-'+term+'-jobs-SRCH_IL.0,8_IC1132187_KO9,21.htm?jobType=fulltime&fromAge=1&radius=30'
```


Towards the end of the file, we compare each job title against the `blacklist` from earlier. At the same time, we eliminate jobs located out of state. You can replace `"NY"` with your own state, or simply remove ` or job["loc"][len(job["loc"]) - 2:] != "NY"` from the following line to include jobs from all states within your specified distance:

```python
for job in sorted_jobs:
  ...
  blacklisted = any(bad_word in job["title"] for bad_word in blacklist) or job["loc"][len(job["loc"]) - 2:] != "NY"
  ...
```

Also in the `for` loop above, Indeed results are kept over duplicate Glassdoor results, and Glassdoor results are kept over Monster results. Simply change the terms in these `if` statements if you disagree with prioritizing in this order:

```python
...
# first choice
if 'indeed' in job["href"]:
    sorted_jobs.remove(job2)
# second choice and make sure duplicate is not first choice
elif 'glassdoor' in job["href"] and 'indeed' not in job2["href"]:
    sorted_jobs.remove(job2)
else:
    sorted_jobs.remove(job)
...
```

No code beyond this point needs to be modified. The program will delete `results.csv` if it exists, and then populate a new `results.csv` with the sorted and filtered jobs. At this point `jsas.py` is done running, confirmed by the message, "Job search complete! Check results.csv" being printed to the terminal.

---

Note that the Indeed and Monster searches are done entirely in the background, but each Glassdoor search will open a browser window, navigate to the appropriate URL, and immediatelly close that window. While this slows down the program, it is necessary as Glassdoor blocks site access when using the `requests` module. Some Selenium-related warnings may appear in the terminal as well. As far as I am aware, these can be ignored.

## Issues and Ideas
- The biggest issue is that each search only returns jobs from the first page of search results. This shouldn't be an issue if you limit the search to the past 24 hours and use specific enough search terms. I'd like to avoid using Selenium to click through results for each job, as this dramatically increases the time required to perform a single search.

- Glassdoor specifically tends to give many results, but it seems like most jobs posted there do not specify an experience level and therefore we cannot reasonably use that filter.

- In one test run of the program, a single duplicate was present in the output file. This has never happened again and I am not sure why the incident occurred in the first place. Also, the current method of eliminating duplicate jobs could probably be improved, although it is not an urgent issue as long as we are limited to the first-page results.

- Ideally settings like location and distance would be determined outside of `indeed_url` and `monster_url`, and `g_terms` would be made to work with `glassdoor_url` so as to be consistent. At this point, all such settings could be moved to a separate `settings.ini` file and there would be no need for the user to touch any python files.
- Someone requested separating jobs with an "easy apply" option from others. This seems straightforward enough to implement and will likely be included in one of the first updates to the repository.
- Another feature that would ideally be included in the program is scheduling the search to be performed every 24 hours. The problem here is that these websites tend to block the program during a second run in the same window. This was tested in Windows 10 Command Prompt and PowerShell. Admittedly, I did not wait 24 hours during initial testing, so it is possible that there is no issue here. If this can be made to work, a next step is to email the search results to the user after each search for a hands-off approach.
- It is easy by design to add more job sources as desired, as long as those websites are cooperative.

## Contributing
If you are able to implement an improvement to *JSAS* and you feel so inclined, please go ahead and submit a pull request!

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Terms of Service
I do not condone using this software in cases where its use violates the terms of service of Indeed, Glassdoor, or Monster.
