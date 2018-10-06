# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 03:29:33 2018

@author: Lenovo
"""
import speech_recognition as sr
import pydub
import nltk
from nltk import word_tokenize
import datetime
import re

### Extract .wav file from uploaded .mp3 file

sound = pydub.AudioSegment.from_mp3("audio1.mp3")
start_time=13*1000
sound= sound[start_time:]
sound.export("audioo2.wav", format= "wav")

### Speech to text conversion using python library

r = sr.Recognizer()

with sr.AudioFile('audioo2.wav') as source:
    audio= r.record(source)
    
print(type(audio))
data= r.recognize_ibm(audio,username="dc1fd34c-22c4-4b33-8400-2ef7192854e8", password="1rrHBmgDfUJJ")

print(data)
### data is the text file of the uploaded recoding
### Further: Information Extraction
'''
Steps of Information Extraction:
    1. Tokenization
    2. POS Tagging
    3. Clunching
    4. Name Entity Recognition
    5. Entitiy relation extraction
'''
import spacy, pprint
import pydub
from spacy import displacy
from collections import Counter
import en_core_web_sm

#print(name_entity);

print("DATE: ", datetime.date.today())
print("TIME: ", datetime.datetime.now().time())

nlp= en_core_web_sm.load()
doc= nlp(data)
name_entity={}

for token in doc:
    name_entity[token.text]= token.pos_
    
print(name_entity)

### returns a dictionary with tokenised word of the text and its entity type

names=set()
for token in doc:
    if(token.pos_ == "PROPN"):
        names.add(token.text)
        
print("ATTENDEES")
for name in names:

    print(name)
    
### Tag the people who attended the meeting
    

from gensim.summarization.summarizer import summarize
print(summarize(data, ratio=0.1))