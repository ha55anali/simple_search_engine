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

import shutil
sys.setrecursionlimit(1500)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--corpus_path')
parser.add_argument('--n_files', type=int,
     help='process first n documents in corpus',
     default=-1)
parser.add_argument('--results_path' ,default='results')
parser.add_argument('--stop_words_path' ,default='stoplist.txt')

def flatten(t):
    return [item for sublist in t for item in sublist]

# returns the string content of a soup file
def recTokenize(soup) -> str:

    if type(soup) != bs4.element.Tag and type(soup) != bs4.BeautifulSoup:
        if soup and soup.string != "\n" and type(soup) != bs4.Comment: ##and type(soup) != bs4.Script:
            return soup.extract()
        return
    children=list(soup.children)

    return_str=""
    for c in children:
        ret=recTokenize(c)
        if ret:
            return_str+=" "+ ret

    return return_str

def get_stop_words(path="/content/gdrive/My Drive/stoplist.txt"):
    file=open(path, 'r')
    return set(file.read().split('\n'))

#regex match

#tokenizes(stopwords and lower case) a corpus(list of documents)
def preprocess(data, stop_words):
    ret=[]
    
    for doc in tqdm.tqdm(data):
        if not doc:
            continue
        d=doc.split()
        d=[str.lower(x) for x in d]

        d= [re.findall("[a-zA-Z0-9_]+", x) for x in d]
        d=flatten(d)

        
        for w in d:
            if w in stop_words: #or w in set([',','-','--']):
                d.remove(w)
        ret.append(d)
                
    return ret if ret else None

# generates and writes docids
def file_tokenizer(filelist, path):
  a_set = set() #stores unqiue ids already assigned
  while True:
      a_set.add(randint(0, 4000))
      if len(a_set)==3465:
          break

  lst = sorted(list(a_set))
  
  with open(path, 'w') as writefile:
    for i, j in zip(lst, filelist):
        writefile.write(str(i) + "\t" + j + "\n")

  ret= zip(lst, filelist) 
  ret=sorted([(b,a) for a,b in ret])
  return dict(ret)

# generates ids for each term 
def term_tokenizer(termlist, path):
  a_set = set()
  term_list = set()

  for i in termlist:
    term_list.add(i)
  while True:
      a_set.add(randint(0, 1000000))
      if len(a_set)==len(term_list):
          break
  lst = sorted(list(a_set))
  
  with open(path, 'w') as writefile:
    for i, j in zip(lst, term_list):
        writefile.write(str(i) + "\t" + j + "\n") 

  ret= list(zip(lst, term_list))
  ret=sorted([(b,a) for a,b in ret])
  return dict(ret)

def get_inmem_forwardindex(FILES_PATH, n_files=-1):
    files=os.listdir(FILES_PATH)
    if n_files != -1:
        files=files[:n_files]
    
    files=[os.path.join(FILES_PATH, f) for f in files]

    non_null_files = []

    data=[]
    count = 1
    for f in tqdm.tqdm(files):
        if 'stoplist' not in f:
            try:
                file=open(f,'r')
                soup = bs4.BeautifulSoup(file, 'html.parser')
            except(UnicodeDecodeError):
                continue
        #soup
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.decompose()    # rip it out

        temp=recTokenize(soup.body)
        if temp is not None:
            data.append(temp)
            non_null_files.append(f)
        file.close()

    return data, non_null_files

def get_term_list(data):
    term_list=[]
    for i in data:
        term_list.append(i)
    return term_list

def write_findex(path, findex, terms, files, non_null_files):
    # terms=sorted([(b,a) for a,b in terms])
    # terms=dict(terms)
    # files=sorted([(b,a) for a,b in files])
    # files=dict(files)
    data=findex

    forward_index = open(path, 'w')
    term_postings = []

    for i,_ in enumerate(data):
        counter=dict(Counter(data[i]))
        counter=counter.items()

        write_forward=sorted([(terms[x[0]], x[1]) for x in counter])
        for w in write_forward:
            term_postings.append(w)
            forward_index.write(str(files[non_null_files[i]]) + "\t" + f"{w[0]}" + "\t" + f"{w[1]}" + "\n")
        forward_index.write('\n')

    forward_index.close() 

if __name__=='__main__':
    args = parser.parse_args()
    corpus_path=args.corpus_path
    results_path=args.results_path
    os.makedirs(results_path, exist_ok=True)

    files=os.listdir(corpus_path)
    files=[os.path.join(corpus_path, f) for f in files]

    file_list = file_tokenizer(files, os.path.join(results_path , "docids.txt"))

    findex, non_null_files=get_inmem_forwardindex(corpus_path , args.n_files)
    findex=preprocess(
        findex,
        get_stop_words(args.stop_words_path)
    )

    term_list=get_term_list(findex)

    termlist = flatten(term_list)
    terms = term_tokenizer(termlist, os.path.join(results_path , "termids.txt"))

    write_findex(
        os.path.join(results_path, "forwardindex.txt"),
        findex,
        terms,
        file_list,
        non_null_files
    )

