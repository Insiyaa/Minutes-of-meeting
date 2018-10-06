# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 19:03:33 2018

@author: Lenovo
"""

from nltk.corpus import brown
 
data = []
for fileid in brown.fileids():
    document = ' '.join(brown.words(fileid))
    data.append(document)
 
NO_DOCUMENTS = len(data)

from nltk.corpus import brown, stopwords
import re
from nltk import word_tokenize
from gensim import models, corpora

NUM_TOPICS=10
STOPWORDS= stopwords.words('english')

def clean_text(text):
    tokenized_text= word_tokenize(text.lower())
    cleaned_text = [t for t in tokenized_text if t not in STOPWORDS and re.match('[a-zA-Z\-][a-zA-Z\-]{2,}', t)]
    return cleaned_text

tokenized_data=[]

for text in data:
    tokenized_data.append(clean_text(text))

dictionary = corpora.Dictionary(tokenized_data)
corpus = [dictionary.doc2bow(text) for text in tokenized_data]

print(corpus[20])

lda_model = models.LdaModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)

for idx in range(NUM_TOPICS):
    


    
