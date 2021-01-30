from django.shortcuts import render
from django.http import HttpResponse
from .forms import HandleForm

import nltk
from nltk.corpus import twitter_samples
from nltk.twitter.common import json2csv
from nltk.tokenize import TweetTokenizer

import pandas as pd

from string import punctuation

def normalization(word_list):
        lem = nltk.WordNetLemmatizer()
        normalized_word = []
        for word in word_list:
            normalized_text = lem.lemmatize(word,'v')
            normalized_word.append(normalized_text)
        return normalized_word

def index(request):
    return HttpResponse("Hello, world. You're at the enter_handle index.")

def get_handle(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = HandleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # For now, we use the twitter "userid" instead of
            ## the twitter handle. User ID to Handle conversions can
            ## be done at https://tweeterid.com/

            handle = int(form.cleaned_data['handle'])

            # Use a sample from the Twitter corpus
            input_file = twitter_samples.abspath("tweets.20150430-223406.json")

            # Convert the relevant fields in the json to a CSV text file
            with open(input_file) as fp:
                json2csv(fp, 'tweets_text.csv',
                        ['created_at', 'favorite_count', 'id', 'in_reply_to_status_id', 
                        'in_reply_to_user_id', 'retweet_count', 'retweeted', 
                        'text', 'truncated', 'user.id'])

            # Read the CSV into a Pandas dataframe
            tweets = pd.read_csv('tweets_text.csv', index_col=2, header=0, encoding="utf8")

            # nltk stuff

            # Only look at tweets from a specific user
            tweets = tweets.loc[tweets['user.id'] == handle]['text']
            
            # Convert the tweets into a text string.
            raw_text1 = ""
            for tweet in tweets:
                raw_text1 = raw_text1 + tweet + "\n"
            
            # Tokenize the tweets into separate words, hashtags etc.
            tknzr = TweetTokenizer()
            text1 = nltk.Text(tknzr.tokenize(raw_text1))
            
            # Stopwords are common English words which are to be ignored
            stopwords = nltk.corpus.stopwords.words('english')
            stopwords.append('…')
            stopwords.append('rt')
            stopwords.append('')
            
            # Lemmatize the text
            nom_text1 = normalization(text1)
            
            # Strip punctuation and stopwords, and compute a frequency distribution of all the words.
            allWordExceptStopDistAndNoms = nltk.FreqDist(
                    w.lower().rstrip(punctuation) 
                    for w in nom_text1 if 
                    w[0] != '#' and w.lower() not in stopwords 
                    and len(w) > 1)
            
            # Hashtags are just words which start with "#'
            all_hashtags = nltk.FreqDist(w.lower().rstrip(punctuation) for w in text1 if w.lower() not in stopwords and w[0] == '#')

            # back to Django
            # bundle all the data into a "context" to send
            context = {'handle': str(handle), 
                    'tweet_list': tweets.tolist(), 
                    'most_common_hashtags': all_hashtags.most_common(10),
                    'most_common_words': allWordExceptStopDistAndNoms.most_common(10)}
            return render(request, 'enter_handle/analyze_tweets.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HandleForm()

    return render(request, 'enter_handle/handle.html', {'form': form})
