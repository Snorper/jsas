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
- [Installation](#Installation)
- [Usage](#Usage)
- [Contributing](#Contributing)
- [License](#License)

## Summary
*Job Search Automation Software* reads job search criteria from a JSON config file and performs searches across various job posting websites. Resultant jobs are added to a list which is sorted and filtered before finally being recorded to a CSV file. A PowerShell script is provided to open all job links within the CSV file.

This software is very similar in functionality to the [Jobert API](https://github.com/jobert-app/jobert-api). The API is prioritized regarding maintenance, while this repository exists as a simpler alternative for daily use.

## Installation
Run `pip install -r requirements.txt` or individually install the necessary modules:
```
pip install beautifulsoup4
pip install lxml
pip install pandas
pip install selenium
```
Selenium requires a driver to interface with web browsers. For Chrome, this is [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads). If you run into issues with Glassdoor and Selenium, try using ChromeDriver and following the first answer from [this Stack Overflow post](https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver).

## Usage
Credentials and search criteria are taken from `config.json`. An example has been provided:

```json
{
    "gdUser": "GLASSDOOR USERNAME",
    "gdPass": "GLASSDOOR PASSWORD",
    "queries": [
        {
            "city": "New York",
            "radius": "25",
            "state": "NY",
            "term": "Software Engineer"
        },
        {
            "city": "New York",
            "radius": "25",
            "state": "NY",
            "term": "Systems Engineer"
        }
    ],
    "blacklist": [
        "Cashier",
        "Advisor"
    ]
}
```

Glassdoor login credentials are required. This program does not log into Indeed, so no other credentials are necessary. Search criteria is added to the `queries` list in the format shown. Any jobs whose titles contain items in the `blacklist` list will be removed before the program terminates.

Note that there are restrictions on acceptable `radius` values:

```Python
# Parameters allowed by radius filter on Indeed, Glassdoor
radius_options = ['0', '5', '10', '15', '25', '50', '100']
```

Run the program and `results.csv` will be created with your jobs. You can then run `jsasOpen.ps1` with PowerShell to open every link at once. It is recommended that you check how many results there are before running this.

Should the program exit with an error, a second attempt may resolve the issue. Otherwise, see `jsas.log` for debugging information.

## Contributing
Webscraping applications are fequently broken by website updates. If you are the first to notice such an event here, please feel free to open an issue or to address it and submit a pull request.

## License
All original software is distributed under the MIT License. User is bound to the Terms of Service of any other websites with which the user interacts with this software. [Developer](https://github.com/f-104) does not support Terms of Service violations.