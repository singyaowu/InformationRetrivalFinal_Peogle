import os
import re
import argparse
import math
import csv
import numpy as np
import xml.etree.ElementTree as ET
import time

def okapi_normalization(tf, doc_length, doc_cnt):
    norm_tf = tf
    avg_doc_length = sum(doc_length) / doc_cnt

    b = 0.75
    k1 = 1.2

    for i in range(doc_cnt):
        normalizer = 1 - b + b * (doc_length[i] / avg_doc_length)
        for ngram, raw_tf in tf[i].items():
            norm_tf[i][ngram] = ((k1 + 1) * raw_tf) / (k1 * normalizer + raw_tf)
    
    return norm_tf

def query_parsing(file_path):
    tree = ET.ElementTree(file=file_path)

    id, concepts = [], []

    for number in tree.iter(tag="number"):
        id.append(number.text[-3:])
    
    for concept in tree.iter(tag="concepts"):
        concepts.append(concept.text.strip())

    return id, concepts

def concepts_splitting(concepts):
    concepts_list = concepts.split("、")
    concepts_list[-1] = concepts_list[-1].strip("。")

    FULLWIDTH_TO_HALFWIDTH = str.maketrans(
                                            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
                                            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                                        )
    
    # Split concepts into ngram
    ngram_concepts = []
    for i in range(len(concepts_list)):
        ngram_concepts.append(concepts_list[i].translate(FULLWIDTH_TO_HALFWIDTH))
        
        if bool(re.match(r'[\u4e00-\u9fff]+', concepts_list[i])):
            for j in range(len(concepts_list[i])-1):
                ngram_concepts.append(concepts_list[i][j:j+2])

    return ngram_concepts

def score_calculating(doc_cnt, query, inv_file, idf, tf):
    k3 = 500
    score = np.zeros((doc_cnt,))
    for term, qtf in query.items():
        for id in inv_file[term]:
            score[id] += idf[term] * tf[id][term] * (((k3 + 1) * qtf) / (k3 + qtf))

    return score

def get_rank(score):
    # Get the true/false value for each index 
    mask = score > 0.0
    # Sorted in descending order and get the index
    sorted_index = np.argsort(-score)
    # Get the masked index
    index = sorted_index[mask[sorted_index]]

    return index

def rocchio(query, doc_id, doc):
    new_query = query
    rel_size = 10
    irrel_size = 10
    rel_id = doc_id[:rel_size]
    irrel_id = doc_id[100:100+irrel_size]

    a = 0.5
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", help="Rocchio feedback", dest="rfb", default=False, action="store_true")
    parser.add_argument("-b", help='Best version', dest="best", default=False, action="store_true") 
    parser.add_argument("-i", help="query-file", dest="query_file", default="./queries/query-test.xml")
    parser.add_argument("-o", help="ranked-list", dest="ranked_list", default="./output.csv")
    parser.add_argument("-m", help="model-dir", dest="model_dir", default="./model")
    parser.add_argument("-d", help="NTCIR-dir", dest="NTCIR_dir", default="./CIRB010")
    args = parser.parse_args()
    
    print(args.rfb, args.best, args.query_file, args.ranked_list, args.model_dir, args.NTCIR_dir)

    START = time.time()

    ### All the vocabs in vocab.all
    # e.g.
    # VOCAB[vocab_id_1] = "Copper"
    ###
    print("\nStart accessing vocab.all.")
    start = time.time()
    
    with open(os.path.join(args.model_dir, "vocab.all"), "r") as f:
        VOCAB = [line.strip() for line in f]
    
    print("Finish accessing vocab.all, and it takes {} seconds.".format(time.time() - start))

    ### All the paths in file-list
    # e.g.
    # FILE_LIST[file_id0] = "CDN_LOC_0001457"
    ###
    print("\nStart accessing file-list.")
    start = time.time()

    with open(os.path.join(args.model_dir, "file-list"), "r") as f:
        FILE_LIST = np.array([line.strip().split("/")[-1].lower() for line in f])
    doc_count= len(FILE_LIST)
    
    print("Finish accessing file-list, and it takes {} seconds.".format(time.time() - start))
    

    # TF[i] : Contain the TF of all unigrams & bigrams in doc i
    TF = {i: {} for i in range(doc_count)}
    # INV_FILE[i] : Contain the document list that has term i
    INV_FILE = {}
    # DOC_LENGTH[i] : The length of doc i
    DOC_LENGTH = [0 for _ in range(doc_count)]
    # All unigrams & bigrams
    LEXICON = []
    # IDF[i] : Contain the IDF of term i
    IDF = {}

    print("\nStart accessing inverted-file.")
    start = time.time()
    
    with open(os.path.join(args.model_dir, "inverted-file"), "r") as f:
        for line in f:
            line = line.strip().split()
            vocab_id1, vocab_id2, N = [int(num) for num in line]
            
            if vocab_id2 != -1:
                LEXICON.append(VOCAB[vocab_id1]+VOCAB[vocab_id2])
            else:
                LEXICON.append(VOCAB[vocab_id1])
            
            INV_FILE[LEXICON[-1]] = []
            #IDF[LEXICON[-1]] = math.log((doc_count - N + 0.5) / (N + 0.5))
            IDF[LEXICON[-1]] = math.log((doc_count + 1) / N)

            for _ in range(N):
                line = f.readline().strip().split()
                file_id, count = [int(num) for num in line]
                
                TF[file_id][LEXICON[-1]] = count
                INV_FILE[LEXICON[-1]].append(file_id)
                DOC_LENGTH[file_id] += count
    
    print("Finish accessing inverted-file, and it takes {} seconds.\n".format(time.time() - start))
    

    # Normalize the term frequency
    NORM_TF = okapi_normalization(TF, DOC_LENGTH, doc_count)

    # Parse the query to retrieve id & concepts
    query_id, query_concepts = query_parsing(args.query_file)    
    query_count = len(query_id)

    with open(args.ranked_list, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["query_id", "retrieved_docs"])

        for i in range(query_count):
            start = time.time()
            print("Processing query {}.".format(query_id[i]))
            # query i
            concepts = concepts_splitting(query_concepts[i])
            query = {}

            for concept in concepts:
                if concept in LEXICON:
                    if concept not in query.keys():
                        query[concept] = 1
                    else:
                        query[concept] += 1
            
            doc_score = score_calculating(doc_count, query, INV_FILE, IDF, NORM_TF)
            index = get_rank(doc_score)

            if args.rfb or args.best:
                query = rocchio(query, index, TF)
                doc_score = score_calculating(doc_count, query, INV_FILE, IDF, NORM_TF)
                index = get_rank(doc_score)

            rank = FILE_LIST[index][:100]

            writer.writerow([query_id[i], " ".join(rank)])

            print("Processing query {} take {} seconds.".format(query_id[i], time.time()-start))
    
    print("\nTotal execution time : {} seconds.".format(time.time()-START))