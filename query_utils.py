import pandas as pd
import numpy as np

import xml.etree.ElementTree as ET

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
