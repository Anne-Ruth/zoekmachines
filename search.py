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

if __name__ == '__main__':
   app.run(debug = True)
