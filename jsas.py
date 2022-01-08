import pandas as pd
import json
import logging
import indeed, glassdoor

def main():
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(filename='jsas.log', level=level, format=fmt, filemode='w')
    logger = logging.getLogger(__name__)

    with open('config.json') as j:
        jsn = j.read()

    try:
        cfg = json.loads(jsn)
    except Exception:
        logger.exception("Error in loading json configuration")

    queries = cfg['queries']
    blacklist = cfg['blacklist']

    # iterate over queries, returning a list of the search results from each website
    i = 1
    j = len(queries)

    unfiltered_jobs = []
    for query_item in queries:
        logger.info(f'Scraping Indeed for query {i} of {j}...')
        print(f'Scraping Indeed for query {i} of {j}...')
        indeed_jobs = indeed.iJobs(**query_item).get()
        unfiltered_jobs.extend(indeed_jobs)

        logger.info(f'Scraping Glassdoor for query {i} of {j}...')
        print(f'Scraping Glassdoor for query {i} of {j}...')
        glassdoor_jobs = glassdoor.gJobs(**query_item).get()
        unfiltered_jobs.extend(glassdoor_jobs)

        i += 1

    # sort jobs by title and remove all duplicates
    print('Removing duplicate job results...')
    df = pd.DataFrame(unfiltered_jobs)
    df.drop_duplicates(subset=['title', 'company', 'location'],keep='first',inplace=True)
    df.sort_values(by=['title'],inplace=True)
    df.reset_index(drop=True, inplace=True)

    # remove jobs with blacklisted words in title
    print('Removing jobs with blacklisted terms...')
    to_drop = []
    for i, row in df.iterrows():
        if any(bad_word in row['title'] for bad_word in blacklist):
            to_drop.append(i)
    df.drop(df.index[to_drop], inplace=True)

    # Write jobs df to results.csv
    print('Writing results to results.csv...')
    df.to_csv('results.csv',index=False)

    logger.info("All jobs recorded for this session")
    print('All jobs have been recorded for this session!')

if __name__ == '__main__':
    main()
