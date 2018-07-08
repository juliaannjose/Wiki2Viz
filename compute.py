# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import re
import os
import argparse
import numpy as np
import io

T = []
f = codecs.open('results/preprocessed_titles.txt', encoding='utf-8')
for line in f:
    T.append(line)        

T = map(lambda s: s.strip(), T)     #removing '\n' char from list elements


#computing average of vectors of titles using word vectors from fasttext
nmax = 500000
vectors = []
word2id = {}
words = []
with io.open('data/wiki.multi.fr.vec', 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
    next(f)
    for i, line in enumerate(f):
        word, vect = line.rstrip().split(' ', 1)
        vect = np.fromstring(vect, sep=' ')
        assert word not in word2id, 'word found twice'
        vectors.append(vect)
        words.append(word)
        word2id[word] = len(word2id)
        if len(word2id) == nmax:
            break
X = []
X_title = []
for titles in T:
    TITLE = titles
    titles = titles.replace('(','')              #remove "()","-",":" and convert to lowercase
    titles= titles.replace(')','')
    titles= titles.replace('-',' ')
    titles= titles.replace(':',' ')
    word_list = titles.strip().split(' ')
    avg_vect = 0
    flag = 0
    for w in word_list:
        for w1,v1 in zip(words,vectors):
            if w1 == w.lower(): 
                avg_vect = avg_vect + v1
                flag = 1
                break
    avg = avg_vect/len(word_list)          #avg for one article
    if flag!=0:             #if avg not computed for an article (i.e =0) then ignore article and title
        X.append(avg)
        X_title.append(TITLE)

print "writing to file..."

X_stack = np.vstack(X)               #vstack for output to file 
with open('results/fr_titles.vec','a') as f:
    for t1,x1 in zip(X_title,X_stack):
        f.write(t1.encode("utf-8"))
        f.write('~')
        for x in x1:
            f.write('%s' %x)
            f.write(' ')
        f.write('\n')
