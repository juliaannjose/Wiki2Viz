# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import re
import os
import argparse
import time
import lda
import numpy as np
import io


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


tree = ET.parse('enwiki.xml')
root = tree.getroot()

articles_and_titles = []
titles = []
for i,page in enumerate(root.findall('{http://www.mediawiki.org/xml/export-0.10/}page')):
    for p in page:  
        if p.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
            article_title = p.text 
            if not article_title == None: 
                article_title = re.sub(r"\!|\"|\#|\$|\%|\&|\'|\(|\)|\*|\+|\,|\-|\/|\:|\;|\<|\=|\>|\?|\@|\[|\\|\]|\^|\_|\`|\{|\||\}|\~"," ",article_title)
                article_title = article_title.replace(u'\xa0', u' ')
                article_title = article_title.replace('Category',u'')
                article_title = article_title.replace('Wikipedia',u'')
                article_title = article_title.replace('{{',u'')
                article_title = article_title.replace('}}',u'')
                article_title = article_title.replace('File',u'')
                article_title = article_title.replace('Image',u'')
                article_title = article_title.replace('Infobox',u'')
                article_title = article_title.replace('Templates',u'')
                article_title = article_title.replace('infobox',u'')
                article_title = article_title.replace('templates',u'')
                article_title = article_title.replace('Template',u'')
                article_title = article_title.replace('template',u'')
        if p.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
            for x in p:
                if x.tag == "{http://www.mediawiki.org/xml/export-0.10/}text":                    
                    article_txt = x.text
                    if not article_txt == None:                                                
                        article_txt = article_txt[ : article_txt.find("==")]
                        article_txt = re.sub(r"{{.*}}","",article_txt)
                        article_txt = re.sub(r"\[\[File:.*\]\]","",article_txt)
                        article_txt = re.sub(r"\[\[Image:.*\]\]","",article_txt)
                        article_txt = re.sub(r"\n: \'\'.*","",article_txt)
                        article_txt = re.sub(r"\n!.*","",article_txt)
                        article_txt = re.sub(r"^:\'\'.*","",article_txt)
                        article_txt = re.sub(r"&nbsp","",article_txt)
                        article_txt = re.sub(r"http\S+","",article_txt)
                        article_txt = re.sub(r"\d+","",article_txt)   
                        article_txt = re.sub(r"\(.*\)","",article_txt)
                        article_txt = re.sub(r"Category:.*","",article_txt)
                        article_txt = re.sub(r"\| .*","",article_txt)
                        article_txt = re.sub(r"\n\|.*","",article_txt)
                        article_txt = re.sub(r"\n \|.*","",article_txt)
                        article_txt = re.sub(r".* \|\n","",article_txt)
                        article_txt = re.sub(r".*\|\n","",article_txt)
                        article_txt = re.sub(r"{{Infobox.*","",article_txt)
                        article_txt = re.sub(r"{{infobox.*","",article_txt)
                        article_txt = re.sub(r"{{taxobox.*","",article_txt)
                        article_txt = re.sub(r"{{Taxobox.*","",article_txt)
                        article_txt = re.sub(r"{{ Infobox.*","",article_txt)
                        article_txt = re.sub(r"{{ infobox.*","",article_txt)
                        article_txt = re.sub(r"{{ taxobox.*","",article_txt)
                        article_txt = re.sub(r"{{ Taxobox.*","",article_txt)
                        article_txt = re.sub(r"\* .*","",article_txt)
                        article_txt = re.sub(r"<.*>","",article_txt)
                        article_txt = re.sub(r"\n","",article_txt)  
                        article_txt = re.sub(r"\!|\"|\#|\$|\%|\&|\'|\(|\)|\*|\+|\,|\-|\.|\/|\:|\;|\<|\=|\>|\?|\@|\[|\\|\]|\^|\_|\`|\{|\||\}|\~"," ",article_txt)
                        article_txt = re.sub(r" +"," ",article_txt)
                        article_txt = article_txt.replace(u'\xa0', u' ')
                        title_and_text = ' '.join([article_title,article_txt])
                        if not article_txt == None and not article_txt == "" and len(article_txt) > 100 and is_ascii(article_txt) and not "Articles for deletion" in article_title and not "WikiProject" in article_title:
                            articles_and_titles.append(title_and_text)      #list having titles and article text
                            titles.append(article_title) 
                            print article_title

print len(articles_and_titles) 
print len(titles)                     
l = articles_and_titles[25001:30000]                   
t = titles[25001:30000] 
T = []
L = []
for t0,l0 in zip(t,l):            #no duplicate titles (hence articles) created
    if t0 not in T:
        T.append(t0)
        L.append(l0)

print len(T)
print len(L)

#computing average of word vectors obtained with fasttext
nmax = 500000
vectors = []
word2id = {}
words = []
with io.open('wiki.multi.en.vec', 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
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
i = 0
for entry,titles in zip(L,T):
    word_list = entry.strip().split(' ')
    avg_vect = 0
    flag = 0
    for w in word_list:
        for w1,v1 in zip(words,vectors):
            if w1 == w: 
                avg_vect = avg_vect + v1
                flag = 1
                break
    avg = avg_vect/len(word_list)          #avg for one article (entry)
    i = i+1
    print i 
    print avg
    if flag!=0:             #if avg not computed for an article (i.e =0) then ignore article and title
        X.append(avg)
        X_title.append(titles)

print len(L)
print len(X)
print len(T)
print len(X_title)


#sentence vectors to file
X_stack = np.vstack(X)               
with open('english.vec','a') as f:
    for t1,x1 in zip(X_title,X_stack):
        f.write(t1.encode("utf-8"))
        f.write('~')
        for x in x1:
            f.write('%s' %x)
            f.write(' ')
        f.write('\n')




                 

       
    


