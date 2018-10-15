import json,  csv, datetime
from elasticsearch import Elasticsearch

def load_questions(es, directory, doc , n):
    with open(directory, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            if len(row) is n:
                try:
                    if es.exists("goeievraag", doc, int(row[0])):
                        continue
                    date = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    data = {
                        "questionId": int(row[0]),
                        "date": date,
                        "userId": int(row[2]),
                        "categoryId": int(row[3]),
                        "question": str(row[4]),
                        "description": str(row[5])
                    }
                except ValueError:
                    print("Invalid", row[0])
                    continue
                es.create("goeievraag", doc, int(row[0]), data)

def load_answers(es, directory,doc, n):
    with open(directory, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            if len(row) is n:
                try:
                    if es.exists("goeievraag", doc, int(row[0])):
                        continue
                    date = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    data = {
                        "answerId": int(row[0]),
                        "date": date,
                        "userId": int(row[2]),
                        "questionId": int(row[3]),
                        "answer": str(row[4]),
                        "thumbsDown": int(row[5]),
                        "thumbsUp": int(row[6]),
                        "isBestAnswer": int(row[7])
                    }
                except ValueError:
                    print("Invalid", row[0])
                    continue
                es.create("goeievraag", doc, int(row[0]), data)

def load_users(es, directory, doc , n):
    with open(directory, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            if len(row) is n:
                try:
                    if es.exists("goeievraag", doc, int(row[0])):
                        continue
                    date = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    data = {
                        "userId": int(row[0]),
                        "registrationDate": date,
                        "expertise": str(row[2]),
                        "bestAnswers": int(row[3])
                    }
                except ValueError:
                    print("Invalid", row[0])
                    continue
                es.create("goeievraag", doc, int(row[0]), data)

def load_categories(es, directory, doc , n):
    with open(directory, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            if len(row) is n:
                try:
                    if es.exists("goeievraag", doc, int(row[0])):
                        continue
                    data = {
                        "categoryId": int(row[0]),
                        "parentId": int(row[1]),
                        "category": str(row[2])
                    }
                except ValueError:
                    print("Invalid", row[0])
                    continue
                es.create("goeievraag", doc, int(row[0]), data)

def load_data(es):
    print("Loading questions")
    load_questions(es, "data/questions.csv", "questions", 6)
    print("Loading answers")
    load_answers(es, "data/answers.csv", "answers", 8)
    print("Loading categories")
    load_categories(es, "data/categories.csv", "categories", 3)
    print("Loading users")
    load_users(es, "data/users.csv", "users", 4)

es = Elasticsearch()
load_data(es)
