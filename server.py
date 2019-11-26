# -*- coding: utf-8 -*-
#--------------------------------------#
#    SERVER WITH FLASK / CELERY        #
#--------------------------------------#

import celery.utils
import os
import shutil
import time
from flask import Flask,render_template, request, send_from_directory, redirect, url_for
from celery import signature, chain, group
from celery_tasks import *

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = {YOUR UPLOAD_FOLDER}

#global variables
theQuery = ''
partial_res1 =''
partial_res2 =''

#---CELERY WORKFLOW---#
def celery_workflow(theQuery):

    workflow = (twitterQuery.s(theQuery) | group(uploadtoDropbox.s(), obtainSentiment.s()))
    launch1 = workflow.delay()
    partial_res1 = launch1.get()[1]

    workflow2 = (group (uploadtoDropbox.s(partial_res1),createPieChart.s(partial_res1)))
    launch2 = workflow2.delay()
    partial_res2 = launch2.get()[1]

    lastworkflow = uploadtoDropbox.s(partial_res2)
    launchfinal = lastworkflow.delay()


def workflow_download():

    tuplef1 = ('/raw_result_tweets.txt','texto_tweets.txt')
    tuplef2 = ('/tweets.csv','sentimiento_tweets.csv')
    tuplef3 = ('/sentimentanalysis_pie.html', 'grafica_sentimiento_tweets.html')

    #(file_local, file_cloud)
    workdown = group(downloadfromDropbox.si(tuplef1),downloadfromDropbox.si(tuplef2),downloadfromDropbox.si(tuplef3))
    res = workdown.apply_async()
    res.join()

#---Helper function---#
def after_download():

    dst1 = 'texto_tweets.txt'
    dst2 = 'sentimiento_tweets.csv'
    dst3 = 'grafica_sentimiento_tweets.html'

    common = {YOUR_DOWNLOAD_FOLDER}
    folder= '/SD-SentimentTwitterAnalysis'

    listdest = [dst1,dst2,dst3]

    for dst in listdest:
        newdst = common+dst
        infolder = folder+dst
        if os.path.exists(newdst) == True:
            print ('EXISTING FILE '+newdst)
            os.remove(infolder)
        else:
            shutil.move(dst,{YOUR_DOWNLOAD_FOLDER})





#---Defining FLASK Routes---#

#Root route
@app.route('/')
def home():
    return render_template('home.html', image_name = '/SD-SentimentTwitterAnalysisstatic/emojis.png')

#Loading route
@app.route('/loading')
def loading():
    global theQuery
    if request.method == 'POST':
        theQuery = request.form['query']
        return render_template('load.html')

    else:
        theQuery = request.args.get('query')
        return render_template('load.html')


#Route for running the workflow and showing results
@app.route('/results')
def results():
    global theQuery
    celery_workflow(theQuery)
    return render_template('results.html')

#Route for running the workflow and showing results
@app.route('/download')
def download():
    workflow_download()
    after_download()
    return render_template('bye.html')


#Route for serving pictures
@app.route('/static/<namepicture>')
def picturestatic(namepicture):
    return send_from_directory('templates/static',namepicture)


#---APPLICATION POINT---#
if __name__ == '__main__':
   app.run(debug = True)
