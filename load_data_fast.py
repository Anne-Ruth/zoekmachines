import datetime
import pandas as pd
from elasticsearch import Elasticsearch, helpers


# Create a dataframe for all questions of the goeievraag database.
qdf =  pd.read_csv('data/questions.csv', sep=',', header=None,
                   names=['questionId', 'date', 'userId', 'categoryId',
                  'question', 'description'], quotechar='"',
                   error_bad_lines=False, escapechar='\\', na_filter=False)

# Create a dataframe for all answers of the goeievraag database.
adf =  pd.read_csv('data/answers.csv', sep=',', header=None,
                   names=['answerId', 'date', 'userId', 'questionId',
                  'answer', 'thumbsDown', 'thumbsUp',
                  'isBestAnswer'], quotechar='"',
                   error_bad_lines=False, escapechar='\\', na_filter=False)

# Create a dataframe for all categories of the goeievraag database.
cdf =  pd.read_csv('data/categories.csv', sep=',', header=None,
                   names=['categoryId', 'parentId', 'category'],
                   quotechar='"',error_bad_lines=False,
                   escapechar='\\', na_filter=False)

# Create a dataframe for all users of the goeievraag database.
udf =  pd.read_csv('data/users.csv', sep=',', header=None,
                    names=['userId', 'registrationDate', 'expertise',
                    'bestAnswers'], quotechar='"',
                    error_bad_lines=False, escapechar='\\', na_filter=False)

# Parse all questions and make json documents to prepare for elasticsearch.
def create_questions_doc(panda):
    docs = []
    for i, row in panda.iterrows():
        date = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
        doc = {
            '_index' : "questions",
            '_type' : "question",
            '_id' : row['questionId'],
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

# Parse all answers and make json documents to prepare for elasticsearch.
def create_answers_doc(panda):
    docs = []
    for i, row in panda.iterrows():
        date = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
        doc = {
            '_index' : "answers",
            '_type' : "answer",
            '_id' : row['answerId'],
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

# Parse all categories and make json documents to prepare for elasticsearch.
def create_categories_doc(panda):
    docs = []
    for i, row in panda.iterrows():
        doc = {
            '_index' : "categories",
            '_type' : "category",
            '_id' : row['categoryId'],
            '_source' : {
                'categoryId' : row['categoryId'],
                'parentId' : row['parentId'],
                'category' : row['category']
            }
        }
        docs.append(doc)
    return docs

# Parse all users and make json documents to prepare for elasticsearch.
def create_users_doc(panda):
    docs = []
    for i, row in panda.iterrows():
        date = datetime.datetime.strptime(row['registrationDate'], '%Y-%m-%d %H:%M:%S')
        doc = {
            '_index' : "users",
            '_type' : "user",
            '_id' : row['userId'],
            '_source' : {
                'userId' : row['userId'],
                'registrationDate' : date,
                'expertise' : row['expertise'],
                'bestAnswers' : row['bestAnswers'],
            }
        }
        docs.append(doc)
    return docs

# Connect with elasticsearch
es = Elasticsearch(hosts=['http://localhost:9200/'])

# Check if documents with index ind already exists, if so it will be deleted.
def exists_check(ind):
    if es.indices.exists(index=ind):
        es.indices.delete(index=ind)
        print('Previous version of index',ind,'has been removed')

exists_check("questions")
exists_check("answers")
exists_check("categories")
exists_check("users")

# Load questions in elasticsearch
print("Loading questions")
q_docs = create_questions_doc(qdf)
helpers.bulk(es, q_docs)

# Load answers in elasticsearch
print("Loading answers")
a_docs = create_answers_doc(adf)
helpers.bulk(es, a_docs)

# Load categories in elasticsearch
print("Loading categories")
c_docs = create_categories_doc(cdf)
helpers.bulk(es, c_docs)

# Load users in elasticsearch
print("Loading users")
u_docs = create_users_doc(udf)
helpers.bulk(es, u_docs)

# refresh all indexes.
es.indices.refresh(index='questions')
es.indices.refresh(index='answers')
es.indices.refresh(index='categories')
es.indices.refresh(index='users')
