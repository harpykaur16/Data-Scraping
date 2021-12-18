
'''This script is geting top repositories and stroring information in csv files.'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
 
def parse_star_count(stars_str):
    stars_str= stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1]) * 1000)
    return int(stars_str)

def get_repo_info(h3_tag, star_tag):
    #returns all required info about a repository
    a_tags= h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url= base_url + a_tags[1]['href']
    stars= parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url

def get_topic_repos(topic_url):
    #Download the page
    response= requests.get(topic_url)
    #check succesful response
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    #parsing using Beautiful Soup
    topic_doc= BeautifulSoup(response.text, 'html.parser')
    #get h3 tags containing repo title, repo URL and username
    h3_selection_class= 'f3 color-fg-muted text-normal lh-condensed'
    repo_tags = topic_doc.find_all('h3', {'class': h3_selection_class })
    #get star tags
    star_tags = topic_doc.find_all('span',{ 'class': 'Counter js-social-count'} )

    topic_repos_dict= {
    'username':[],
    'repo_name':[],
    'stars':[],
    'repo_url':[]
        }

    #get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])
        # print(repo_info)
    
    return pd.DataFrame(topic_repos_dict)

def scrape_topic(topic_url, topic_name):
    fname= topic_name +'.csv'
    if os.path.exists(fname):
        print("The file {} already exists. skipping..".format(fname))
        return
    topic_df =get_topic_repos(topic_url)
    
    topic_df.to_csv(fname + '.csv', index=None)

topic4_repos = get_topic_repos(topic_urls[4])

def get_topic_titles(doc):
    selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_p_tags=doc.find_all('p', {'class': selection_class })
    ''' topic title'''
    topic_titles = []
    for tag in topic_title_p_tags:
        topic_titles.append(tag.text)
    return topic_titles


def get_topic_description(doc):
    selection_class_description= 'f5 color-fg-muted mb-0 mt-1'
    topic_description_p_tags=doc.find_all('p', {'class': selection_class_description })
    '''topic description'''
    topic_description=[]
    for tag in topic_description_p_tags:
        topic_description.append(tag.text.strip())
    return topic_description    

def get_topic_url(doc):
    topic_link_tags= doc.find_all('a', {'class': 'd-flex no-underline'})
    '''topic urls'''

    topic_urls=[]
    base_url= "https://github.com"
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls



def scrape_topics():
    topics_url= "https://github.com/topics"
    response= requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    topics_dict= {
        'title': get_topic_titles(doc),
        'description': get_topic_description(doc),
        'url': get_topic_url(doc)
    }
    return pd.DataFrame(topics_dict)

def scrape_topics_repos():
    print('Scraping list of topics')
    topics_df =scrape_topics()
    print(topics_df)
    for index, row in topics_df.iterrows():
        print('Scraping top repositories for "{}"'.format(row['title']))
        scrape_topic(row['url'], row['title'])

scrape_topics_repos()

