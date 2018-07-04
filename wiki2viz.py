# -*- coding: utf-8 -*-
import io
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, LabelSet, Label, CustomJS, OpenURL, TapTool, Range1d, HoverTool
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import TextInput, Slider
from bokeh.layouts import row
from sklearn.decomposition import PCA
from bokeh.io import curdoc

output_file("DocRetrieval.html")

def load_vec(emb_path, nmax=50000):
    vectors = []
    word2id = {}
    with io.open(emb_path, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
        next(f)
        for i, line in enumerate(f):
            word, vect = line.rstrip().split('~', 1)
            vect = np.fromstring(vect, sep=' ')
            assert word not in word2id, 'word found twice'
            vectors.append(vect)
            word2id[word] = len(word2id)
            if len(word2id) == nmax:
                break
    id2word = {v: k for k, v in word2id.items()}
    embeddings = np.vstack(vectors)
    return embeddings, id2word, word2id


src_path = 'results/eng_titles.vec' 
tgt_path = 'results/french_titles.vec'            #ar_titles.vec for arabic
nmax = 50000  # maximum number of word embeddings to load

src_embeddings, src_id2word, src_word2id = load_vec(src_path, nmax)
tgt_embeddings, tgt_id2word, tgt_word2id = load_vec(tgt_path, nmax)


user_query = TextInput(value = 'football', title="Search for an article: ")
no_of_articles = Slider(title="Number of articles", start=1, end=50, value=5, step=1)

source = ColumnDataSource(data = dict(x=[],y=[],names=[])) 
hover = HoverTool(
        tooltips=[
            ("Title", "@names"),
        ]
)
p1= figure(plot_width = 950, plot_height = 600, tools=[hover,'tap','reset','box_zoom'], title="Click to view")
p1.circle('x','y',source = source, alpha = 0.6,size=9, color = 'red')  

url = "https://fr.wikipedia.org/wiki/@names"       #https://ar.wikipedia.org/wiki/@names
taptool = p1.select(type=TapTool)
taptool.callback = OpenURL(url=url)

p1.x_range = Range1d(-8,8)
p1.y_range = Range1d(-8,8)


def select_articles():
    s_w = " "
    g = 1
    K = no_of_articles.value
    u = user_query.value
    src_word = u.encode('utf-8')
    src_word = src_word.lower()
    src_word = src_word.replace('–',' ')
    src_word = src_word.replace('-',' ')
    with open('results/eng_titles.vec', 'r') as f:
        for line in f:
            word1 = line.rstrip().split('~')
            w = word1[0]
            if src_word in w:
                g = 1
    if g == 1:
        print "Article not present; related articles:"
        vectors1 = []
        words1 = []
        word2id1 = {}
        with io.open('data/wiki.multi.en.vec', 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
            next(f)
            for i, line in enumerate(f):
                word1, vect1 = line.rstrip().split(' ', 1)
                vect1 = np.fromstring(vect1, sep=' ')
                assert word1 not in word2id1, 'word found twice'
                vectors1.append(vect1)
                words1.append(word1)
                word2id1[word1] = len(word2id1)
                if len(word2id1) == nmax:
                    break
        avg_vect = 0  
        c = 0 
        for w in src_word.split(' '):
            for w2,v2 in zip(words1,vectors1):
                if w in w2: 
                    avg_vect = avg_vect + v2
                    c = c+1
                    break
        avg = avg_vect/c 
        t_w = []
        scores = (tgt_embeddings / np.linalg.norm(tgt_embeddings, 2, 1)[:, None]).dot(avg / np.linalg.norm(avg))
        k_best = scores.argsort()[-K:][::-1]
        for i, idx in enumerate(k_best):
            print('%.4f - %s' % (scores[idx], tgt_id2word[idx]))
            t_w.append(tgt_id2word[idx])

    #Visualize cross lingual embeddings using PCA
    pca = PCA(n_components=2, whiten=True)  
    pca.fit(np.vstack([tgt_embeddings]))
    
    Y = []
    word_labels = []
    for tw in t_w:
        Y.append(tgt_embeddings[tgt_word2id[tw]])
        word_labels.append(tw)
        
    # find tsne coords for 2 dimensions
    Y = pca.transform(Y)
    x_coords = Y[:, 0]
    y_coords = Y[:, 1]

    #Bokeh visualization
    x = x_coords
    y = y_coords
    S = ColumnDataSource(data = dict(x=x,y=y,names=word_labels))
    print "====================================="
    return x,y,word_labels
    
def update(): 
    x,y,names1 = select_articles()
    source.data = dict(
        x=x,
        y=y,
        names=names1,
    )


controls = [user_query,no_of_articles]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [inputs, p1],
], sizing_mode=sizing_mode)

update() 


curdoc().add_root(l)
curdoc().title = "Multi-lingual IR system"



