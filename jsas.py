import os
import pandas as pd
from prep import indeed, monster, glassdoor

# search terms, formatted for each website. Modify in accordance with proper formatting
printed_terms=['Python Developer','Math Major','Financial Analyst','Data Analyst','Data Engineer','Business Analyst']
i_terms=['Python+Developer','Math+Major','Financial+Analyst','Data+Analyst','Data+Engineer','Business+Analyst']
m_terms=['Python-Developer','Math-Major','Financial-Analyst','Data-Analyst','Data-Engineer','Business-Analyst']
g_terms=['https://www.glassdoor.com/Job/bethpage-python-developer-jobs-SRCH_IL.0,8_IC1132187_KO9,25.htm?jobType=fulltime&fromAge=1&radius=30',
         'https://www.glassdoor.com/Job/bethpage-math-major-jobs-SRCH_IL.0,8_IC1132187_KE9,19.htm?jobType=fulltime&fromAge=1&radius=30',
         'https://www.glassdoor.com/Job/bethpage-financial-analyst-jobs-SRCH_IL.0,8_IC1132187_KO9,26.htm?jobType=fulltime&fromAge=1&radius=30',
         'https://www.glassdoor.com/Job/bethpage-data-analyst-jobs-SRCH_IL.0,8_IC1132187_KO9,21.htm?jobType=fulltime&fromAge=1&radius=30',
         'https://www.glassdoor.com/Job/bethpage-data-engineer-jobs-SRCH_IL.0,8_IC1132187_KO9,22.htm?jobType=fulltime&fromAge=1&radius=30',
         'https://www.glassdoor.com/Job/bethpage-business-analyst-jobs-SRCH_IL.0,8_IC1132187_KO9,25.htm?jobType=fulltime&fromAge=1&radius=30']

# eliminate jobs if these words are found in the job title
blacklist=['Senior','Sandwich','Cashier','Retail','Lead','Korean','VP','Director','Azure','Speech','Accountant','Tutor','Sales','Head','Advisor','Sr. ','Sr ','Summer','ecommerce','VP','Greeter','Full Stack']

# iterate over terms, returning a list of the search results from each website
# modify indeed_url, monster_url, or g_terms to adjust search filters
unfiltered_jobs = []
for i in range(len(printed_terms)):
    print(f'Searching Indeed for "{printed_terms[i]}"')
    indeed_url='https://www.indeed.com/jobs?q='+i_terms[i]+'&l=Bethpage,+NY&radius=30&jt=fulltime&explvl=entry_level&fromage=1'
    indeed1 = indeed.iJobs(indeed_url)
    indeed_jobs = indeed1.get()
    print(f'Found {len(indeed_jobs)} jobs meeting the specified criteria')
    print('----------------------------------------------')
    unfiltered_jobs.extend(indeed_jobs)

    print(f'Searching Glassdoor for "{printed_terms[i]}"...')
    glassdoor1 = glassdoor.gJobs(g_terms[i])
    glassdoor_jobs = glassdoor1.get()
    print(f'Found {len(glassdoor_jobs)} jobs meeting the specified criteria')
    print('----------------------------------------------')
    unfiltered_jobs.extend(glassdoor_jobs)

    print(f'Searching Monster for "{printed_terms[i]}"...')
    monster_url='https://www.monster.com/jobs/search/Full-Time_8?q='+m_terms[i]+'&intcid=skr_navigation_nhpso_searchMain&where=New-York__2c-NY&rad=50&tm=1'
    monster1 = monster.mJobs(monster_url)
    monster_jobs = monster1.get()
    print(f'Found {len(monster_jobs)} jobs meeting the specified criteria')
    print('----------------------------------------------')
    unfiltered_jobs.extend(monster_jobs)

# sort jobs by title and remove all duplicates
df = pd.DataFrame(unfiltered_jobs)
df.drop_duplicates(subset=['title', 'company', 'location'],keep='first',inplace=True)
df.sort_values(by=['title'],inplace=True)
df.reset_index(drop=True, inplace=True)

# remove jobs with blacklisted words in title or location out of state
to_drop = []
for i, row in df.iterrows():
    if any(bad_word in row['title'] for bad_word in blacklist) or row['location'][len(row['location']) - 2:] != 'NY':
        to_drop.append(i)
df.drop(df.index[to_drop], inplace=True)

# delete results.csv if it exists and add jobs to new results.csv
if os.path.exists('results.csv'):
    os.remove('results.csv')
df.to_csv('results.csv',index=False)

print('Job search complete! Check results.csv.')
