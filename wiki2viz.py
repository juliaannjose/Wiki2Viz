# -*- coding: utf-8 -*-
import io
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, LabelSet, Label, CustomJS, OpenURL, TapTool, Range1d
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import TextInput
from bokeh.layouts import row
from sklearn.decomposition import PCA

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


src_path = 'results/english.vec'
tgt_path = 'results/french.vec'
nmax = 50000  # maximum number of word embeddings to load

src_embeddings, src_id2word, src_word2id = load_vec(src_path, nmax)
tgt_embeddings, tgt_id2word, tgt_word2id = load_vec(tgt_path, nmax)
t_w = []

#getting k nearest neighbors
def get_nn(word, src_emb, src_id2word, tgt_emb, tgt_id2word, K=3):
    print("Nearest neighbors of \"%s\":" % word)
    word2id = {v: k for k, v in src_id2word.items()}
    wd = word.decode('utf-8')
    word_emb = src_emb[word2id[wd]]
    scores = (tgt_emb / np.linalg.norm(tgt_emb, 2, 1)[:, None]).dot(word_emb / np.linalg.norm(word_emb))
    k_best = scores.argsort()[-K:][::-1]
    for i, idx in enumerate(k_best):
        print('%.4f - %s' % (scores[idx], tgt_id2word[idx]))
        t_w.append(tgt_id2word[idx])

src_word = raw_input('Search for an article: ')
with open('results/english.vec', 'r') as f:
    for line in f:
        word1 = line.rstrip().split('~')
        w = word1[0]
        if src_word in w:
            get_nn(w, src_embeddings, src_id2word, tgt_embeddings, tgt_id2word, K=3)

#Visualize cross lingual embeddings using PCA
pca = PCA(n_components=2, whiten=True)  
pca.fit(np.vstack([tgt_embeddings]))


def plot_similar_word(src_words, src_word2id, src_emb, tgt_words, tgt_word2id, tgt_emb, pca):

    Y = []
    word_labels = []
    for tw in tgt_words:
        Y.append(tgt_emb[tgt_word2id[tw]])
        word_labels.append(tw)
    # find tsne coords for 2 dimensions
    Y = pca.transform(Y)
    x_coords = Y[:, 0]
    y_coords = Y[:, 1]

    #Bokeh visualization
    x = x_coords
    y = y_coords
    s1 = ColumnDataSource(data = dict(x=x,y=y,names=word_labels)) 
    p1= figure(plot_width = 1350, plot_height = 600, tools="tap,box_zoom,reset", title="Click to view")
    p1.circle('x','y',source = s1, alpha = 0.6,size=8)                                     
    labels1 = LabelSet(x='x', y='y', text='names', level='glyph', text_color = 'red',
                  x_offset=5, y_offset=5, source=s1, render_mode='canvas')
    
    url = "https://fr.wikipedia.org/wiki/@names"
    taptool = p1.select(type=TapTool)
    taptool.callback = OpenURL(url=url)

    p1.x_range = Range1d(-8,8)
    p1.y_range = Range1d(-8, 8)

    p1.add_layout(labels1)
    text_input = TextInput(value="Eg: Australian Football", title="Search for an article: ")
    layout = row(p1, text_input)
    show(layout)


tgt_words = t_w
plot_similar_word(tgt_words, tgt_word2id, tgt_embeddings, pca)

