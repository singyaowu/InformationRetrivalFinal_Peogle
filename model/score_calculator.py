import csv
import json
import random
import operator
from argparse import ArgumentParser
from collections import Counter
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from keras.models import load_model
import jieba

punctuation = [
    "，", "、", "　", "《", "〈", "＜", "<", ",", "。", "・", "·", "》", "〉", "＞", ">", ".",
    "！","？", "/", "／", "÷", "?", "：", "；", ":", ";", "“", "”", "\"", "〃", "'", " ",
    "『", "「", "【", "〔", "［", "{", "[", "』", "」", "】", "〕", "］", "}", "]","：", "｜", "|", "\\",
    "~", "!", "@", "#", "$#", "%", "^", "&", "*", "(", ")", "_", "__", "+", "=", "2025"
]

w2v_model = Word2Vec.load('model/w2v.model')
model = load_model('model/final.h5')

def okapi_normalization(tf, doc_length, doc_cnt):
    norm_tf = tf
    avg_doc_length = sum(doc_length.values()) / doc_cnt

    b = 0.75
    k1 = 1.2

    for doc_id, length in doc_length.items():
        normalizer = 1 - b + b * (length / avg_doc_length)
        for ngram, raw_tf in tf[doc_id].items():
            norm_tf[doc_id][ngram] = ((k1 + 1) * raw_tf) / (k1 * normalizer + raw_tf)
    
    return norm_tf

def score_calculating(query, inv_file, idf, tf):
    k3 = 500
    score = dict()
    for term, qtf in query.items():
        if term in inv_file.keys():
            for doc_id in inv_file[term]:
                if doc_id not in score.keys():
                    score[doc_id] = 0
                assert(doc_id in tf)
                score[doc_id] += idf[term] * tf[doc_id][term] * (((k3 + 1) * qtf) / (k3 + qtf))

    return score

def rocchio(query, doc_id, doc):
    a = 0.6
    b = 0.3
    c = 0.1

    new_query = query
    rel_size = 20
    irrel_size = 20

    if len(doc_id) < rel_size: return query
    rel_id = [doc_id[i][0] for i in range(rel_size)]
    #irrel_id = [ doc_id[300+i][0] for i in range(irrel_size)]

    # Query expansion for relevant documents
    for idx in rel_id: 
        for term in doc[idx]:
            if term not in new_query:
                new_query[term] = 0
    
    # Query expansion for irrelevant documents
    #for idx in irrel_id:
    #    for term in doc[idx]:
    #        if term not in new_query:
    #            new_query[term] = 0

    # Calculate the tf of new query
    for term, qtf in new_query.items():
        rel_tf = 0
        irrel_tf = 0
        
        for idx in rel_id:
            if term in doc[idx]:
                rel_tf += doc[idx][term]
    #    for idx in irrel_id:
    #        if term in doc[idx]:
    #            irrel_tf += doc[idx][term]
        
        new_query[term] = a * qtf + b * (rel_tf / rel_size) - c * (irrel_tf / irrel_size)

    return new_query

def init():
    # Load the neccessary files preprocesses before
    with open("data/TF.json", "r", encoding="utf-8") as f:
        TF = json.load(f)
    with open("data/INV_FILE.json", "r", encoding="utf-8") as f:
        INV_FILE = json.load(f)
    with open("data/DOC_LENGTH.json", "r", encoding="utf-8") as f:
        DOC_LENGTH = json.load(f)
    with open("data/IDF.json", "r", encoding="utf-8") as f:
        IDF = json.load(f)
    with open("data/data.json", "r", encoding="utf-8") as f:
        corpus = json.load(f)
        corpus = corpus['articles']
    
    doc_count = len(corpus)

    NORM_TF = okapi_normalization(TF, DOC_LENGTH, doc_count)
    return INV_FILE, IDF, corpus, NORM_TF, TF

INV_FILE, IDF, corpus, NORM_TF, TF = init()

def search_docs(queries, feedback):
    qterm_count = Counter()
    qterm_count.update([queries])
    # Calculate the score of each document
    doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)
        
    # Sort the document score pair by the score
    sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
    
    if feedback:
        qterm_count = rocchio(qterm_count, sorted_doc_scores, TF)
        # Calculate the scores and Sort them
        doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)
        sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_doc_scores

def personal_score(query):      
    sorted_doc_scores = search_docs(query, False)
    if len(sorted_doc_scores) == 0:
        return 0
    sorted_doc_scores = sorted_doc_scores[:min(len(sorted_doc_scores), 5)]
    
    pscore = 0
    
    for i in range(len(sorted_doc_scores)):
        doc_id = int(sorted_doc_scores[i][0])
        
        x = []
        
        boo, push = corpus[doc_id]['message_count']['boo'], corpus[doc_id]['message_count']['push']
        if (boo > 200):
            boo = 200
        if (push> 200):
            push = 200
        x.append( [boo, push] )
        
        x = np.array(x)
        dscore = model.predict(x)[0][0]

        pscore += int(dscore*100) #corpus[doc_id][name]
    pscore /= len(sorted_doc_scores)
    print (pscore)
    return pscore

if __name__ == "__main__":

    people = ['馬英九', '韓國瑜']
    pscore = {}
    for name in people:
        pscore[name] = personal_score(name)







