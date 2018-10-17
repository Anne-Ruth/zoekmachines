from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/result',methods = ['POST'])
def result():
    keyword = request.form['search']

    body = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["question", "description"]
            }
        }
    }

    res = es.search(index="questions", size=10000, doc_type="question", body=body)
    return render_template("result.html",result = res)

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
    return render_template("answers.html",data = q_res,result = a_res)

if __name__ == '__main__':
   app.run(debug = True)
