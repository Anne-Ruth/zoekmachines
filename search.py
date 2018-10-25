from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
import nltk

from wordcloud import WordCloud
from nltk.corpus import stopwords

from collections import Counter
from collections import defaultdict
from datetime import datetime as dt
from datetime import timedelta

class Settings:
    def __init__(self):
        self.title = 'EEND EEND GA'
        self.subtitle = 'Er bestaan geen domme vragen'
        self.search = 'Zoek'
        self.place = 'Goeievraag?'

class Chart:
    def __init__(self):
        self.data = defaultdict(Counter)
        self.name = ''

    def create_data(self, result, data_type):
        self.data[data_type].clear()
        for hit in result['hits']['hits']:
            if data_type == 'date':
                date = dt.strptime(hit['_source'][data_type], '%Y-%m-%dT%H:%M:%S')
                self.data[data_type][date.strftime("%Y")] += 1
            else:
                self.data[data_type][hit['_source'][data_type]] += 1

    def setName(self, name):
        self.name = name

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index():
    body = {
        "query": {
            "match_all" : {}
        }
    }
    res = es.search(index="categories", size=10000, doc_type="category", body=body)
    return render_template('index.html', cat = res, set = settings)

@app.route('/result',methods = ['POST'])
def result():
    start_time = dt.now()
    keyword = request.form['search']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    category = request.form['categorylist']
    qtype = request.form['qtype']

    booty = {
        "query": {
            "match_all" : {}
        }
    }

    if qtype == "user":
        body = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["expertise"]
                }
            }
        }
        res = es.search(index="users", size=10000, doc_type="user", body=body)
        end_time = dt.now()
        time_delta = end_time - start_time
        time_delta = timedelta(days=0, seconds=time_delta.seconds, microseconds=time_delta.microseconds)
        cat = es.search(index="categories", size=10000, doc_type="category", body=booty)
        return render_template("result.html",result=res, cat=cat, set = settings, td = time_delta, qtype=qtype)#, graph = graph)


    else:
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

        end_time = dt.now()
        time_delta = end_time - start_time
        time_delta = timedelta(days=0, seconds=time_delta.seconds, microseconds=time_delta.microseconds)

        DutchStop= stopwords.words('dutch')
        tes = []
        for item in res['hits']['hits']:
            tokens = Counter([w for w in nltk.word_tokenize(item['_source']['question'].lower()) if w.isalpha() and not w in set(DutchStop)])
            tes.append(tokens.keys())
        flat_list = [item for sublist in tes for item in sublist]
        flat_list = Counter(flat_list)
        if len(flat_list) > 0:
            wc = WordCloud(max_font_size=50, max_words=100, background_color="white").generate_from_frequencies(flat_list)
            wc.to_file("static/img/wordcloud.png")


        cat = es.search(index="categories", size=10000, doc_type="category", body=booty)
        chart.create_data(res, 'date')
        chart.setName(keyword)
        data_type = 'date'
        chart_labels = []
        chart_values = []
        max_value = None

        for i in chart.data[data_type]:
            chart_labels.append(i)
            chart_values.append(chart.data[data_type][i])

        if len(chart_values) > 0:
            max_value = max(chart_values)

        graph = [chart_labels, chart_values, max_value]

        return render_template("result.html",result=res, cat=cat, wordcloud=flat_list,path = "../static/img/wordcloud.png", set = settings, td = time_delta, qtype=qtype, graph = graph)

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

    a_res = es.search(index="answers", size=10000, doc_type="answer", body=body)

    DutchStop= stopwords.words('dutch')
    tes = []
    for item in a_res['hits']['hits']:
        tokens = Counter([w for w in nltk.word_tokenize(item['_source']['answer'].lower()) if w.isalpha() and not w in set(DutchStop)])
        tes.append(tokens.keys())
    flat_list = [item for sublist in tes for item in sublist]
    flat_list = Counter(flat_list)
    if len(flat_list) > 0:
        wc = WordCloud(max_font_size=50, max_words=100, background_color="white").generate_from_frequencies(flat_list)
        wc.to_file("static/img/wordcloud.png")
    return render_template("answers.html",data = q_res,result = a_res, wordcloud = flat_list,path = "../static/img/wordcloud.png", set = settings)

@app.route('/user/<int:user_Id>')
def users(user_Id):
    q_res = es.get(index="users", doc_type="user", id=user_Id)

    body={
        "size": 1000,
        "query": {
            "match": {
                "userId": user_Id
            }
        }
    }

    a_res = es.search(index="answers", size=10000, doc_type="answer", body=body)

    DutchStop= stopwords.words('dutch')
    tes = []
    for item in a_res['hits']['hits']:
        tokens = Counter([w for w in nltk.word_tokenize(item['_source']['answer'].lower()) if w.isalpha() and not w in set(DutchStop)])
        tes.append(tokens.keys())
    flat_list = [item for sublist in tes for item in sublist]
    flat_list = Counter(flat_list)
    if len(flat_list) > 0:
        wc = WordCloud(max_font_size=50, max_words=100, background_color="white").generate_from_frequencies(flat_list)
        wc.to_file("static/img/wordcloud.png")
    return render_template("users.html",data = q_res,result = a_res, wordcloud = flat_list,path = "../static/img/wordcloud.png", set = settings)

@app.route('/u_filters/<int:user_Id>', methods = ['POST'])
def u_filters(user_Id):
    likes = request.form['likes']
    if request.form.get('best_answer'):
        best = True
    else:
        best = False
    q_res = es.get(index="users", doc_type="user", id=user_Id)

    if request.method == "POST":

        booty = {
            "query": {
                "match_all" : {}
            }
        }
        if not likes:
            if not best:
                body={
                    "query": {
                        "match": {
                            "userId": user_Id
                        }
                    }
                }
            else:
                body = {
                   "query" : {
                      "constant_score" : {
                         "filter" : {
                            "bool" : {
                                "must" : [
                                    { "term" : {"userId" : user_Id}},
                                    { "term" : {"isBestAnswer" : 1}}
                                  ]
                                }
                            }
                        }
                    }
                }
        elif not best:
            body = {
               "query" : {
                  "constant_score" : {
                     "filter" : {
                        "bool" : {
                            "must" : [
                                { "term" : {"userId" : user_Id}}
                              ],
                            "should": [
                                { "range": {"thumbsUp" : { "gte": likes }}}
                              ]
                            }
                        }
                    }
                }
            }
        else:
            body = {
               "query" : {
                  "constant_score" : {
                     "filter" : {
                        "bool" : {
                            "must" : [
                                { "term" : {"userId" : user_Id}},
                                { "term" : {"isBestAnswer" : 1}},
                              ],
                             "should": [
                                 { "range": {"thumbsUp" : { "gte": likes }}}
                               ]
                            }
                        }
                    }
                }
            }

        a_res = es.search(index="answers", size=10000, doc_type="answer", body=body)

        DutchStop= stopwords.words('dutch')
        tes = []
        for item in a_res['hits']['hits']:
            tokens = Counter([w for w in nltk.word_tokenize(item['_source']['answer'].lower()) if w.isalpha() and not w in set(DutchStop)])
            tes.append(tokens.keys())
        flat_list = [item for sublist in tes for item in sublist]
        flat_list = Counter(flat_list)
        if len(flat_list) > 0:
            wc = WordCloud(max_font_size=50, max_words=100, background_color="white").generate_from_frequencies(flat_list)
            wc.to_file("static/img/wordcloud.png")


        cat = es.search(index="categories", size=10000, doc_type="category", body=booty)
        return render_template("users.html",data = q_res,result = a_res, wordcloud = flat_list,path = "../static/img/wordcloud.png", set = settings)


@app.route('/a_filters/<int:question_Id>', methods = ['POST'])
def a_filters(question_Id):
    likes = request.form['likes']
    if request.form.get('best_answer'):
        best = True
    else:
        best = False
    q_res = es.get(index="questions", doc_type="question", id=question_Id)
    if request.method == "POST":

        booty = {
            "query": {
                "match_all" : {}
            }
        }
        if not likes:
            if not best:
                body={
                    "query": {
                        "match": {
                            "questionId": question_Id
                        }
                    }
                }
            else:
                body = {
                   "query" : {
                      "constant_score" : {
                         "filter" : {
                            "bool" : {
                                "must" : [
                                    { "term" : {"questionId" : question_Id}},
                                    { "term" : {"isBestAnswer" : 1}}
                                  ]
                                }
                            }
                        }
                    }
                }
        elif not best:
            body = {
               "query" : {
                  "constant_score" : {
                     "filter" : {
                        "bool" : {
                            "must" : [
                                { "term" : {"questionId" : question_Id}}
                              ],
                            "should": [
                                { "range": {"thumbsUp" : { "gte": likes }}}
                              ]
                            }
                        }
                    }
                }
            }
        else:
            body = {
               "query" : {
                  "constant_score" : {
                     "filter" : {
                        "bool" : {
                            "must" : [
                                { "term" : {"questionId" : question_Id}},
                                { "term" : {"isBestAnswer" : 1}},
                              ],
                             "should": [
                                 { "range": {"thumbsUp" : { "gte": likes }}}
                               ]
                            }
                        }
                    }
                }
            }



        a_res = es.search(index="answers", size=10000, doc_type="answer", body=body)
        cat = es.search(index="categories", size=10000, doc_type="category", body=booty)
        return render_template("answers.html",data = q_res,result = a_res, cat=cat, set = settings)


@app.route("/timeline")
def timeline():
    labels = []
    values = []

    data_type = request.args.get('data_type', default = 'date', type = str)
    for i in chart.data[data_type]:
        labels.append(i)
        values.append(chart.data[data_type][i])
    max_value = max(values)
    return render_template('timeline.html', values=values, labels=labels, max=max_value, name=chart.name)

if __name__ == '__main__':
    settings = Settings()
    chart = Chart()
    app.run(debug = True)
