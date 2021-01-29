######################################################################
# This program searches multiple websites for jobs and narrows down
# the results in accordance with site-specific filters and personal
# needs. With Python, Requests, BeautifulSoup4, and Selenium installed,
# enter "python jsas.py" in a terminal from this directory. Jobs are
# returned in results.csv. See README.md for instructions regarding
# proper usage and all other concerns.
######################################################################

import csv, os
from operator import itemgetter
from prep import indeed, monster, glassdoor

# search terms, formatted for each website. Modify in accordance with proper formatting.
i_terms=['Python','Math+Major','Financial+Analyst','Data+Analyst','Statistician']
m_terms=['Python','Math-Major','Financial-Analyst','Data-Analyst','Statistician']
g_terms=['https://www.glassdoor.com/Job/bethpage-python-jobs-SRCH_IL.0,8_IC1132187_KO9,15.htm?jobType=fulltime&fromAge=1&radius=30',
'https://www.glassdoor.com/Job/bethpage-math-major-jobs-SRCH_IL.0,8_IC1132187_KE9,19.htm?jobType=fulltime&fromAge=1&radius=30',
'https://www.glassdoor.com/Job/bethpage-financial-analyst-jobs-SRCH_IL.0,8_IC1132187_KO9,26.htm?jobType=fulltime&fromAge=1&radius=30',
'https://www.glassdoor.com/Job/bethpage-data-analyst-jobs-SRCH_IL.0,8_IC1132187_KO9,21.htm?jobType=fulltime&fromAge=1&radius=30',
'https://www.glassdoor.com/Job/bethpage-statistician-jobs-SRCH_IL.0,8_IC1132187_KO9,21.htm?jobType=fulltime&fromAge=1&radius=30']

# eliminate jobs if these words are found in the job title.
blacklist=['Senior','Sandwich','Cashier','Retail','Lead','Korean','VP','Director','Azure','Speech','Accountant','Tutor','Sales','Head','Advisor']

# don't touch these.
unfiltered_jobs = []
sorted_jobs=[]
filtered_jobs = []

# search Indeed. Modify indeed_url for search filters.
for term in i_terms:
    print(f'Searching indeed for "{term}"...')
    indeed_url='https://www.indeed.com/jobs?q='+term+'&l=Bethpage,+NY&radius=30&jt=fulltime&explvl=entry_level&fromage=1'
    indeed1 = indeed.iJobs(indeed_url)
    indeed_jobs = indeed1.get()
    print(f'Found {len(indeed_jobs)} jobs meeting the specified criteria:')
    print('------------------------------------------------------------------------------')

    unfiltered_jobs.extend(indeed_jobs)

# search Monster. Modify monster_url for search filters.
for term in m_terms:
    print(f'Searching Monster for "{term}"...')
    monster_url='https://www.monster.com/jobs/search/Full-Time_8?q='+term+'&intcid=skr_navigation_nhpso_searchMain&where=New-York__2c-NY&rad=50&tm=1'
    monster1 = monster.mJobs(monster_url)
    monster_jobs = monster1.get()
    print(f'Found {len(monster_jobs)} jobs meeting the specified criteria:')
    print('------------------------------------------------------------------------------')

    unfiltered_jobs.extend(monster_jobs)

# search Glassdoor. Modify terms in g_terms (line 8) for search filters.
for term in g_terms:
    print(f'Searching Glassdoor for "{term}"...')
    #glassdoor_url='https://www.glassdoor.com/Job/bethpage-'+term+'-jobs-SRCH_IL.0,8_IC1132187_KO9,21.htm?jobType=fulltime&fromAge=1&radius=30'
    glassdoor1 = glassdoor.gJobs(term)
    glassdoor_jobs = glassdoor1.get()
    print(f'Found {len(glassdoor_jobs)} jobs meeting the specified criteria:')
    print('------------------------------------------------------------------------------')

    unfiltered_jobs.extend(glassdoor_jobs)

# sort jobs list and remove exact duplicates.
sorted_jobs_tmp = sorted(unfiltered_jobs, key=itemgetter('title'))
for job in sorted_jobs_tmp:
    if job not in sorted_jobs:
        sorted_jobs.append(job)

# remove jobs posted on multiple websites. Prioritizes Indeed, then Glassdoor due to personal preference.
for job in sorted_jobs:
    for job2 in sorted_jobs:
        if job["title"] == job2["title"] and job["company"] == job2["company"] and job["loc"] == job2["loc"] and job["href"] != job2["href"]:
            if 'indeed' in job["href"]:
                sorted_jobs.remove(job2)
            elif 'glassdoor' in job["href"] and 'indeed' not in job2["href"]:
                sorted_jobs.remove(job2)
            else:
                sorted_jobs.remove(job)

    # finally, remove any jobs containing blacklisted words or located out of state.
    blacklisted = any(bad_word in job["title"] for bad_word in blacklist) or job["loc"][len(job["loc"]) - 2:] != "NY"
    if not blacklisted:
        filtered_jobs.append(job)

# if output exists from previous execution of jsas.py, remove. Then populate new csv with filtered results.
if os.path.exists('results.csv'):
    os.remove('results.csv')
with open('results.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=('title','company','loc','date','href'))
    writer.writeheader()
    writer.writerows(filtered_jobs)

print('Job search complete! Check results.csv.')
