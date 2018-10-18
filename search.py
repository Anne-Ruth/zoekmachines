from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch

from collections import Counter
from datetime import datetime as dt

class Timeline:
    def __init__(self):
        self.data = Counter()
        self.name = ''

    def create_timeline(self, result):
        dates = []
        for hit in result['hits']['hits']:
            date = dt.strptime(hit['_source']['date'], '%Y-%m-%dT%H:%M:%S')
            self.data[date.strftime("%Y")] += 1

    def setName(self, name):
        self.name = name

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

@app.route('/')
def index():
    body = {
        "query": {
            "match_all" : {}
        }
    }
    res = es.search(index="categories", size=10000, doc_type="category", body=body)
    return render_template('index.html', cat = res)

@app.route('/result',methods = ['POST'])
def result():
    keyword = request.form['search']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    category = request.form['categorylist']
    booty = {
        "query": {
            "match_all" : {}
        }
    }

    if not startdate:
        if not enddate:
            if not category:
                body = {
                    "query": {
                        "multi_match": {
                            "query": keyword,
                            "fields": ["question", "description"]
                        }
                    }
                }
            else:
                body = {
                    "query":{
                        "bool":{
                            "must":{
                                "multi_match":{
                                    "query": keyword,
                                    "fields":[ "question","description" ]
                                }
                            },
                            "filter": [{
                                "bool" : {
                                    "must" : [
                                        {
                                            "multi_match": {
                                                "query": category,
                                                "fields": ["categoryId"]
                                            }
                                        }
                                    ]
                                }
                            }]
                        }
                    }
                }

    elif not category:
        body = {
            "query":{
                "bool":{
                    "must":{
                        "multi_match":{
                            "query": keyword,
                            "fields":[ "question","description" ]
                        }
                    },
                    "filter": [{
                        "bool" : {
                            "must" : [
                                {
                                    "range": {
                                        "date": {
                                            "gte" : startdate,
                                            "lte" : enddate
                                        }
                                    }
                                }
                            ]
                        }
                    }]
                }
            }
        }

    else:
        body = {
            "query":{
                "bool":{
                    "must":{
                        "multi_match":{
                            "query": keyword,
                            "fields":[ "question","description" ]
                        }
                    },
                    "filter": [{
                        "bool" : {
                            "should" : [
                                {
                                    "range": {
                                        "date": {
                                            "gte" : startdate,
                                            "lte" : enddate
                                        }
                                    }
                                },
                                {"multi_match": {
                                    "query": category,
                                    "fields": ["categoryId"]
                                }}
                            ]
                        }
                    }]
                }
            }
        }

    res = es.search(index="questions", size=10000, doc_type="question", body=body)
    cat = es.search(index="categories", size=10000, doc_type="category", body=booty)
    tl.create_timeline(res)
    tl.setName(keyword)
    return render_template("result.html",result = res, cat=cat)

@app.route('/answer/<int:question_Id>')
def answers(question_Id):
    q_res = es.get(index="questions", doc_type="question", id=question_Id)

    body={
        "size": 1000,
        "query": {
            "match": {
                "questionId": question_Id
            }
        }
    }

    booty = {
        "query": {
            "match_all" : {}
        }
    }

    a_res = es.search(index="answers", size=10000, doc_type="answer", body=body)
    cat = es.search(index="categories", size=10000, doc_type="category", body=booty)
    return render_template("answers.html",data = q_res,result = a_res, cat=cat)

@app.route("/timeline")
def timeline():
    labels = []
    values = []

    for i in tl.data:
        labels.append(i)
        values.append(tl.data[i])
    max_value = max(values)
    # labels = ["January","February","March","April","May","June","July","August"]
    # values = [10,9,8,7,6,4,7,8]
    return render_template('timeline.html', values=values, labels=labels, max=max_value, name=tl.name)

if __name__ == '__main__':
    tl = Timeline()
    app.run(debug = True)
