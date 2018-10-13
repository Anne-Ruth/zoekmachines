import os 
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
import json

def initialize():
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    questions_path = dir_path + "/goeievraag/questions.csv"
    answers_path = dir_path + "/goeievraag/answers.csv"
    users_path = dir_path + "/goeievraag/users.csv"
    
    # the questions
    qdf=pd.read_csv(questions_path,error_bad_lines=False , header=None, 
                index_col=0,parse_dates=[1], quotechar='"', quoting=2)
                    
    adf=0#pd.read_csv(answers_path,error_bad_lines=False , header=None, 
         #       parse_dates=[1], quotechar='"', quoting=2)
             
    udf=0#pd.read_csv(users_path,error_bad_lines=False , header=None, 
         #       parse_dates=[1], quotechar='"', quoting=2)
                    
    return qdf, adf, udf

# validate the document
def valid(document):
    
    for i in document:
        if not i == 'description' and document.get(i) is None:
            return False
    return True;
    
# store the data for elastic search to use
def store_in_es(es, data_index, data_type, data):
    
    # process every document seperately
    for i in data:
        data_id = int(i)
        doc = data.get(i)
        
        # skip invalid documents
        if not valid(doc): 
            print(data_id, ": ", doc) # print the invalid document (only for debugging/testing)
            continue
            
        # store the document
        es.index(index=data_index, doc_type=data_type, id=data_id, body=doc)
        es.indices.refresh(index=data_index, doc_type=data_type)
    
# read the files
qdf, adf, udf = initialize()

# clean up
qdf=qdf.dropna(subset=[4])  # drop lines in which the question field is empty anyway
qdf.index = np.arange(1, len(qdf)+1) # set the index to integers
qdf[1]= pd.to_datetime(qdf[1], errors='coerce') # parse dates 
qdf.columns = ["date", "user","category","question","description"]

# get the json string
qstring = qdf.to_json(orient='index')

# convert to actual json
qjson = json.loads(qstring)

#print(qjson.get("186954"))

es = Elasticsearch()

store_in_es(es, "gv", "question", qjson)
