import csv
import json
import random
import operator
from argparse import ArgumentParser
from collections import Counter
import numpy as np
import pandas as pd
import jieba
from helper import *

def okapi_normalization(tf, doc_length, doc_cnt):
    norm_tf = tf
    avg_doc_length = sum(doc_length.values()) / doc_cnt

    b = 0.75
    k1 = 1.2

    for doc, length in doc_length.items():
        normalizer = 1 - b + b * (length / avg_doc_length)
        for ngram, raw_tf in tf[doc].items():
            norm_tf[doc][ngram] = ((k1 + 1) * raw_tf) / (k1 * normalizer + raw_tf)
    
    return norm_tf

def score_calculating(query, inv_file, idf, tf):
    k3 = 500
    score = dict()
    for term, qtf in query.items():
        if term in inv_file.keys():
            for doc in inv_file[term]:
                if doc not in score.keys():
                    score[doc] = 0
                score[doc] += idf[term] * tf[doc][term] * (((k3 + 1) * qtf) / (k3 + qtf))

    return score

def rocchio(query, doc_id, doc):
    new_query = query
    rel_size = 30
    irrel_size = 30

    rel_id = []
    for i in range(rel_size):
        rel_id.append(doc_id[i][0])
    irrel_id = []
    for i in range(irrel_size):
        irrel_id.append(doc_id[300+i][0])
    
    a = 0.6
    b = 0.3
    c = 0.1

    # Query expansion for relevant documents
    for id in rel_id:
        terms = doc[id].keys()
        for term in terms:
            if term not in new_query.keys():
                new_query[term] = 0
    
    # Query expansion for irrelevant documents
    for id in irrel_id:
        terms = doc[id].keys()
        for term in terms:
            if term not in new_query.keys():
                new_query[term] = 0

    # Calculate the tf of new query
    for term, qtf in new_query.items():
        rel_tf = 0
        irrel_tf = 0
        
        for id in rel_id:
            if term in doc[id]:
                rel_tf += doc[id][term]
        for id in irrel_id:
            if term in doc[id]:
                irrel_tf += doc[id][term]
        
        new_query[term] = a * qtf + b * (rel_tf / rel_size) - c * (irrel_tf / irrel_size)

    return new_query

def main(args):
    # Load the neccessary files preprocesses before
    with open("TF.json", "r") as f:
        TF = json.load(f)
    with open("INV_FILE.json", "r") as f:
        INV_FILE = json.load(f)
    with open("DOC_LENGTH.json", "r") as f:
        DOC_LENGTH = json.load(f)
    with open("IDF.json", "r") as f:
        IDF = json.load(f)

    querys = pd.read_csv(args.query_file).values
    corpus = pd.read_csv(args.corpus_file).values
    doc_count = corpus.shape[0]

    # Normalize tf by using okapi normalization
    NORM_TF = okapi_normalization(TF, DOC_LENGTH, doc_count)

    # Process each query
    final_ans = []
    for qid, query in querys:
        print("query id: {}".format(qid))

        # Calculte tf of the query
        qterm_count = Counter()
        query_terms = jieba.lcut(query)
        qterm_count.update(query_terms)

        # Calculate the score of each document
        doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)
            
        # Sort the document score pair by the score
        sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
        
        # Use Pseudo Rocchio Feedback to update the query
        qterm_count = rocchio(qterm_count, sorted_doc_scores, TF)

        # Calculate the scores and Sort them
        doc_scores = score_calculating(qterm_count, INV_FILE, IDF, NORM_TF)
        sorted_doc_scores = sorted(doc_scores.items(), key=operator.itemgetter(1), reverse=True)
        

        # Record the answer of this query to final_ans
        if len(sorted_doc_scores) >= 300:
            final_ans.append([doc_score_tuple[0] for doc_score_tuple in sorted_doc_scores[:300]])
        else: # if candidate documents less than 300, random sample some documents that are not in candidate list
            documents_set  = set([doc_score_tuple[0] for doc_score_tuple in sorted_doc_scores])
            sample_pool = ["news_%06d"%news_id for news_id in range(1, doc_count+1) if "news_%06d"%news_id not in documents_set]
            sample_ans = random.sample(sample_pool, 300-len(sorted_doc_scores))
            sorted_doc_scores.extend(sample_ans)
            final_ans.append([doc_score_tuple[0] for doc_score_tuple in sorted_doc_scores])

    # Write answer to csv file
    with open(args.output_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        head = ["Query_Index"] + ["Rank_%03d"%i for i in range(1,301)]
        writer.writerow(head)
        for query_id, ans in enumerate(final_ans, 1):
            writer.writerow(["q_%02d"%query_id]+ans)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-q", "--query_file", default="QS_1.csv", dest="query_file", help="Pass in a .csv file.")
    parser.add_argument("-c", "--corpus_file", default="NC_1.csv", dest="corpus_file", help="Pass in a .csv file.")
    parser.add_argument("-o", "--output_file", default="output.csv", dest="output_file", help="Pass in a .csv file.")
    
    args = parser.parse_args()
    
    main(args)