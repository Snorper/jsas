<div align="center">
  <a href="LICENSE"><img alt="License badge" src="https://img.shields.io/badge/License-MIT-blueviolet?logoWidth=0"></a>
  <a href="https://github.com/tzipor/jsas/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/tzipor/jsas?color=blueviolet"></a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/tzipor/jsas?color=blueviolet">
</div>

<br>

<div align="center">
  <img alt="Logo goes here" style="width: 25%; height: auto" src="logo.png">
</div>
<h1 align="center">Job Search Automation Software</h1>
<p align ="center">
  Stop wasting hours on your job search every day!
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
There are other projects floating around the internet which are similar to this, but none so far have provided all of the features that I would expect in a job search program. While looking at other programs, I noticed a few problems:
- Nobody had automated Glassdoor searches. I discovered that this is because Glassdoor generally blocks Requests, although I was able to get around this using Selenium.
- Available programs went no further than spewing out results in the terminal. Having the data saved for reference is a huge convenience.
- I found that the filtering methods used by others were lacking.

Thus, *JSAS* was born. Written in Python, *JSAS* currently searches Indeed, Glassdoor, and Monster for jobs. Duplicates are removed, then jobs are sorted, filtered, and returned in a CSV file.

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
- Pandas
```
pip install pandas
```
Selenium requires a driver to interface with web browsers. For Chrome, this is [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads). If you run into issues with Glassdoor and Selenium, try using ChromeDriver and following the first answer from [this Stack Overflow post](https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver).

## Usage
`jsas.py` is the only file that needs to be modified.

Searches are performed by taking terms from a list and plugging them into a URL for each website. Unfortunately and unsurprisingly, the terms must be formatted differently for all three of the currently supported websites. For Indeed, terms containing multiple words must have the words separated by a plus symbol. For Monster, these terms must be hyphenated. Things get more annoying with Glassdoor. From what I've seen, the only way to make this work is for the search terms to be the entire URL, meaning a much longer list is necessary. I recommend performing the searches manually once and copying the links into the list. The search terms for Indeed, Monster, and Glassdoor are respectively stored in `i_terms`, `m_terms`, and `g_terms`, and `printed_terms` is the same list formatted in regular English with spaces:
```python
printed_terms=[`oneword`,`two words`]
i_terms=['oneword','two+words']
m_terms=['oneword','two-words']
g_terms=['https://www.glassdoor.com/Job/new-york-software-engineer-jobs-SRCH_IL.0,8_IC1132348_KO9,26.htm...']
```
Note that Glassdoor searches are performed using Selenium and therefore take more time than the Indeed and Monster searches.

By utilizing `blacklist`, jobs whose titles contain undesired terms can optionally be removed from consideration. The titles are strings, so this time terms containing multiple words can be written with spaces between those words:

```python
blacklist=['oneword', 'two words']
```

Filtering results by location, distance, and other site-specific job information is done by editing the URL before inserting the search term. This is done through `g_terms` in the case of Glassdoor, and `indeed_url` and `monster_url` for the others. The URL text is simple to modify, but you could perform a manual search to get a template for the URL corresponding to your needs.

```python
indeed_url='https://www.indeed.com/jobs?q='+term+'&l=Bethpage,+NY&radius=30&jt=fulltime&explvl=entry_level&fromage=1'
...
monster_url='https://www.monster.com/jobs/search/Full-Time_8?q='+term+'&intcid=skr_navigation_nhpso_searchMain&where=New-York__2c-NY&rad=50&tm=1'
```


Toward the end of the file, we compare each job title against the `blacklist` from earlier. At the same time, we eliminate jobs located out of state. You can replace `'NY'` with your own state, or simply remove ` or row['location'][len(row['location']) - 2:] != 'NY'` from the following line to include jobs from all states within your specified distance:

```python
for i, row in df.iterrows():
    if any(bad_word in row['title'] for bad_word in blacklist) or row['location'][len(row['location']) - 2:] != 'NY':
        to_drop.append(i)
```

No code beyond this point needs to be modified. The program will delete `results.csv` if it exists, and then populate a new `results.csv` with the sorted and filtered jobs. At this point `jsas.py` is done running, confirmed by the message, "Job search complete! Check results.csv" being printed to the terminal.

## Issues and Ideas
- The biggest issue is that each search only returns jobs from the first page of search results. This shouldn't be an issue if you limit the search to the past 24 hours and use specific enough search terms. I'd like to avoid using Selenium to click through results for each job, as this dramatically increases the time required to perform a single search.

- Glassdoor specifically tends to give many results, but it seems like most jobs posted there do not specify an experience level and therefore we cannot reasonably use that filter. Interestingly, there is an issue where sometimes not all Glassdoor results are returned by the program.

- Ideally settings like location and distance would be determined outside of `indeed_url` and `monster_url`, and `g_terms` would be made to work with `glassdoor_url` so as to be consistent. At this point, all such settings could be moved to a separate `settings.ini` file and there would be no need for the user to touch any python files.

## Contributing
If you are able to implement an improvement to *JSAS* and you feel so inclined, please go ahead and submit a pull request!

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Terms of Service
Use of this software not permitted in cases where its use violates the terms of service of Indeed, Glassdoor, or Monster. Users are encouraged to read the terms of service of these websites.
