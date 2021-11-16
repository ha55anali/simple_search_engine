import os
import bs4
#from bs4 import BeautifulSoup
import random
import tqdm
#from nltk.stem import PorterStemmer
from random import randint
import sys
import re
from collections import Counter
import csv
import copy

import shutil
sys.setrecursionlimit(1500)
from collections import defaultdict

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--results_path', default='results')

def read_docids(path):
    f=open(path)
    text=f.read()
    f.close()

    docs=dict()

    # split on new line
    text=text.split('\n')

    for line in text:
        if line=='':
            continue

        arr=line.split('\t')
        id, name=arr

        docs[id]=name

    return docs

def read_termids(path):
    file = open(path, 'r')
    Lines = file.readlines()
    term_dict = {}
    term_info_dict = {}
    doc_dict = {}

    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        term_id, term = line.strip().split('\t')
        term_dict[term_id] = term
    file.close()

    return term_dict

def read_forwardindex(path):
    doc_index_dict = defaultdict(list)
    file = open(path, 'r')
    Lines = file.readlines()

    count = 0
    # Strips the newline character
    for line in Lines:
            content = line.strip().split('\t')
            if line.strip() != '':
                count += 1
                doc_id, term_id, term_count = content
                doc_index_dict[doc_id].append( (term_id,  term_count))
    file.close()

    return doc_index_dict

def write_invindex(path,findex, terms, files, non_null_files=None):
    # terms=sorted([(b,a) for a,b in terms])
    # terms=dict(terms)
    # files=sorted([(b,a) for a,b in files])
    # files=dict(files)
    data=findex
    term_info=dict([
               (t, {'offset':-1,'occu': 0, 'documents':0 })
               for t in terms
        ])

    term_index = open(path, 'w')
    offset=0
    for i in tqdm.tqdm(sorted(terms, key=lambda x: terms[x])):
        write_line=str(i)

        doc_counter=0
        occ_counter=0
        #print(len(data))
        for j in data:
            counter=Counter([x[0] for x in data[j]])

            if counter[i] > 0:
                #print('oeu')
                doc_counter+=1
                occ_counter+=counter[i]

                write_line+="\t" + str(j) + ":" + str(counter[i]) + "\t"

            #print(len(data))
        
        write_line+="\n"
        term_index.write(write_line)

        term_info[i]['offset']=offset
        term_info[i]['documents']=doc_counter
        term_info[i]['occu']=occ_counter

        offset+=len(write_line)
    term_index.close()
    return term_info

def write_terminfo(path, term_info):
    file=open(path, 'w')
    for t in term_info:
        file.write(f'{t}\t{term_info[t]["offset"]}\t{term_info[t]["occu"]}\t{term_info[t]["documents"]}\n')

    file.close()


def write_invindex_fast(path,findex, terms, files, non_null_files=None):
    # terms=sorted([(b,a) for a,b in terms])
    # terms=dict(terms)
    # files=sorted([(b,a) for a,b in files])
    # files=dict(files)
    data=findex
    term_info=dict([
               (t, {'offset':-1,'occu': 0, 'documents':0 })
               for t in terms
        ])

    term_index = open(path, 'w')
    offset=0

    inv_index=dict()

    for j in data:
        for word, freq in data[j]:
            if word in inv_index.keys():
                inv_index[word][j]= freq
            else:
                inv_index[word]={j:freq}


    for word in inv_index:
        occu=0
        writeline=word
        for doc in inv_index[word]:
            writeline+="\t"+str(doc)+":"+str(inv_index[word][doc])
            occu+=int(inv_index[word][doc])

        term_index.write(writeline)
        term_index.write("\n")

        term_info[word]['offset']=offset
        term_info[word]['documents']=len(inv_index[word])
        term_info[word]['occu']=occu

        offset+=len(writeline)

    
        #print(term_info[word])
        #print(inv_index[word])

    return term_info



    for i in tqdm.tqdm(sorted(terms, key=lambda x: terms[x])):
        write_line=str(i)

        doc_counter=0
        occ_counter=0
        #print(len(data))
        for j in data:
            counter=Counter([x[0] for x in data[j]])

            if counter[i] > 0:
                #print('oeu')
                doc_counter+=1
                occ_counter+=counter[i]

                write_line+="\t" + str(j) + ":" + str(counter[i]) + "\t"

            #print(len(data))
        
        write_line+="\n"
        term_index.write(write_line)

        term_info[i]['offset']=offset
        term_info[i]['documents']=doc_counter
        term_info[i]['occu']=occ_counter

        offset+=len(write_line)
    term_index.close()
    return term_info

if __name__=='__main__':
    args = parser.parse_args()
    results_path=args.results_path

    findex_path=os.path.join(results_path, 'forwardindex.txt')
    files_list_path=os.path.join(results_path, 'docids.txt')
    term_list_path=os.path.join(results_path, 'termids.txt')


    docs=read_docids(files_list_path)
    terms=read_termids(term_list_path)
    findex=read_forwardindex(findex_path)


    term_info=write_invindex_fast(
        os.path.join(results_path, "term_index.txt"),
        findex,
        terms,
        [docs[x] for x in docs]
    )

    
    write_terminfo(
        os.path.join(results_path, 'term_info.txt'),
        term_info
    )


