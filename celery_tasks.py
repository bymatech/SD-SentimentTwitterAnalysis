# -*- coding: utf-8 -*-

from celery import Celery, task
import time
import secondary_tasks

#Using AMQP as broker and RPC as backend point.
app = Celery("tasks", backend="rpc://",
broker="pyamqp://guest@localhost//")

#------- CELERY TASKS -------#

@app.task(no_ack=True)
def twitterQuery(query):
    tupleFiles = secondary_tasks.recolectingTweetsQuery(query)
    print('Recolect tweets related with query: DONE.')
    return tupleFiles

@app.task(no_ack=True)
def uploadtoDropbox(tupleFiles):
    secondary_tasks.upload_file(tupleFiles)
    print( tupleFiles[0] + ' uploaded to Dropbox: DONE.')

@app.task(no_ack=True)
def downloadfromDropbox(tupleFiles):
    secondary_tasks.download_file(tupleFiles)
    time.sleep(2)
    print( tupleFiles[1] + ' downloaded from Dropbox: DONE.')

@app.task(no_ack=True)
def obtainSentiment(tupleFiles):
    tupleFilesCSV = secondary_tasks.meaning_sentiment(tupleFiles)
    print ('Created ' +tupleFilesCSV[0]+' CSV file containing sentiment analysis data: DONE.')
    return tupleFilesCSV

@app.task(no_ack=True)
def createPieChart(tupleFilesCSV):
    tupleFilesHTML = secondary_tasks.plotly_piechart(tupleFilesCSV)
    print ('Created ' +tupleFilesHTML[1]+' HTML file containing data visualization in pie chart: DONE.')
    return tupleFilesHTML
