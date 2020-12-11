import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import tweepy
from geopy.exc import GeocoderTimedOut 
from geopy.geocoders import Nominatim
import config
from textblob import TextBlob
from datetime import date,timedelta, datetime
import matplotlib.pyplot as plt
import statistics
import yweather
from newsapi import NewsApiClient

#import json
from ibm_watson import NaturalLanguageUnderstandingV1
#from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, ConceptsOptions

def findGeocode(city):    
    try: 
        geolocator = Nominatim(user_agent="your_app_name")
        return geolocator.geocode(city) 
    except GeocoderTimedOut: 
        return findGeocode(city)     

version='2020-09-08'
ibmapikey=config.get_ibm_nlu_keys()[0]
ibmurl=config.get_ibm_nlu_keys()[1]

twit=config.get_twitter_keys()
twitter_acc_token=twit[0]
twitter_acc_secret=twit[1]
twitter_api_key=twit[2]
twitter_api_secret=twit[3]

class TwitterStreamer():
    def stream_tweets(self,hash_list):
        listener=TwitterStreamListener()
        auth=tweepy.OAuthHandler(twitter_api_key,twitter_api_secret)
        auth.set_access_token(twitter_acc_token,twitter_acc_secret)

        stream=tweepy.streaming.Stream(auth,listener)
        stream.filter(track=hash_list)

class TwitterStreamListener(tweepy.streaming.StreamListener):
     
    def on_status(self,status):
        print(status.id)
        print(status.user.name)
        print(status.text)
        return True
    
    def on_data(self,data):
        print(data)
        return True

    def on_error(self,status_code):
        print('Error with status code: ',status_code)
        return True
    
    def on_timeout(self):
        print('Timeout')
        return True

ddd=0
def get_tweets(location,count):
    loc=findGeocode(location)

    #date list
    d=[]
    today=date.today()
    for i in range(6):
        l=[]
        l.append(today-timedelta(i))
        d.append(l)



    #listener=TwitterStreamListener()
    auth=tweepy.OAuthHandler(twitter_api_key,twitter_api_secret)
    auth.set_access_token(twitter_acc_token,twitter_acc_secret)
    api=tweepy.API(auth)
    #place=api.geo_search(query="India",granularity="country")
    #place_id=place[0].id
    c=0
    global ddd
    for i in d:
        fetched=api.search(q="covid -filter:retweets",lang='en',geocode=str(loc.latitude)+','+str(loc.longitude)+',3000000km',count=count,tweet_mode='extended',until=i[0])
        l=[]
        for j in fetched:
            if(c==0):
                ddd=j.created_at
                c=1
            l.append(j.full_text)
        i.append(l)
    return d
    
    #for i in fetched:
    #    print(i.text)

def get_tweets2(location,count,topic="covid"):

    loc=findGeocode(location)


    auth=tweepy.OAuthHandler(twitter_api_key,twitter_api_secret)
    auth.set_access_token(twitter_acc_token,twitter_acc_secret)
    api=tweepy.API(auth)

    search_words=topic+" -filter:retweets"
    d=[]
    date_since= date.today()#"2020-10-08"
    for i in range(6):
        d.append(date_since-timedelta(i))
    d=d[::-1]
    t=[]
    for i in range(0,len(d)-1):
        l=[]
        tweets=tweepy.Cursor(api.search,q=search_words,geocode=str(loc.latitude)+','+str(loc.longitude)+',3000000km',lang="en",since=d[i],until=d[i+1],tweet_mode='extended').items(count)
        for j in tweets:
            l.append(j.full_text)
        t.append([d[i],l])
    return t

def analyze3(data):
    x,y=[],[]

    for i in data:
        x.append(str(i[0].day)+'-'+str(i[0].month))
        l=[]
        for j in i[1]:
            a=TextBlob(j).sentiment.polarity
            l.append(a)
        y.append(statistics.mean(l))
    #plt.plot(x,y)
    #plt.show()
    return (x,y)

def trending(location,count):
    loc=findGeocode(location)
    #client=yweather.Client()
    with open('woeid.json','r') as f:
        w=json.load(f)
    woeid=2295377
    for i in w:
        if(i["name"]==location or i["country"]==location or i["countryCode"]==location):
            woeid=i["woeid"]
    #woeid=2295377#23424977 #USA
    #client.fetch_woeid("London")
    
    auth=tweepy.OAuthHandler(twitter_api_key,twitter_api_secret)
    auth.set_access_token(twitter_acc_token,twitter_acc_secret)
    api=tweepy.API(auth)

    trends=api.trends_place(id=woeid)
    t=[]
    #search=""
    c=0
    for i in trends:
        for j in i['trends']:
            c+=1
            t.append(j['name'])
            #search=search+" OR "+j['name']
            if(c>3):
                break
        if(c>3):
            break
    
    d=[]
    for i in t:
        l=[]
        l.append(i)
        search=i
        tweets=tweepy.Cursor(api.search,q=search,geocode=str(loc.latitude)+','+str(loc.longitude)+',3000000km',lang="en",tweet_mode='extended').items(count)
        m=[]
        for j in tweets:
            m.append(j.full_text)
        l.append(m)
        d.append(l)
    return d

def analyze4(data):
    x,y=[],[]

    for i in data:
        x.append(i[0])
        l=[]
        for j in i[1]:
            a=TextBlob(j).sentiment.polarity
            l.append(a)
        y.append(statistics.mean(l))
    return (x,y)

def analyze5(data):
    x,y=[],[]

    for i in data:
        x.append(i[0])
        l=[0,0,0]
        for j in i[1]:
            a=TextBlob(j).sentiment.polarity
            if(a>0):
                l[0]+=1
            elif (a==0):
                l[1]+=1
            else:
                l[2]+=1
        y.append(l)
    return (x,y)

def analyze6(data):
    l=[]

    for i in data:
        d=[]
        d.append(i[0])
        d1=[]
        for j in i[1]:
            d1.append([TextBlob(j).sentiment.subjectivity,TextBlob(j).sentiment.polarity])
        d.append(d1)
        l.append(d)
    return l

def analyze_pol_and_sent(data):
    l=[]
    for i in data:
        for j in i[1]:
            l.append([round(TextBlob(j).sentiment.subjectivity,4),round(TextBlob(j).sentiment.polarity,4)])
    return l
    
def ibm_concepts(data): #returns concepts related to text. Input are tweets list in the form of [[date1,[tweets]],[date2,[tweets]]] like get_tweets2 output
    l=""
    for i in data:
        l=l+''.join(i[1])
    l=l[0:49999]
    #print(l)
    authenticator = IAMAuthenticator(ibmapikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2020-08-01',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(ibmurl)

    response = natural_language_understanding.analyze(text=l,features=Features(concepts=ConceptsOptions(limit=10))).get_result()

    result=[]
    for i in response['concepts']:#result['concepts']:
        result.append([i["dbpedia_resource"][7::].split('/')[-1],i["relevance"]])
    return result
    #print(json.dumps(response, indent=2))

def get_user_tweets(user):
    auth=tweepy.OAuthHandler(twitter_api_key,twitter_api_secret)
    auth.set_access_token(twitter_acc_token,twitter_acc_secret)
    api=tweepy.API(auth)
    
    tweets=api.user_timeline(screen_name=user,count=10,include_rts=False,tweet_mode='extended')
    l=[]
    for i in tweets:
        l.append(i.full_text)

def get_news(topic):
    newsapi=NewsApiClient(api_key='9546ef01d07d4bba9d4ef31973475dbd')
    #topic=input('Topic to look for: ')
    head=newsapi.get_top_headlines(q=topic)
    x,y=[],[]
    for i in head['articles']:
        x.append(i['title'])
        y.append(i['description'])
        # print('Description: ',i['description'])
        # print('_________')
    return (x,y)

#t=get_tweets2('USA',20)
#analyze3(t)
#t=trending("USA",5)
#d=analyze4(t)

# t=get_tweets2("USA",100,"halloween")
# ibm_concepts(t)