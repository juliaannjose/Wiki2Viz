# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import re


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


tree = ET.parse('data/frwiki_1.xml')
root = tree.getroot()

articles = []
titles = []

for i,page in enumerate(root.findall('{http://www.mediawiki.org/xml/export-0.10/}page')):
    for p in page:  
        if p.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
            article_title = p.text 
            if not article_title == None: 
                article_title = re.sub(r"\"|\#|\~"," ",article_title)
            #print article_title
        if p.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
            for x in p:
                if x.tag == "{http://www.mediawiki.org/xml/export-0.10/}text":                    
                    article_txt = x.text
                    if not article_txt == None:                                                
                        article_txt = article_txt[ : article_txt.find("==")]
                        article_txt = re.sub(r"{{.*}}","",article_txt)
                        article_txt = re.sub(r"\[\[Fichier:.*\]\]","",article_txt)
                        article_txt = re.sub(r"\[\[Média:.*\]\]","",article_txt)
                        article_txt = re.sub(r"\n: \'\'.*","",article_txt)
                        article_txt = re.sub(r"\n!.*","",article_txt)
                        article_txt = re.sub(r"^:\'\'.*","",article_txt)
                        article_txt = re.sub(r"&nbsp","",article_txt)
                        article_txt = re.sub(r"http\S+","",article_txt)
                        article_txt = re.sub(r"\d+","",article_txt)   
                        article_txt = re.sub(r"\(.*\)","",article_txt)
                        article_txt = re.sub(r"Catégorie:.*","",article_txt)
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
                            articles.append(title_and_text)      #list having title and article text
                            titles.append(article_title)

T = []
L = []
for t0,l0 in zip(titles,articles):            #no duplicate titles (or articles) created
    if t0 not in T:
        T.append(t0)
        L.append(l0)

with open('results/preprocessed_articles.txt','w') as F:
    for articles in L:
        F.write(articles.encode("utf-8"))
        F.write('\n')

with open('results/preprocessed_titles.txt','w') as f:
    for titles in T:
        f.write(titles.encode("utf-8"))
        f.write('\n')
