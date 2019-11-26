
# -*- coding: utf-8 -*-
#! /usr/bin/env python
import sys
import tweepy
import dropbox
import shutil
import csv
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import meaningcloud
import pandas as pd
import plotly.tools
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
from plotly.offline import iplot,plot

###########################################################################################
#   TWITTER SEARCH FUNCTION

def recolectingTweetsQuery(query):
    consumer_key={YOUR_CONSUMER_KEY}
    consumer_secret={YOUR_CONSUMER_SECRET}
    access_token={YOUR_ACCESS_TOKEN}
    access_token_secret={YOUR_ACCESS_TOKEN_SECRET}

    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

    #Error handling
    if (not api):
        print ("Problem Connecting to API")

    searchQuery = query

    maxTweets = 50
    #The twitter Search API allows up to 100 tweets per query
    tweetsPerQry = 100
    tweetCount = 0

    fileNameRawTweets =  'raw_result_tweets.txt'
    filePath = '/'+fileNameRawTweets

    with open(fileNameRawTweets, 'w') as f:

        for tweet in tweepy.Cursor(api.search,q=searchQuery,lang='es',tweet_mode='extended').items(maxTweets):
            text=tweet.full_text.encode('utf-8');
            if(text[0:2]!='RT'):
                f.write(text.replace('\n',' ')+'\n')
            else:
                f.write("RT: "+tweet.retweeted_status.full_text.encode('utf-8').replace('\n',' ')+'\n')
            tweetCount += 1

        #Display how many tweets we have collected
        print("Downloaded {0} tweets".format(tweetCount))

    tupleFiles = (fileNameRawTweets,filePath)
    return tupleFiles

###########################################################################################
#   DROPBOX UPLOADING FILES FUNCTION

def upload_file(tupleFiles):

    file_from = tupleFiles[0]
    file_to = tupleFiles[1]
    Token = {YOUR_DROPBOX_TOKEN}

    if (len(Token) == 0):
        sys.exit("Error with Access Token ")

    dbx = dropbox.Dropbox(Token)

    try:
        dbx.users_get_current_account()
    except AuthError as err:
        sys.exit("Must be an error with Acces Token.")

    with open(file_from, 'rb') as f:
        try:
            dbx.files_upload(f.read(), file_to, mode=WriteMode('overwrite'))
        except ApiError as err:
            if (err.error.is_path() and
                    err.error.get_path().reason.is_insufficient_space()):
                sys.exit("Insufficient space! You cannot upload new files.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()
    return tupleFiles

###########################################################################################
#   DROPBOX UPLOADING FILES FUNCTION

#('/raw_result_tweets.txt','raw_result_tweets.txt')
def download_file(tupleFiles):

    file_cloud = tupleFiles[0]
    file_local = tupleFiles[1]
   Token = {YOUR_DROPBOX_TOKEN}

    dbx = dropbox.Dropbox(Token)

    try:
        dbx.users_get_current_account()
    except AuthError as err:
        sys.exit("Error with Access Token ")

    #ArchivoSubido = '/hola.txt' #Poner siempre la / que si no peta.
    dbx.files_download_to_file(file_local, file_cloud)

###########################################################################################
#   MEANINGCLOUD SENTIMENT ANALYSIS FUNCTION

def meaning_sentiment(tupleFiles):

    rawtweets = tupleFiles[0]
    license_key = {YOUR_MEANINGCLOUD_LICENSE_KEY}

    filenameCSV = 'tweets.csv'
    filepathCSV = '/'+filenameCSV

    with open(filenameCSV, 'w') as csv_file:
        fieldnames = ['sentiment', 'tweet']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        with open(rawtweets, 'r') as file_tweets:
            for line in file_tweets.readlines():
                sentiment_response = meaningcloud.SentimentResponse(meaningcloud.SentimentRequest(license_key, lang='es', txt=line, txtf='plain').sendReq())
                s = sentiment_response.getGlobalScoreTag()
                writer.writerow({'sentiment': s , 'tweet': line})

    tupleFilesCSV = (filenameCSV,filepathCSV)
    return tupleFilesCSV

##########################################################################################
#   FUNCTION FOR CREATING RESULTS.html
def insertGraphicIntoHTML(div_script):

    string1='<!DOCTYPE html><html lang="es"><head><meta http-equiv="content-type" content="text/html; charset=utf-8"><title>Sentoment Analysis </title><style type="text/css">#Title {font-family: "Gotham Bold";text-align: center;font-size: x-large;color: #1f2ea4;font-weight: bold;float: none;display: grid;}#myframe{position: relative;width: 1424px;height: 739px;}.textcreators {font-family: "Gotham Bold";text-align: center;}</style></head><body id="Title"><p> TWITTER SEARCH SENTIMENT ANALYSIS <span style="font-family: monospace;"></span></p>'

    string2='<form action="http://localhost:5000/download"><input type="submit" value="DESCARGAR ARCHIVOS" /></form><p class="textcreators">Sistemas Distribuidos - Universidad de Cadiz 2017/2018 </p><p class="textcreators">Desarrollado por Miguel Angel Alvarez Garcia y Ana Gomez Gonzalez </p></body></html>'

    finalstring=string1+div_script+string2

    with open('results.html','w+') as ftemp:
        ftemp.write(finalstring)


###########################################################################################
#   PLOTLY PIE CHART DRAWING FUNCTION
def plotly_piechart(tupleFiles):

    read_from = tupleFiles[0]

    py.sign_in({YOUR_USER}, {YOUR_KEY})
    plotly.tools.set_config_file(world_readable=False, sharing='private')

    df = pd.read_csv(read_from)
    data_dict = df['sentiment'].value_counts().to_dict()

    l = ('NONE: Sin sentimiento','N+: Fuertemente negativo','N: Negativo','P: Positivo', 'P+: Fuertemente positivo', 'NEU: Neutral')
    labels =list(l)
    values = data_dict.values()


    trace = {
      "hole": 0,
      "labels": labels,
      "labelssrc": "angoglez:5:22434e",
      "pull": 0,
      "type": "pie",
      "uid": "fdb1d3",
      "values": values,
      "valuessrc": "angoglez:5:f53641"
    }
    data = Data([trace])
    layout = {
      "autosize": True,
      "legend": {
        "x": 0.78,
        "y": 1,
        "borderwidth": 0.3,
        "font": {"size": 14}
      },
      "margin": {"pad": 20}
    }

    fig = Figure(data=data, layout=layout)

    html_filename = 'sentimentanalysis_pie.html'
    plotly.offline.plot(fig,filename ='sentimentanalysis_pie.html',auto_open=False,image = 'png', image_filename = 'sentimentanalysis_pie.png')
    div_result = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    div_result = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'+div_result

    with open('created_PieChart.html','w') as f:
        f.write(div_result)

    insertGraphicIntoHTML(div_result)
    shutil.move('SD-SentimentTwitterAnalysis/results.html','SD-SentimentTwitterAnalysis/templates/results.html')

    tupleFilesHTML = (html_filename,'/'+html_filename)
    return tupleFilesHTML
