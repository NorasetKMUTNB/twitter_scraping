import sys
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from Widgets.Sentiment import *
from Widgets.Counting import *
from Widgets.TwitterManager import *

################################################################
## WorkerTweet Class
################################################################
class WorkerTweet(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.twm = twitter_manager()
        self.count = Counting()


    def run(self):
        """ 
        This method will crawler twitter.
        """
        i = 0; key = self.parent.key
        print("Thread Worker CSV :", key, " runing...")

        begin_date_obj = datetime.strptime(self.parent.begin_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(self.parent.end_date, '%Y-%m-%d')
        count_progress = (end_date_obj - begin_date_obj).days + 1 

        ################################################################
        # Crawler tweets
        ################################################################
        while True: # start(24) => end(25)
            until_obj   = datetime.strptime(self.parent.begin_date, '%Y-%m-%d') + timedelta(days=i)
            date        = until_obj.strftime("%Y-%m-%d") # date(str)

            # break out loop
            if until_obj > end_date_obj:break

            # progress label
            self.parent.pbar.set_progress_label('Crawler {}'.format(date))
            # tweets 
            self.twm.new_data_aday(key, date)
            self.update_progress.emit((1/3)*(i+1/count_progress)*100)
            # word
            self.parent.pbar.set_progress_label('Count words {}'.format(date))
            self.count.BoW_tweet(key, date)
            self.update_progress.emit((2/3)*(i+1/count_progress)*100)
            # hashtag
            self.parent.pbar.set_progress_label('Count hashtags {}'.format(date))
            self.count.count_hashtag(key, date); i += 1
            self.update_progress.emit((i/count_progress)*100)

        # get list date in Key directory
        folder = './backup/{}/file_date'.format(key)
        datelist = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

        ################################################################
        # Union file_date
        ################################################################
        self.parent.pbar.set_progress_label('Union {}'.format(key))
        # union_tweets
        self.twm.union_file_tw(key, datelist)
        self.update_progress.emit(33)
        # union_words
        self.twm.union_file_word(key, datelist)
        self.update_progress.emit(66)
        # union_hashtags
        self.twm.union_file_hashtag(key, datelist)
        self.update_progress.emit(99)

        self.exit()

    def stop(self):
        print('Stop Worker Tweet')
        self.terminate()


################################################################
## WorkerCSV Class
################################################################
class WorkerCSV(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        """ 
        This method will make all table.
        """
        key = self.parent.key
        ### base_table ###
        self.parent.ui.base_label.setText("{}".format(key))
        df_base = pd.read_csv('.//backup//{}//{}.csv'.format(key, key))

        # progress label
        self.parent.pbar.set_progress_label('Open Base {} file'.format(key))

        len_row_base = len(df_base.index)
        len_col_base = len(df_base.columns)

        self.parent.ui.base_table.setColumnCount(len_col_base)
        self.parent.ui.base_table.setRowCount(len_row_base)
        self.parent.ui.base_table.setHorizontalHeaderLabels(df_base.columns)

        pbar_count = 0
        self.update_progress.emit(pbar_count)
        for i in range(len_row_base):
            for j in range(len_col_base):
                self.parent.ui.base_table.setItem(i ,j, QTableWidgetItem(str(df_base.iat[i, j])))
            pbar_count = int((i/len_row_base)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.base_table.resizeColumnsToContents()
        self.parent.ui.status_base_label.setText("{} Tweets".format(len_row_base))

        ################################################################
        # Percent Sentimanet
        ################################################################
        count_positive, count_negative, count_neutral = 0, 0, 0

        #count sentiment
        for count in df_base["sentiment"]:
            if count == 'positive': count_positive += 1
            elif count == 'negative': count_negative += 1
            else: count_neutral += 1

        if len_row_base == 0:
            PerPos = 0
            PerNeg = 0
            PerNeu = 0
        else:
            PerPos = (count_positive/len_row_base)*100
            PerNeg = (count_negative/len_row_base)*100
            PerNeu = (count_neutral/len_row_base)*100

        # PerCount Senitment)
        self.parent.ui.negative_label.setText('Negative : {:.2f}%'.format(PerNeg))
        self.parent.ui.neutal_label.setText('Neutal : {:.2f}%'.format(PerNeu))
        self.parent.ui.positive_label.setText('Positive : {:.2f}%'.format(PerPos))

        ################################################################
        ### word_table ###
        ################################################################
        self.temp_df_word = pd.read_csv('.//backup//{}//{}_count_word.csv'.format(key, key))

        del self.temp_df_word["date"]       # delete column date
        
        self.df_word = self.temp_df_word.groupby(['keyword', 'word']).sum().reset_index()
        self.df_word = self.df_word.sort_values(by=['count_word'], ascending=False)

        # progress label
        self.parent.pbar.set_progress_label('Open BOW {} file'.format(key))

        len_row_word = len(self.df_word.index)
        len_col_word = len(self.df_word.columns)

        self.parent.ui.word_table.setColumnCount(len_col_word)
        self.parent.ui.word_table.setRowCount(len_row_word)
        self.parent.ui.word_table.setHorizontalHeaderLabels(self.df_word.columns)

        pbar_count = 0
        for i in range(len_row_word):
            for j in range(len_col_word):
                self.parent.ui.word_table.setItem(i ,j, QTableWidgetItem(str(self.df_word.iat[i, j])))
            # update progress bar
            pbar_count = int((i/len_row_word)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.word_table.resizeColumnsToContents()
        self.parent.ui.status_word_label.setText("{} Words".format(len_row_word))

        ################################################################
        ### hashtag_table ###
        ################################################################
        self.temp_df_hashtag = pd.read_csv('.//backup//{}//{}_count_hashtag.csv'.format(key, key))

        del self.temp_df_hashtag["date"]       # delete column date

        self.df_hashtag = self.temp_df_hashtag.groupby(['keyword', 'hashtag']).sum().reset_index()
        self.df_hashtag = self.df_hashtag.sort_values(by=['count_hashtag'], ascending=False)

        # progress label
        self.parent.pbar.set_progress_label('Open Hashtag {} file'.format(key))

        len_row_hashtag = len(self.df_hashtag.index)
        len_col_hashtag = len(self.df_hashtag.columns)

        self.parent.ui.hashtag_table.setColumnCount(len_col_hashtag)
        self.parent.ui.hashtag_table.setRowCount(len_row_hashtag)
        self.parent.ui.hashtag_table.setHorizontalHeaderLabels(self.df_hashtag.columns)

        pbar_count = 0
        for i in range(len_row_hashtag):
            for j in range(len_col_hashtag):
                self.parent.ui.hashtag_table.setItem(i ,j, QTableWidgetItem(str(self.df_hashtag.iat[i, j])))
            # update progress bar
            pbar_count = int((i/len_row_hashtag)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.hashtag_table.resizeColumnsToContents()
        self.parent.ui.status_hashtag_label.setText("{} Hashtags".format(len_row_hashtag))


    def stop(self):
        print('Stop Worker CSV')
        self.terminate()

################################################################
## WorkerChangeDate Class
################################################################
class WorkerChangeDate(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.twm = twitter_manager()
        self.count = Counting()

    def run(self):
        """ 
        This method will make all table when change date.
        """
        temp_count = 0
        value = self.parent.DateSelection
        self.key = self.parent.key
        self.datelist = []

        print("Thread Worker Change Date :", self.key, " runing...")

        # varr for percent sentiment
        count_positive, count_negative, count_neutral = 0, 0, 0
        PerPos, PerNeg, PerNeu = 0, 0, 0

        # progress label
        self.parent.pbar.set_progress_label('Open Base {} file'.format(self.key))

        # clear table and set label status tabel
        self.parent.ui.base_table.setRowCount(0)        # clear table base
        self.parent.ui.status_base_label.setText("0 Tweets")
        self.parent.ui.word_table.setRowCount(0)        # clear table word
        self.parent.ui.status_word_label.setText("0 Words")
        self.parent.ui.hashtag_table.setRowCount(0)     # clear table hashtag
        self.parent.ui.status_hashtag_label.setText("0 Hashtags")

        # PerCount Senitment
        self.parent.ui.positive_label.setText('Positive : 0%')
        self.parent.ui.negative_label.setText('Negative : 0%')
        self.parent.ui.neutal_label.setText('Neutal : 0%')

        ################################################################
        # Selection 'All' => get range date
        ################################################################
        if value == 'All':
            for i in self.parent.dict_date:
                if not self.parent.dict_date[i] :
                    # not all date it have. it's range date
                    self.df_base = pd.DataFrame(columns= [
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

                    self.df_word = pd.DataFrame(columns= [
                        'keyword',
                        'language',
                        'word',
                        'count_word',
                        'date'])

                    self.df_hashtag = pd.DataFrame(columns= [
                        'keyword',
                        'hashtag',
                        'count_hashtag',
                        'date'])

                    for date in self.parent.list_date[1:]:
                        self.datelist.append(date)  # append date

                        self.temp_df = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_twitterCrawler.csv'.format(self.key , date, self.key, date))
                        self.df_base = pd.concat([self.df_base, self.temp_df],ignore_index=True)

                        self.temp_df = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_count_word.csv'.format(self.key , date, self.key, date))
                        self.df_word = pd.concat([self.df_word, self.temp_df],ignore_index=True)

                        self.temp_df = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_count_hashtag.csv'.format(self.key , date, self.key, date))
                        self.df_hashtag = pd.concat([self.df_hashtag, self.temp_df],ignore_index=True)

                    break   # break for loop check range date 
                else: 
                    temp_count += 1

            ################################################################
            # All date in keyword have
            ################################################################
            if temp_count == len(self.parent.dict_date):
                self.df_base = pd.read_csv('.//backup//{}//{}.csv'.format(self.key, self.key))
                self.df_word = pd.read_csv('.//backup//{}//{}_count_word.csv'.format(self.key, self.key))
                self.df_hashtag = pd.read_csv('.//backup//{}//{}_count_hashtag.csv'.format(self.key, self.key))

        ################################################################
        # Selection Only a Date
        ################################################################
        elif value != '':
            self.df_base = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_twitterCrawler.csv'.format(self.key, value, self.key, value))
            self.df_word = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_count_word.csv'.format(self.key, value, self.key, value))
            self.df_hashtag = pd.read_csv('.//backup//{}//file_date//{}//{}_{}_count_hashtag.csv'.format(self.key, value, self.key, value))

        ################################################################
        ### base_table ###            
        ################################################################
        len_row_base = len(self.df_base.index)
        len_col_base = len(self.df_base.columns)

        self.parent.ui.base_table.setColumnCount(len_col_base)
        self.parent.ui.base_table.setRowCount(len_row_base)
        self.parent.ui.base_table.setHorizontalHeaderLabels(self.df_base.columns)

        pbar_count = 0
        self.update_progress.emit(pbar_count)
        for i in range(len_row_base):
            for j in range(len_col_base):
                self.parent.ui.base_table.setItem(i ,j, QTableWidgetItem(str(self.df_base.iat[i, j])))
            pbar_count = int((i/len_row_base)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.base_table.resizeColumnsToContents()
        self.parent.ui.status_base_label.setText("{} Tweets".format(len_row_base))


        ################################################################
        # It is range date 'All', it must have new BOW and Hashtag
        ################################################################
        if not (self.df_base.empty) :
            # count sentiment
            for count in self.df_base["sentiment"]:
                if count == 'positive': count_positive += 1
                elif count == 'negative': count_negative += 1
                else: count_neutral += 1

            if len_row_base == 0:
                PerPos = 0
                PerNeg = 0
                PerNeu = 0
            else:
                PerPos = (count_positive/len_row_base)*100
                PerNeg = (count_negative/len_row_base)*100
                PerNeu = (count_neutral/len_row_base)*100

            # PerCount Senitment
            self.parent.ui.positive_label.setText('Positive : {:.2f}%'.format(PerPos))
            self.parent.ui.negative_label.setText('Negative : {:.2f}%'.format(PerNeg))
            self.parent.ui.neutal_label.setText('Neutal : {:.2f}%'.format(PerNeu))

            ################################################################
            # LoadData Word & Hashtag
            ################################################################
    
            ################################################################
            ### word_table ###            
            ################################################################
            del self.df_word["date"]       # delete column date

            self.df_word = self.df_word.groupby(['keyword', 'word']).sum().reset_index()
            self.df_word = self.df_word.sort_values(by=['count_word'], ascending=False)

            len_row_word = len(self.df_word.index)
            len_col_word = len(self.df_word.columns)

            self.parent.ui.word_table.setColumnCount(len_col_word)
            self.parent.ui.word_table.setRowCount(len_row_word)
            self.parent.ui.word_table.setHorizontalHeaderLabels(self.df_word.columns)

            pbar_count = 0
            for i in range(len_row_word):
                for j in range(len_col_word):
                    self.parent.ui.word_table.setItem(i ,j, QTableWidgetItem(str(self.df_word.iat[i, j])))
                # update progress bar
                pbar_count = int((i/len_row_word)*100)
                self.update_progress.emit(pbar_count)
            
            self.parent.ui.word_table.resizeColumnsToContents()
            self.parent.ui.status_word_label.setText("{} Words".format(len_row_word))

            ################################################################
            ### hashtag_table ###
            ################################################################
            del self.df_hashtag["date"]       # delete column date

            self.df_hashtag = self.df_hashtag.groupby(['keyword', 'hashtag']).sum().reset_index()
            self.df_hashtag = self.df_hashtag.sort_values(by=['count_hashtag'], ascending=False)

            len_row_hashtag = len(self.df_hashtag.index)
            len_col_hashtag = len(self.df_hashtag.columns)

            self.parent.ui.hashtag_table.setColumnCount(len_col_hashtag)
            self.parent.ui.hashtag_table.setRowCount(len_row_hashtag)
            self.parent.ui.hashtag_table.setHorizontalHeaderLabels(self.df_hashtag.columns)

            pbar_count = 0
            for i in range(len_row_hashtag):
                for j in range(len_col_hashtag):
                    self.parent.ui.hashtag_table.setItem(i ,j, QTableWidgetItem(str(self.df_hashtag.iat[i, j])))
                # update progress bar
                pbar_count = int((i/len_row_hashtag)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.hashtag_table.resizeColumnsToContents()
            self.parent.ui.status_hashtag_label.setText("{} Hashtags".format(len_row_hashtag))


    def stop(self):
        print('Stop Worker Change Date')
        self.terminate()

################################################################
## WorkerTweet Class
################################################################
class WorkerExport(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent


    def run(self):
        """ 
        This method will export all file.
        """
        folder = './backup'
        keylist = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

        self.parent.pbar.set_key_progress('All Keyword')
        keylen = len(keylist)

        ################################################################
        # union file tweets
        ################################################################
        self.df = pd.DataFrame(columns= [
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

        self.parent.pbar.set_progress_label('Union All Tweets File')
        pbar_count = 0; i=0
        print('start union all tweets')
        for key in keylist:
            self.temp_df = pd.read_csv('.//backup//{}//{}.csv'.format(key, key))
            self.df = pd.concat([self.df,self.temp_df],ignore_index=True)
            # update progress bar
            pbar_count = int((i/keylen)*100)
            self.update_progress.emit(pbar_count)
            i+=1

        self.parent.pbar.set_progress_label('Export All Tweets File')
        self.df.to_csv('.//backup//all_tweets.csv', index=False, encoding='utf-8')
        print('finish export all tweets')

        ################################################################
        # union file word 
        ################################################################
        self.df = pd.DataFrame(columns= [
            'keyword',
            'language',
            'word',
            'count_word',
            'date'])

        self.parent.pbar.set_progress_label('Union All Words File')
        pbar_count = 0; i=0
        print('start union all words')
        for key in keylist:
            self.temp_df = pd.read_csv('.//backup//{}//{}_count_word.csv'.format(key, key))
            self.df = pd.concat([self.df,self.temp_df],ignore_index=True)
            # update progress bar
            pbar_count = int((i/keylen)*100)
            self.update_progress.emit(pbar_count)
            i+=1

        self.parent.pbar.set_progress_label('Export All Words File')
        self.df.to_csv('.//backup//all_count_word.csv', index=False, encoding='utf-8')
        print('finish export all words')


        ################################################################
        # union file hashtag
        ################################################################
        self.df = pd.DataFrame(columns= [
            'keyword',
            'hashtag',
            'count_hashtag',
            'date'])

        self.parent.pbar.set_progress_label('Union All Hashtags File')
        pbar_count = 0; i=0
        print('start union all hashtags')
        for key in keylist:
            self.temp_df = pd.read_csv('.//backup//{}//{}_count_hashtag.csv'.format(key, key))
            self.df = pd.concat([self.df,self.temp_df],ignore_index=True)
            # update progress bar
            pbar_count = int((i/keylen)*100)
            self.update_progress.emit(pbar_count)
            i=+1

        self.parent.pbar.set_progress_label('Export All Hashtag File')
        self.df.to_csv('.//backup//all_count_hashtag.csv'.format(key, key), index=False, encoding='utf-8')
        print('finish export all hashtags')


        self.exit()

    def stop(self):
        print('Stop Worker Export All')
        self.terminate()