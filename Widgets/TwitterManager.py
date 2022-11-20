import os
import tweepy as tw
import pandas as pd
import re

from datetime import datetime, timedelta

from Widgets.Sentiment import Sentiment 
senti = Sentiment()
from Widgets.Counting import Counting 
count = Counting()

from DialogGui import *

################################################################
## twitter_manager Class
################################################################
class twitter_manager:
    """
    twitter_manager class is object for Crawler Twitter

    ...

    Attributes
    ----------
    consumer_key : str
        keep text key for use when you use TwitterAPI
    consumer_secret : str
        keep text key for use when you use TwitterAPI
    access_token : str 
        keep text key for use when you use TwitterAPI
    access_token_secret : str
        keep text key for use when you use TwitterAPI
    auth : twiiter_API
        use to connect account developer twitter
    api : twiiter_API
        use it when crawler twitter 
    
    
    """

    def __init__(self):
        # Consumer Key = API Key
        self.consumer_key= '7wlWBiho3eO8BnNQihvZptNHl'   
        # Consumer Secret = API Secret
        self.consumer_secret= 'd4LRXmrOOhL7V3ZdPeSHYh2QCsvt9rfJLKF9WfffTUVY1sfzoR'
        # OAuth Token = Access Token
        self.access_token= '824220293111500800-lO5uQ3dlEoVIQ6cjadV6JGV0iKDjGAp'
        # OAuth Token Secret = Access Token Secret
        self.access_token_secret= 'h2r1uSEtEp7Mo5z6tb7LLM3mbE559hD1W9v3aa8vladTZ'

        self.auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        # get twiiter_API
        self.api = tw.API(self.auth, wait_on_rate_limit=True)

    
    def remove_url_th(self,txt):
        """Replace URLs found in a text string with nothing 
        (i.e. it will remove the URL from the string).

        Parameters
        ----------
        txt : str
            A text string that you want to parse and remove urls.

        Returns
        -------
        The same txt string with url's removed.
        """

        return " ".join(re.sub("([^\u0E00-\u0E7Fa-zA-Z' ]|^'|'$|''|(\w+:\/\/\S+))", "", str(txt)).split())

    ################################################################
    # Create Key Dicectory
    ################################################################
    def create_key_directory(self, key):
        """
        This method will create directory (keyword) when have new keyword

        Parameters
        ----------
        key : str
            keyword 
        """
        # Parent Directory path
        parent_dir = "C://yaengg\DNS//tweepy//backup"
        
        # Path
        path = os.path.join(parent_dir, key)

        # Create the directory
        # directory in parent_dir
        os.mkdir(path)

        # Create the directory
        # directory in parent_dir
        date_path = os.path.join(parent_dir, key, 'file_date')
        os.mkdir(date_path)

    ################################################################
    # Create Date Dicectory
    ################################################################
    def create_date_directory(self, key, date):
        """
        This method will create directory (date) when crawler new date

        Parameters
        ----------
        key : str
            keyword 
        date : str
            date form YYYY-MM-DD
        """
        # Directory
        directory = key + "//file_date//{}".format(date)
        # Parent Directory path
        parent_dir = "C://yaengg\DNS//tweepy//backup"

        # get list date in Key directory
        folder = './backup/{}/file_date'.format(key)
        datelist = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

        # it have date in datelist
        if date in datelist: return
        
        # Path
        path = os.path.join(parent_dir, directory)
        
        # Create the directory
        # directory in parent_dir
        os.mkdir(path)

    ################################################################
    # Serach Tweet A Day
    ################################################################
    def new_data_aday(self, key, until):
        """
        This method will crawler twitter.
        in Thai tweet have limit 100 tweet
        and in English tweet have limit 100 tweet.
        
        Parameters
        ----------
        key : str
            keyword 
        until : str
            date form YYYY-MM-DD
        """
        self.key = key

        self.create_date_directory(key, until)  # create date directory

        new_search = self.key + " -filter:retweets"

        # set until day (str)
        until_obj   = datetime.strptime(until, '%Y-%m-%d') + timedelta(days=1)
        until_set   = until_obj.strftime("%Y-%m-%d")
        # set endDate day for end loop
        startDate   = datetime.strptime(until+'23:59:59+00:00', '%Y-%m-%d%H:%M:%S%z')
        endDate     = startDate - timedelta(days=1)

        df = pd.DataFrame(columns= [
            'keyword',
            'language',
            'author',
            'twitter_name',
            'create_at',
            'location', 
            'text', 
            'hashtag', 
            'tweets_count',
            'retweet_count', 
            'favourite_count',
            'date',
            'time',
            'sentiment'])

        columns = [
            'keyword',
            'language',
            'author',
            'twitter_name',
            'create_at', 
            'location',
            'text', 
            'hashtag', 
            'tweets_count',
            'retweet_count', 
            'favourite_count',
            'date',
            'time',
            'sentiment']

        ############################################################
        # twitter(TH)
        ############################################################
        for tweet in tw.Cursor(self.api.search_tweets,
            q=new_search,
            lang='th',
            until=until_set,
            result_type='recent',
            tweet_mode='extended').items(100):

            # create_at = tweet.created_at.astimezone()
            create_at = tweet.created_at

            if create_at > startDate: continue
            elif create_at < endDate : break

            # keyword = query
            language = 'th'
            tweets_count = 1

            # hashtag
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ''
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'/'+entity_hashtag[i]['text']

            # infomantion
            twitter_name = '@'+tweet.user.screen_name
            author = tweet.user.name
            location = tweet.user.location
            re_count = tweet.retweet_count
            tweets_count += re_count
            
            date = create_at.strftime("%d/%m/%Y")
            time = create_at.strftime("%H:%M")

            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            # sentiment 
            sentiment = senti.checksentimentword(self.remove_url_th(text))

            # temp for a tweet in data_frame
            new_column = pd.DataFrame([[
                self.key, 
                language, 
                author,
                twitter_name,
                create_at, 
                location,
                text, 
                hashtag, 
                tweets_count, 
                re_count,
                fav_count, 
                date,
                time,
                sentiment]], columns = columns)

            # append in data_frame
            df = pd.concat([df,new_column],ignore_index=True)

        ############################################################
        # twitter(EN)
        ############################################################
        for tweet in tw.Cursor(self.api.search_tweets,
            q=new_search,
            lang='en',
            until=until_set,
            result_type='recent',
            tweet_mode='extended').items(100):

            # create_at = tweet.created_at.astimezone()
            create_at = tweet.created_at

            if create_at > startDate: continue
            elif create_at < endDate : break
            
            # keyword = self.key
            language = 'en'
            tweets_count = 1

            # hashtag
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ''
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'/'+entity_hashtag[i]['text']

            # infomantion
            twitter_name = '@'+tweet.user.screen_name
            author = tweet.user.name
            location = tweet.user.location
            re_count = tweet.retweet_count
            tweets_count += re_count

            date = create_at.strftime("%d/%m/%Y")
            time = create_at.strftime("%H:%M")
 
            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            # sentiment 
            sentiment = senti.checksentimentword(self.remove_url_th(text))

            new_column = pd.DataFrame([[
                self.key, 
                language, 
                author,
                twitter_name,
                create_at, 
                location,
                text, 
                hashtag, 
                tweets_count, 
                re_count,
                fav_count, 
                date,
                time,
                sentiment]], columns = columns)

            # append in data_frame
            df = pd.concat([df,new_column],ignore_index=True)

        # convent to csv
        df.to_csv('backup//{}//file_date//{}//{}_{}_twitterCrawler.csv'.format(self.key, until, self.key, until), index=False, encoding='utf-8')
        # print('finished : {} at {}'.format(self.key, until))

    ################################################################
    # Union File Tweets
    ################################################################
    def union_file_tw(self, key, datelist):
        """
        This method will union file tweets
        
        Parameters
        ----------
        key : str
            keyword 
        datelist : list
            list date from directory keyword
        """
        df = pd.DataFrame(columns= [
            'keyword',
            'language',
            'author',
            'twitter_name',
            'create_at',
            'location', 
            'text', 
            'hashtag', 
            'tweets_count',
            'retweet_count',
            'favourite_count',
            'date',
            'time',
            'sentiment'])

        for date in datelist:
            temp_df = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_twitterCrawler.csv'.format(key ,date, key, date))
            df = pd.concat([df,temp_df],ignore_index=True)

            # convent to csv
            df.to_csv('.//backup//{}//{}.csv'.format(key, key), index=False, encoding='utf-8')

    ################################################################
    # Union File Words
    ################################################################
    def union_file_word(self, key, datelist):
        """
        This method will union file words

        Parameters
        ----------
        key : str
            keyword 
        datelist : list
            list date from directory keyword
        """
        df = pd.DataFrame(columns= [
            'keyword',
            'language',
            'word',
            'count_word',
            'date'])

        for date in datelist:
                temp_df = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_count_word.csv'.format(key ,date, key, date))
                df = pd.concat([df,temp_df],ignore_index=True)

                # convent to csv
                df.to_csv('.//backup//{}//{}_count_word.csv'.format(key, key), index=False, encoding='utf-8')
    
    ################################################################
    # Union File Haashtags
    ################################################################
    def union_file_hashtag(self, key, datelist):
        """
        This method will union file hashtags

        Parameters
        ----------
        key : str
            keyword 
        datelist : list
            list date from directory keyword
        """
        df = pd.DataFrame(columns= [
            'keyword',
            'hashtag',
            'count_hashtag',
            'date'])

        for date in datelist:
                temp_df = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_count_hashtag.csv'.format(key ,date, key, date))
                df = pd.concat([df,temp_df],ignore_index=True)

                # convent to csv
                df.to_csv('.//backup//{}//{}_count_hashtag.csv'.format(key, key), index=False, encoding='utf-8')

        
