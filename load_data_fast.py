import json, datetime
import pandas as pd
from elasticsearch import Elasticsearch, helpers

qdf =  pd.read_csv('data/questions.csv', sep=',', header=None,
                   names=['questionId', 'date', 'userId', 'categoryId',
                  'question', 'description'], quotechar='"',
                   error_bad_lines=False, escapechar='\\', na_filter=False)

adf =  pd.read_csv('data/answers.csv', sep=',', header=None,
                   names=['answerId', 'date', 'userId', 'questionId',
                  'answer', 'thumbsDown', 'thumbsUp',
                  'isBestAnswer'], quotechar='"',
                   error_bad_lines=False, escapechar='\\', na_filter=False)

cdf =  pd.read_csv('data/categories.csv', sep=',', header=None,
                   names=['categoryId', 'parentId', 'category'],
                   quotechar='"',error_bad_lines=False,
                   escapechar='\\', na_filter=False)

udf =  pd.read_csv('data/users.csv', sep=',', header=None,
                    names=['userId', 'registrationDate', 'expertise',
                    'bestAnswers'], quotechar='"',
                    error_bad_lines=False, escapechar='\\', na_filter=False)

def create_questions_doc(panda):
    docs = []
    for index, row in qdf.iterrows():
        date = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
        doc = {
            '_index' : "questions",
            '_type' : "question",
            '_source' : {
                'questionId' : row['questionId'],
                'date' : date,
                'userId' : row['userId'],
                'categoryId' : row['categoryId'],
                'question' : row['question'],
                'description' : row['description']
            }
        }
        docs.append(doc)
    return docs

def create_answers_doc(panda):
    docs = []
    for index, row in qdf.iterrows():
        date = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
        doc = {
            '_index' : "answers",
            '_type' : "answer",
            '_source' : {
                'answerId' : row['answerId'],
                'date' : date,
                'userId' : row['userId'],
                'questionId' : row['questionId'],
                'answer' : row['answer'],
                'thumbsDown' : row['thumbsDown'],
                'thumbsUp' : row['thumbsUp'],
                'isBestAnswer' : row['isBestAnswer']
            }
        }
        docs.append(doc)
    return docs

def create_categories_doc(panda):
    docs = []
    for index, row in qdf.iterrows():
        doc = {
            '_index' : "categories",
            '_type' : "category",
            '_source' : {
                'categoryId' : row['categoryId'],
                'parentId' : row['parentId'],
                'category' : row['category']
            }
        }
        docs.append(doc)
    return docs

def create_users_doc(panda):
    docs = []
    for i, row in qdf.iterrows():
        date = datetime.datetime.strptime(row['registrationDate'], '%Y-%m-%d %H:%M:%S')
        doc = {
            '_index' : "users",
            '_type' : "user",
            '_source' : {
                'userId' : row['userId'],
                'registrationDate' : date,
                'expertise' : row['expertise'],
                'bestAnswers' : row['bestAnswers'],
            }
        }
        docs.append(doc)
    return docs

# init elastic search API
es = Elasticsearch(hosts=['http://localhost:9200/'])

# if es.indices.exists(index='questions'):
#     es.indices.delete(index='index')#, ignore=[400, 404])
#     print('Previous version of index removed!\nReplacing with new!')


# index file
print("Loading questions")
q_docs = create_questions_doc(qdf)
helpers.bulk(es, q_docs)
print("Loading answers")
a_docs = create_answers_doc(adf)
helpers.bulk(es, a_docs)
print("Loading categories")
c_docs = create_categories_doc(cdf)
helpers.bulk(es, c_docs)
print("Loading users")
u_docs = create_users_doc(udf)
helpers.bulk(es, u_docs)

# refresh to have the index take effect
es.indices.refresh(index='questions')
es.indices.refresh(index='answers')
es.indices.refresh(index='categories')
es.indices.refresh(index='users')
