<div align="center">
  <img alt="Logo goes here" style="width: 25%; height: auto" src="logo.png">
</div>
<h1 align="center">Job Search Automation Software</h1>

<div align="center">
  <a href="LICENSE"><img alt="License badge" src="https://img.shields.io/badge/License-MIT-blueviolet?logoWidth=0"></a>
  <a href="https://github.com/tzipor/jsas/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/tzipor/jsas?color=blueviolet"></a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/tzipor/jsas?color=blueviolet">
</div>

#### Table of Contents
- [Summary](#Summary)
- [Requirements](#Requirements)
- [Usage](#Usage)
- [Issues and Ideas](#Issues-and-Ideas)
- [Contributing](#Contributing)
- [License](#License)
- [Terms of Service](#Terms-of-Service)

## Summary
There are other job search programs on the internet, but as far as I am aware none of them search Glassdoor or provide a usable output. *JSAS* addresses both concerns. The software searches Indeed and Glassdoor based on user-defined criteria, sorts and filters results, removes duplicates, and returns the final list in a CSV file.

## Requirements
You can `pip install -r requirements.txt` or individually install the necessary modules:
```
pip install requests
pip install beautifulsoup4
pip install lxml
pip install selenium
pip install pandas
pip install ltoml
```
Selenium requires a driver to interface with web browsers. For Chrome, this is [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads). If you run into issues with Glassdoor and Selenium, try using ChromeDriver and following the first answer from [this Stack Overflow post](https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver).

## Usage
`example.toml` is the only file that needs to be modified. First, change its name to `config.toml` so that the program will recognize your configuration.

Searches are performed by taking terms from a list and plugging them into a URL for each website. Unfortunately and unsurprisingly, the terms must be formatted differently for each of the currently supported websites. For Indeed, terms containing multiple words must have the words separated by a plus symbol. Things get more annoying with Glassdoor. From what I've seen, the only way to make this work is for the search terms to be the entire URL, meaning a much longer list is necessary. I recommend performing the searches manually once and copying the links into the list. The search terms for Indeed  and Glassdoor are respectively stored in `i_terms` and `g_terms`, and `p_terms` is the same list formatted in regular English with spaces:
```toml
p_terms=["oneword","two words"]
i_terms=["oneword","two+words"]
g_terms=["https://www.glassdoor.com/Job/new-york-software-engineer-jobs-SRCH_IL.0,8_IC1132348_KO9,26.htm..."]
```
Note that Glassdoor searches are performed using Selenium and therefore take more time than Indeed searches.

By utilizing `blacklist`, jobs whose titles contain undesired terms can optionally be removed from consideration. The titles are strings, so this time terms containing multiple words can be written with spaces between those words:

```toml
blacklist=["oneword", "two words"]
```

Filtering results by location, distance, and other site-specific job information is done by editing the URL before inserting the search term. This is done through `g_terms` in the case of Glassdoor and `i_string` for Indeed. `i_string` is simple enough to modify, but you could perform a manual search to get a template for the URL corresponding to your needs. Each Glassdoor URL should be individually created by doing a manual search once.

```toml
i_string = "&l=Bethpage,+NY&radius=30&jt=fulltime&explvl=entry_level&fromage=1"
```

To filter for jobs only located in your state, modify `state` with your own state's abbreviation and set the boolean value to `true`. To ignore this condition, set the boolean value to `false`.
```toml
state = [
  "NY",
  true
]
```

Run the program and `results.csv` will be created with your jobs. You can then run `jsasOpen.ps1` with PowerShell to open every link at once. It is highly suggested that you check how many results there are and maybe trim them down a bit before running this.

## Issues and Ideas
- The biggest issue is that each search only returns jobs from the first page of search results. This shouldn't be a problem if you limit the search to the past 24 hours and use specific enough search terms. I'd like to avoid using Selenium to click through results for each job, as this dramatically increases the time required to perform a single search.

- Glassdoor specifically tends to give many results, but it seems like most jobs posted there do not specify an experience level and therefore we cannot reasonably use that filter.

## Contributing
Pull requests welcome, especially concerning iterating over search result pages.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Terms of Service
Use of this software not permitted in cases where its use violates the terms of service of another website. Users are encouraged to read the terms of service of such a website.
