import json
import math
from argparse import ArgumentParser
import pandas as pd
from helper import *

parser = ArgumentParser()
parser.add_argument("-c", "--corpus_file", default="../data.json", dest="corpus_file", help="Pass in a .csv file.")
args = parser.parse_args()

# TF[i] : Contain the TF of all unigrams & bigrams in doc i
TF = {}
name_TF = {}
# INV_FILE[i] : Contain the document list that has term i
INV_FILE = {}
name_INV_FILE = {}
# DOC_LENGTH[i] : The length of doc i
DOC_LENGTH = {}
# IDF[i] : Contain the IDF of term i
IDF = {}

with open(args.corpus_file, encoding="utf-8") as f:
    corpus = json.load(f)

punctuation = set([
    "，", "、", "　", "《", "〈", "＜", "<", ",", "。", "・", "·", "》", "〉", "＞", ">", ".",
    "？", "/", "／", "÷", "?", "：", "；", ":", ";", "“", "”", "\"", "〃", "'",
    "『", "「", "【", "〔", "［", "{", "[", "』", "」", "】", "〕", "］", "}", "]", "｜", "|", "\\",
    "~", "!", "@", "#", "$#", "%", "^", "&", "*", "(", ")", "_", "__", "+", "="
])

for doc_idx, doc in enumerate(corpus['articles']):
    doc_id = str(doc_idx)
    if doc_idx % 1000 == 0:
        print("doc_id", doc_id)
    try:
        for term in doc['article_tf']:
            count = doc['article_tf'][term]
            if term in punctuation: continue
            if not isName(term): continue
            
            if term not in INV_FILE.keys():
                INV_FILE[term] = []
            INV_FILE[term].append(doc_id)

            if doc_id not in TF.keys():
                TF[doc_id] = {}
            TF[doc_id][term] = count
            if doc_id not in DOC_LENGTH.keys():
                DOC_LENGTH[doc_id] = 0
            DOC_LENGTH[doc_id] += count

            if term not in IDF.keys():
                IDF[term] = 0
            IDF[term] += 1
    except: 
        print(doc_idx, doc)
        #exit(1)
        #print(term)

N = len(corpus['articles'])
for term in IDF.keys():
    k = IDF[term]
    IDF[term] = math.log( (N - k + 0.5)/(k + 0.5) ) 

with open("../TF.json", "w", encoding="utf-8") as f:
    json.dump(TF, f, ensure_ascii=False)
with open("../INV_FILE.json", "w", encoding="utf-8") as f:
    json.dump(INV_FILE, f, ensure_ascii=False)
with open("../DOC_LENGTH.json", "w", encoding="utf-8") as f:
    json.dump(DOC_LENGTH, f, ensure_ascii=False)
with open("../IDF.json", "w", encoding="utf-8") as f:
    json.dump(IDF, f, ensure_ascii=False)

