import pandas as pd
import numpy as np

import xml.etree.ElementTree as ET
from nltk.stem import PorterStemmer
import re

import logging
### public
def get_grades(path):    
    '''
        returns dict in the following format
        topic number:
            (docname: str,
            grade: str) (tuple)
    '''
    # returns grades from path
    return parse_grades(read_qrel(path))

def parse_topics(path):
    '''
    returns dict in the following structure
        number: 
            type: str
            query: str
            desc: str
    '''
    
    ret_dict=dict()
    
    tree = ET.parse(path)
    root = tree.getroot()

    for topic in root:
        topic_num=topic.attrib['number']
        topic_dict=dict()
        logging.debug(topic.tag, topic.attrib)
        
        logging.debug(topic[0].tag, ":",topic[0].text)
        topic_dict['type']=topic[0].text
        
        logging.debug(topic[1].tag, ":",topic[1].text)
        topic_dict['desc']=topic[1].text.strip()
        
        ret_dict[topic_num]=topic_dict
        
    return ret_dict

### private

def read_qrel(path):
    rel_query = []
    with open(path, 'r') as fp:
        Lines = fp.readlines()
        for line in Lines:
          # The line below may need to be changed based on the type of data in the qrel file
          rel_query.append(line.split())
    qrel_df = pd.DataFrame(rel_query)
    
    return qrel_df

def parse_grades(frame):
    '''
        returns dict in the following format
        topic number:
            (docname: str,
            grade: str) (tuple)
    '''
    grades=dict()
    topics=np.unique(frame[0])
    
    for topic in topics:
        
        topic_dict=dict()
        topic_output=frame.where(frame[0] == topic).dropna()
        
        for index, row in topic_output.iterrows():
            topic_dict[row[2]]= row[3]
        
        grades[topic]=topic_dict    
        
    return grades


### file reading

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

def read_terminfo(path):
    term_info_dict=dict()
    
    file = open(path, 'r')
    Lines = file.readlines()

    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        term_id, offset, o_count, d_count = line.strip().split('\t')
        term_info_dict[term_id] = {'offset': offset, 'o_count': o_count, 'd_count': d_count}
    file.close()
    
    return term_info_dict

def seek_inv_index(offset, doc_id, path, return_index=False):
    doc_id=str(doc_id)
    found=False
    with open(path, 'r') as f:
        f.seek(int(offset))
        line = f.readline().strip().split('\t')
        line = [x for x in line[1:] if x != '']

        logging.debug(f'inv index {line}')
        if return_index:
            return line
        for l in line:
            if l.split(':')[0] == doc_id:
                found=True
                return int(l.split(':')[1])
        if not found:
            logging.debug('docid not found')
            return 0
    f.close()

def flatten(t):
    return [item for sublist in t for item in sublist]

def get_stop_words(path="/content/gdrive/My Drive/stoplist.txt"):
    file=open(path, 'r')
    return set(file.read().split('\n'))

def process_word(word_list, stop_words):
    #returns processed query
    ps=PorterStemmer()
    
    d=word_list.split()
    d=[str.lower(x) for x in d]
    
    d=[re.findall("[a-zA-Z0-9_]+", x) for x in d]
    d=flatten(d)
    d=[ps.stem(x) for x in d]


    for w in d:
        if w in stop_words: #or w in set([',','-','--']):
            d.remove(w)
    return d

def run_query(query, score_function):
    query=process_word(query)
    
    return score_function(query)

def score(topics):
    '''
    return dict
        topic id:
            docname:
                rank
                score:
    '''
    
def get_tf(word, doc_id, seek_inv_index , termids, term_info):
    '''
        word: word to be searched in str form
        doc_id: int
        seek_inv_index: function(offset)
        termids: mapping of word to ids
        terminfo: gives offset of word
    '''
    
    tid=termids[word]
    return seek_inv_index(term_info[tid]['offset'], doc_id)

def get_total_documents(f_index_path):
    return sum(1 for line in open(f_index_path))

def get_dfi(word , termids, term_info):
    tid=termids[word]
    return int(term_info[tid]['d_count'])