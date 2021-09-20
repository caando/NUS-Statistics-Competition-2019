from credentials import twitter_consumer_key, twitter_consumer_secret, twitter_assess_token, twitter_assess_token_secret
from datetime import datetime, timedelta
import time
import tweepy
import xlwt

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_assess_token, twitter_assess_token_secret)

api = tweepy.API(auth)

class Tweet():
    def __init__(self, Id, text, starttime):
        self.id = Id
        self.text = text
        self.starttime = starttime
        self.favorite_count = []
        self.retweet_count = []
    def get_id(self):
        return self.id
    def add_favorite(self, favourite):
        self.favorite_count.append(favourite)
    def add_retweet(self, retweet):
        self.retweet_count.append(retweet)
    def get_starttime(self):
        return self.starttime
    def get_favourite(self):
        return self.favorite_count
    def get_retweet(self):
        return self.retweet_count

class tweet_tracker():
    def __init__(self, screen_name, tweet_limit, limit, time_interval):
        self.starttime = None
        self.screen_name = screen_name
        self.tweet_limit = tweet_limit
        self.limit = limit
        self.time_interval = timedelta(seconds = time_interval)
        self.tweets = []

    def run(self):
        print("Warning: DO NOT INTERRUPT THE PROGRAM MID RUN, THE OUTPUT FILE WILL ONLY BE SAVED AFTER PROCESS IS COMPLETED!")
        if self.time_interval < timedelta(seconds = 10):
            print("Warning: Having a time interval less than 10s might result in inaccurate data due to slow server respond time. Especially if there is a large number of tweets being tracked.")
        print("Start time:", datetime.now())
        self.starttime = datetime.now()
        last_tweet = api.user_timeline(screen_name = self.screen_name, count = 1)[0].id
        start_tweet = last_tweet
        wf = xlwt.Workbook()
        ws_favorite = wf.add_sheet('favourites')
        ws_retweet = wf.add_sheet('retweets')
        check_complete = False
        wait = self.starttime + self.time_interval
        while not check_complete:
            if len(self.tweets) < self.tweet_limit:
                tweets = api.user_timeline(screen_name = self.screen_name, since_id = start_tweet, count =200)[::-1]
                for tweet in tweets:
                    if tweet.id > last_tweet and tweet.text[:4] != "RT @" and len(self.tweets) < self.tweet_limit:
                        print("New tweet -", "ID:" + str(tweet.id), "Text:" + tweet.text)
                        ws_favorite.write(0, len(self.tweets), tweet.id)
                        ws_favorite.write(1, len(self.tweets), tweet.text)
                        ws_retweet.write(0, len(self.tweets), tweet.id)
                        ws_retweet.write(1, len(self.tweets), tweet.text)
                        last_tweet = tweet.id
                        new_tweet = Tweet(tweet.id, tweet.text, datetime.now())
                        self.tweets.append(new_tweet)
            else:
                check_complete = True
                tweets = api.user_timeline(screen_name = self.screen_name, since_id = start_tweet, max_id = last_tweet)[::-1]
            finished = 0
            for i in range(len(self.tweets)):
                if len(self.tweets[i].get_favourite()) < self.limit:
                    for tweet in tweets:
                        if tweet.id == self.tweets[i].id:
                            check_complete = False
                            ws_favorite.write(len(self.tweets[i].get_favourite()) + 2, i, tweets[i].favorite_count)
                            ws_retweet.write(len(self.tweets[i].get_retweet()) + 2, i, tweets[i].retweet_count)
                            self.tweets[i].add_favorite(tweets[i].favorite_count)
                            self.tweets[i].add_retweet(tweets[i].retweet_count)
                else:
                    finished += 1
            print("Log time - Ideal:", wait - self.time_interval, "Actual:", datetime.now(), "\nTweets- Completed:", finished, "In progress:", len(self.tweets) - finished, "Not started:", self.tweet_limit - len(self.tweets))
            if wait > datetime.now():
                time.sleep((wait - datetime.now()).seconds)
            wait = wait + self.time_interval
            wf.save(self.screen_name+'.xls')
        print("Process completed, output file is", self.screen_name+'.xls', "Total runtime:", str(datetime.now()-self.starttime))
