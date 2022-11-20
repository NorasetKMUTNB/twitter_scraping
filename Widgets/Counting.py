
import os
import re

import pandas as pd
import numpy as np

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import isthai

from nltk.corpus import stopwords
from datetime import datetime
import string

from sklearn.feature_extraction.text import CountVectorizer

################################################################
## Counting Class
################################################################
class Counting:
    """ Counting class is object for counting word and counting hashtag """

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
    # Bow
    ################################################################
    def BoW_tweet(self, key, date):
        """
        This method will counting word a date and save dataframe in form csv.

        Parameters
        ----------
        key : str
            keyword 
        date : str
            date form YYYY-MM-DD
        """
        df = pd.read_csv('backup//{}//file_date//{}//{}_{}_twitterCrawler.csv'.format(key, date, key, date))

        new_text = []
        for txt in df["text"]:
            new_text.append(self.cleanText(txt))

        keyword_df = pd.DataFrame(columns = ['keyword', "language", 'word', 'count_word', "date"])

        if not new_text:
            keyword_df.to_csv('backup//{}//file_date//{}//{}_{}_count_word.csv'.format(key, date, key, date), index=False, encoding='utf-8')
            return 

        vectorizer = CountVectorizer(tokenizer=self.tokenize)   
        transformed_data = vectorizer.fit_transform(new_text)
        keyword_df['word'] = vectorizer.get_feature_names_out()

        self.language(keyword_df)       # language

        # counting of word
        keyword_df['count_word'] = np.ravel(transformed_data.sum(axis=0))

        # date
        temp_date = datetime.strptime(date, '%Y-%m-%d')
        form_date = temp_date.strftime("%d/%m/%Y")
        keyword_df['date'] = form_date
        
        keyword_df['keyword'] = key     # key 

        keyword_df = keyword_df.sort_values(by=['count_word'], ascending=False)
        keyword_df.to_csv('backup//{}//file_date//{}//{}_{}_count_word.csv'.format(key, date, key, date), index=False, encoding='utf-8')


    def language(self, data):
        """
        This method will detect language TH/EN append in dataframe.

        Parameters
        ----------
        data : pandas.core.frame.DataFrame
            dataframe counting word 
        """
        temp_language = pd.Series([],dtype=pd.StringDtype())
        for i in range(len(data)):
            if isthai(data["word"][i]): temp_language[i]="th"
            else: temp_language[i]="en"
        data['language'] = temp_language


    def cleanText(self, text):
        """
        This method will make string word for use when counting word.

        Parameters
        ----------
        text : str
            text from data crawler twitter
        
        Returns
        -------
        result : str
            string word for use when counting word
        """
        text = self.remove_url_th(text).lower()
        stop_word_th = set(thai_stopwords())
        stop_word_en = set(stopwords.words('english'))
        exclude = set(string.punctuation)
        sentence = word_tokenize(text, engine="newmm")
        result = [word for word in sentence if (word not in stop_word_th) and (" " not in word) and (word not in stop_word_en) and (word not in exclude)]

        return "/".join(result)


    def tokenize(self, d):
        """
        This method will split word from func(cleanText).

        Parameters
        ----------
        d : str
            word from func(cleanText) 

        Returns
        -------
        result : list
            list word for use when counting word
        """
        result = d.split("/")
        result = list(filter(None, result))
        return result
    
    ################################################################
    # hashtag
    ################################################################
    def count_hashtag(self, key, date):
        """
        This method will counting hashtag a date and save dataframe in form csv.

        Parameters
        ----------
        key : str
            keyword 
        date : str
            date form YYYY-MM-DD
        """
        df = pd.read_csv('backup//{}//file_date//{}//{}_{}_twitterCrawler.csv'.format(key, date, key, date))

        hash_tag_cnt_df = pd.DataFrame(columns = ['keyword', 'hashtag', 'count_hashtag', 'date']) 

        if df["hashtag"].dropna().empty:
            hash_tag_cnt_df.to_csv('backup//{}//file_date//{}//{}_{}_count_hashtag.csv'.format(key, date, key, date), index=False, encoding='utf-8')
            return 

        hastag_data = df["hashtag"].dropna()

        vectorizer = CountVectorizer(tokenizer=self.slash_tokenize)
        transformed_data = vectorizer.fit_transform(hastag_data)


        hash_tag_cnt_df['hashtag'] = vectorizer.get_feature_names_out()
        hash_tag_cnt_df['count_hashtag'] = np.ravel(transformed_data.sum(axis=0))

        hash_tag_cnt_df = hash_tag_cnt_df.sort_values(by=['count_hashtag'], ascending=False)

        temp_date = datetime.strptime(date, '%Y-%m-%d')
        form_date = temp_date.strftime("%d/%m/%Y")
        hash_tag_cnt_df['date'] = form_date

        hash_tag_cnt_df['keyword'] = key

        hash_tag_cnt_df.to_csv('backup//{}//file_date//{}//{}_{}_count_hashtag.csv'.format(key, date, key, date), index=False, encoding='utf-8')

    
    def slash_tokenize(self, d):  
        """
        This method will split hashtag from hashtag in dataframe .

        Parameters
        ----------
        d : str
            word from hashtag in dataframe 

        Returns
        -------
        result : list
            list hashtag for use when counting word
        """
        result = d.split("/")
        result.remove('')
        return result