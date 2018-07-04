# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import re
import os
import argparse
import numpy as np
import io
from sklearn.manifold import TSNE
import bokeh.plotting as bp
from bokeh.plotting import save
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource, LabelSet, Label, CustomJS,OpenURL, TapTool
from bokeh.plotting import figure, output_file, show
from sklearn.decomposition import PCA
from sklearn import manifold


output_file("sentence_embeddings_fr.html")

def is_ascii(s):
    return all(ord(c) < 128 for c in s)


tree = ET.parse('frwiki.xml')          #arwiki.xml for arabic
root = tree.getroot()

articles_and_titles = []
titles = []
for i,page in enumerate(root.findall('{http://www.mediawiki.org/xml/export-0.10/}page')):
    for p in page:  
        if p.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
            article_title = p.text 
            if not article_title == None: 
                article_title = re.sub(r"\"|\#|\~"," ",article_title)
            print article_title
        if p.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
            for x in p:
                if x.tag == "{http://www.mediawiki.org/xml/export-0.10/}text":                    
                    article_txt = x.text
                    if not article_txt == None:                                                
                        article_txt = article_txt[ : article_txt.find("==")]
                        article_txt = re.sub(r"{{.*}}","",article_txt)
                        article_txt = re.sub(r"\[\[Fichier:.*\]\]","",article_txt)    #article_txt = re.sub(r"\[\[ملف:.*\]\]","",article_txt)
                        article_txt = re.sub(r"\[\[Média:.*\]\]","",article_txt)      #article_txt = re.sub(r"\[\[ميديا:.*\]\]","",article_txt)
                        article_txt = re.sub(r"\n: \'\'.*","",article_txt)
                        article_txt = re.sub(r"\n!.*","",article_txt)
                        article_txt = re.sub(r"^:\'\'.*","",article_txt)
                        article_txt = re.sub(r"&nbsp","",article_txt)
                        article_txt = re.sub(r"http\S+","",article_txt)
                        article_txt = re.sub(r"\d+","",article_txt)   
                        article_txt = re.sub(r"\(.*\)","",article_txt)
                        article_txt = re.sub(r"Catégorie:.*","",article_txt)         #article_txt = re.sub(r"التصنيف:.*","",article_txt) and article_txt = re.sub(r"ويكيبيديا:.*","",article_txt)
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
                        title_and_text = ' '.join([article_title,article_txt])
                        if not article_txt == None and not article_txt == "" and len(article_txt) > 100:
                            articles_and_titles.append(title_and_text)      #list having titles and article text
                            titles.append(article_title)

l = articles_and_titles[:10000]                 
t = titles[:10000] 
T = []
L = []
for t0,l0 in zip(t,l):            #no duplicate titles (hence articles) created
    if t0 not in T:
        T.append(t0)
        L.append(l0)

print len(T)
print len(L)
print "Computing vectors:"
              
#computing average of word vectors obtained with fasttext
nmax = 500000
vectors = []
word2id = {}
words = []
with io.open('wiki.multi.fr.vec', 'r', encoding='utf-8', newline='\n', errors='ignore') as f:        #wiki.multi.ar.vec for arabic
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
    avg = avg_vect/len(word_list)          #avg for one article (entry)
    i = i+1
    #print i 
    #print avg
    #print TITLE
    if flag!=0:             #if avg not computed for an article (i.e =0) then ignore article and title
        X.append(avg)
        X_title.append(TITLE)

print "writing to file..."

#sentence vectors to file
X_stack = np.vstack(X)               #vstack for output to file 
with open('fr_titles.vec','a') as f:       #ar_titles.vec
    for t1,x1 in zip(X_title,X_stack):
        f.write(t1.encode("utf-8"))
        f.write('~')
        for x in x1:
            f.write('%s' %x)
            f.write(' ')
        f.write('\n')

print "performing tsne reduction..."
#dimensionality reduction using tsne
tSNE = manifold.TSNE(n_components = 2)
tSNE_data = tSNE.fit_transform(X)


#plotting tSNE_data using Bokeh 
x = [tSNE_data[i][0] for i in range(len(tSNE_data))]
y = [tSNE_data[j][1] for j in range(len(tSNE_data))]

s1 = ColumnDataSource(data = dict(x=x,y=y,names=X_title))
p1= figure(plot_width = 1300, plot_height = 1000, tools="tap", title="Click to view")
p1.circle('x','y',source = s1, alpha = 0.6,size = 7)
labels1 = LabelSet(x='x', y='y', text='names', level='glyph',
                  x_offset=5, y_offset=5, source=s1, render_mode='canvas')



url = "https://fr.wikipedia.org/wiki/@names"          #https://ar.wikipedia.org/wiki/@names
taptool = p1.select(type=TapTool)
taptool.callback = OpenURL(url=url)


p1.add_layout(labels1)
show(p1)
