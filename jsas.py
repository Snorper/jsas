import pandas as pd
import tomli
from prep import indeed, glassdoor

with open('config.toml') as t:
    tml = t.read()

try:
    cfg = tomli.loads(tml)
except tomli.TOMLDecodeError:
    print("F")

# search criteria from config.toml
printed_terms = cfg['p_terms']
i_terms = cfg['i_terms']
i_string = cfg['i_string']
g_terms = cfg['g_terms']
state = cfg['state'][0]
stateBool = cfg['state'][1]

# eliminate jobs if these words are found in the job title
blacklist = cfg['blacklist']

# iterate over terms, returning a list of the search results from each website
# modify indeed_url, or g_terms to adjust search filters
unfiltered_jobs = []
for i in range(len(printed_terms)):
    print(f'Searching Indeed for "{printed_terms[i]}"')
    indeed_url='https://www.indeed.com/jobs?q='+i_terms[i]+i_string
    indeed1 = indeed.iJobs(indeed_url)
    indeed_jobs = indeed1.get()
    print(f'Found {len(indeed_jobs)} jobs meeting the specified criteria')
    print('----------------------------------------------')
    unfiltered_jobs.extend(indeed_jobs)

# fix this after Indeed

    #print(f'Searching Glassdoor for "{printed_terms[i]}"...')
    #glassdoor1 = glassdoor.gJobs(g_terms[i])
    #glassdoor_jobs = glassdoor1.get()
    #print(f'Found {len(glassdoor_jobs)} jobs meeting the specified criteria')
    #print('----------------------------------------------')
    #unfiltered_jobs.extend(glassdoor_jobs)

# sort jobs by title and remove all duplicates
df = pd.DataFrame(unfiltered_jobs)
df.drop_duplicates(subset=['title', 'company', 'location'],keep='first',inplace=True)
df.sort_values(by=['title'],inplace=True)
df.reset_index(drop=True, inplace=True)

# remove jobs with blacklisted words in title or location out of state
to_drop = []
for i, row in df.iterrows():
    if any(bad_word in row['title'] for bad_word in blacklist) or (row['location'][len(row['location']) - 2:] != state and stateBool == True):
        to_drop.append(i)
df.drop(df.index[to_drop], inplace=True)

# Write jobs df to results.csv
df.to_csv('results.csv',index=False)

print('Job search complete! Check results.csv.')
