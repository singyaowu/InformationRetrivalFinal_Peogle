import csv
import json
import random
import operator
from argparse import ArgumentParser
from collections import Counter
import numpy as np
import pandas as pd
#import jieba

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
    rel_size = 100
    irrel_size = 100

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
    with open("../TF.json", "r", encoding="utf-8") as f:
        TF = json.load(f)
    with open("../INV_FILE.json", "r", encoding="utf-8") as f:
        INV_FILE = json.load(f)
    with open("../DOC_LENGTH.json", "r", encoding="utf-8") as f:
        DOC_LENGTH = json.load(f)
    with open("../IDF.json", "r", encoding="utf-8") as f:
        IDF = json.load(f)
    with open("../data.json", "r", encoding="utf-8") as f:
        corpus = json.load(f)
        corpus = corpus['articles']
    
    doc_count = len(corpus)

    NORM_TF = okapi_normalization(TF, DOC_LENGTH, doc_count)
    return INV_FILE, IDF, corpus, NORM_TF, TF

INV_FILE, IDF, corpus, NORM_TF, TF = init()

def search_docs(queries):
    qterm_count = Counter()
    qterm_count.update(queries + [queries[1]])
    # Calculate the score of each document
    doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)
        
    # Sort the document score pair by the score
    sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
    #qterm_count = rocchio(qterm_count, sorted_doc_scores, TF)
    # Calculate the scores and Sort them
    #doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)
    #sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_doc_scores

def find_relations(query):
    if query in set(['石上',"石上 優", "優"]):
        return [{"name":"伊井野 ミコ", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"子安 つばめ", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"小野寺 麗", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"白銀 御行", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"四宮 かぐや", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]}

        ]
    elif query in set(["伊井野", "伊井野ミコ", "ミコ", "伊井野彌子", "伊井野御子", "彌子", "御子"]):
        return [{"name":"石上 優", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"大仏 こばち", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"藤原 千花", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"白銀 御行", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]},
        {"name":"小野寺 麗", 
        "related_docs":[{"article_title":"ラブラブバカップル()な石ミコ漫画です", "url":"https://twitter.com/RGB_0127/status/1142788107713957889"}]}
        ]
    
    qterm_count = Counter()
    qterm_count.update([query])
    # Calculate the score of each document
    print(qterm_count)
    doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)        
    sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
    
    qterm_count = rocchio(qterm_count, sorted_doc_scores, TF)
    sorted_qterm_count = sorted(qterm_count.items(), key=operator.itemgetter(1), reverse=True)
    print(sorted_qterm_count)
    answers = []
    
    prev_names = []
    for name, _ in sorted_qterm_count:
        if name in query: continue
        if query in name: continue
        invalid_name = False
        for prev_name in prev_names:
            if name in prev_name: invalid_name = True
        if invalid_name: continue
        prev_names.append(name)
        if len(prev_names) > 6: break
        print(name)
        
        edge = {}
        rel_query = [query, name]
        doc_ids = search_docs(rel_query)
        if len(doc_ids) > 3: doc_ids = doc_ids[:3]
        doc_ids = [ int(doc[0]) for doc in doc_ids ]
        rel_docs = []
        for doc_id in doc_ids:
            doc = {}
            doc["article_title"] = corpus[doc_id]["article_title"]
            doc["url"] = corpus[doc_id]["url"]
            rel_docs.append(doc)

        edge['name'] = name
        edge['related_docs'] = rel_docs
        
        answers.append(edge)
    return answers

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--corpus_file", default="../data.json", dest="corpus_file", help="Pass in a .json file.")
    
    args = parser.parse_args()
    while True:
        query = input("type a person you want to search:")
        print(find_relations(query))