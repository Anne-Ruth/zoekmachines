from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])ye

@app.route('/')
def student():
   return render_template('index.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("result.html",result = result)

if __name__ == '__main__':
   app.run(debug = True)

def simple_search(es, query):
    return es.search(index="goeievraag", doc_type="questions", body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["question", "description"]
            }
        }
    })

# searchresult = simple_search(es, result)
# print(searchresult)
