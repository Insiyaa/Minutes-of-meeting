# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 17:05:42 2018

@author: Lenovo
"""

import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
sentence = "Mark and John are working at Google."

sentence= nltk.ne_chunk(pos_tag(word_tokenize(sentence)))

import spacy, pprint
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp= en_core_web_sm.load()
doc = nlp('European authorities fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices')
#print(doc.ents)
name_entity=[]
for token in doc:
    if(token.pos_ == "PROPN"):
        name_entity.append(token.text)
    
print(name_entity)