import requests
from bs4 import BeautifulSoup
from termcolor import colored
from datetime import datetime


#CNBC
def get_CNBC(today_only = True):

    page = requests.get("https://www.cnbc.com/world-economy/")

    soup = BeautifulSoup(page.content, 'html.parser')

    news_div = soup.find_all('div', {'class':'Card-titleContainer'})
    dates_div = soup.find_all('div', {'class':'Card-cardFooter'})

    news_title = []
    news_date = []

    for text in news_div:
        news_title.append(text.find_all('a')[0].text)
    for date in dates_div:
        news_date.append(date.find_all('span', {'class':'Card-time'})[0].text)

    #print(colored("\n\n----------CNBC----------", 'red', attrs=['bold']))
    today_news = []
    older_news = {'news':[],'date':[]}
    for i,date in enumerate(news_date):
        #print("%d. %s %s"%(i+1,news_title[i],date), end='\t')
        if 'hours' in date or 'min' in date or 'hour' in date:
            #print(colored("today",'blue',attrs=['bold']))
            today_news.append(news_title[i])
        else:
            nice_date = date[5:]
            m = nice_date[:3]
            y = nice_date[-5:]
            d = nice_date[4:-7]
            final_date = datetime.strptime(d+" "+m+y,"%d %b %Y").date()
            if final_date == datetime.today().date():
                #print(colored("today",'blue',attrs=['bold']))
                today_news.append(news_title[i])
            else:
                older_news['news'].append(news_title[i])
                older_news['date'].append(date)
                #print(colored("not today",'green',attrs=['bold']))
    
    if today_only:
        return today_news
    else:
        return today_news, older_news



#REUTERS

def get_REUTERS(today_only = True):

    page = requests.get("https://www.reuters.com/news/archive/economicNews")

    soup = BeautifulSoup(page.content, 'html.parser')

    news_div = soup.find_all('div', {'class':'story-content'})
    dates_div = soup.find_all('time', {'class':'article-time'})

    news_title = []
    news_date = []


    for text in news_div:
        news_title.append(text.find_all('a')[0].text.strip())
    for date in dates_div:
        news_date.append(date.find_all('span', {'class':'timestamp'})[0].text)

    #print(colored("\n\n----------REUTERS----------", 'red', attrs=['bold']))
    today_news = []
    older_news = {'news':[],'date':[]}
    for i,date in enumerate(news_date):
        #print("%d. %s %s"%(i+1,news_title[i],date), end='\t')
        if 'EST' in date or 'EDT' in date or 'am' in date or 'pm' in date:
            today_news.append(news_title[i])
            #print("%d. %s %s"%(i+1,news_title[i],date), end='\t')
            #print(colored("today",'blue',attrs=['bold']))
        else:
            older_news['news'].append(news_title[i])
            older_news['date'].append(date)
            #print(colored("not today",'green',attrs=['bold']))
    
    if today_only:
        return today_news
    else:
        return today_news, older_news

'''
#NYTIMES

page = requests.get("https://www.nytimes.com/section/business/economy")

soup = BeautifulSoup(page.content, 'html.parser')

news_div = soup.find_all('div', {'class':'css-1l4spti'})
dates_div = soup.find_all('div', {'class':'css-1cp3ece'})

news_title = []
news_date = []

for text in news_div:
    news_title.append(text.find_all('a')[0].text)
for date in dates_div:
    print(date.span)
    #news_date.append(date.find_all('span')[0].text)

print(colored("\n\n----------NY TIMES----------", 'red', attrs=['bold']))
for i,date in enumerate(news_date):
    print("%d. %s %s"%(i+1,news_title[i],date))
'''

#BUSINESS-STD

def get_BSNN_STD(today_only = True):

    page = requests.get("https://www.business-standard.com/category/international-news-economy-1160102.htm")

    soup = BeautifulSoup(page.content, 'html.parser')

    news_div = soup.find_all('div', {'class':'listing-panel'})


    news_title = []
    news_date = []

    for text in news_div:
        list_els = text.find_all('li')
        #print(list_els)
        for el in list_els:
            #print(el)
            news_date.append(el.find('p').text)
            news_title.append(el.find("h2").text)

    #print(colored("\n\n----------BUSINESS STANDARD----------", 'red', attrs=['bold']))

    today_news = []
    older_news = {'news':[],'date':[]}

    for i,date in enumerate(news_date):
        #print("%d. %s %s"%(i+1,news_title[i],date), end='\t')
        final_date = datetime.strptime(date,"%B %d, %Y, %A").date()
        if final_date == datetime.today().date():
            today_news.append(news_title[i])
            #print(colored("today",'blue',attrs=['bold']))
        else:
            older_news['news'].append(news_title[i])
            older_news['date'].append(date)
            #print(colored("not today",'green',attrs=['bold']))
    
    if today_only:
        return today_news
    else:
        return today_news, older_news
