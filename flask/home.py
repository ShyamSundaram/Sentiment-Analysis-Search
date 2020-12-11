from flask import Flask, render_template, jsonify, json, request
import toneanalyzer
from random import sample

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/data',methods=["GET","POST"])
def data():
    t=toneanalyzer.get_tweets2('USA',5)
    #t1=toneanalyzer.get_tweets2('UK',5)
    x,y=toneanalyzer.analyze3(t)
    #x1,y1=toneanalyzer.analyze3(t1)
    
    data={
        "x":x,
        "y":y
        #"y1":y1
    }
    return data
    #return jsonify({'x':x,'y':y})
    #return jsonify({'results':sample(range(1,10),5)})

@app.route('/data1',methods=["GET","POST"])
def data1():
    t=toneanalyzer.trending("USA",5)
    x,y=toneanalyzer.analyze4(t)

    data={
        "x":x,"y":y
    }
    return data

@app.route('/data2/<cnt>',methods=["GET","POST"])
def data2(cnt):
    t=toneanalyzer.trending(cnt,10)
    x,y=toneanalyzer.analyze5(t)
    l=toneanalyzer.analyze6(t)
    data={
        "x":x,"y":y,"l":l
    }
    return data

@app.route('/data3/<cnt>/<top>',methods=["GET","POST"])
def data3(cnt,top):
    '''if request.method=="POST":
        country=request.form['country']
        t=toneanalyzer.get_tweets2(country,5)
        x,y=toneanalyzer.analyze3(t)
        #x1,y1=toneanalyzer.analyze3(t1)'''
    #cnt=cnt.split('/')
    t=toneanalyzer.get_tweets2(cnt,100,top)
    x,y=toneanalyzer.analyze3(t)
    l=toneanalyzer.analyze_pol_and_sent(t)
    
    data={
        "x":x,
        "y":y,
        "l":l
    }
    return data

@app.route('/news/<top>',methods=["GET","POST"])
def news(top):
    x,y=toneanalyzer.get_news(top)
    data={
        "headlines":x,
        "description":y
    }
    return data


if __name__=='__main__':
    app.run(debug=True)