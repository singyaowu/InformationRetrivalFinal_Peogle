import json
import math
from argparse import ArgumentParser
import pandas as pd

"""

Calculate the tf, idf, inverted file and document length from the inverted_file.json given by TAs

"""

parser = ArgumentParser()
parser.add_argument("-i", "--inverted_file", default="inverted_file.json", dest="inverted_file", help="Pass in a .json file.")
parser.add_argument("-c", "--corpus_file", default="NC_1.csv", dest="corpus_file", help="Pass in a .csv file.")
args = parser.parse_args()

with open(args.inverted_file) as f:
    inv_file = json.load(f)

corpus = pd.read_csv(args.corpus_file).values
N = corpus.shape[0]


# TF[i] : Contain the TF of all unigrams & bigrams in doc i
TF = {}
# INV_FILE[i] : Contain the document list that has term i
INV_FILE = {}
# DOC_LENGTH[i] : The length of doc i
DOC_LENGTH = {}
# IDF[i] : Contain the IDF of term i
IDF = {}

punctuation = [
    "，", "、", "　", "《", "〈", "＜", "<", ",", "。", "・", "·", "》", "〉", "＞", ">", ".",
    "？", "/", "／", "÷", "?", "：", "；", ":", ";", "“", "”", "\"", "〃", "'",
    "『", "「", "【", "〔", "［", "{", "[", "』", "」", "】", "〕", "］", "}", "]", "｜", "|", "\\",
    "~", "!", "@", "#", "$#", "%", "^", "&", "*", "(", ")", "_", "__", "+", "="
]

for word in inv_file:
    if word in punctuation:
        continue

    INV_FILE[word] = []

    k = 0
    for doc_count in inv_file[word]["docs"]:
        for doc, count in doc_count.items():
            INV_FILE[word].append(doc)
            if doc not in TF.keys():
                TF[doc] = {}
            TF[doc][word] = count
            if doc not in DOC_LENGTH.keys():
                DOC_LENGTH[doc] = 0
            DOC_LENGTH[doc] += count
            k += 1

    IDF[word] = math.log((N - k + 0.5) / (k + 0.5))


with open("TF.json", "w") as f:
    json.dump(TF, f, ensure_ascii=False)
with open("INV_FILE.json", "w") as f:
    json.dump(INV_FILE, f, ensure_ascii=False)
with open("DOC_LENGTH.json", "w") as f:
    json.dump(DOC_LENGTH, f, ensure_ascii=False)
with open("IDF.json", "w") as f:
    json.dump(IDF, f, ensure_ascii=False)
