# -*- coding: utf-8 -*-
import io
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, LabelSet, Label, CustomJS
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import TextInput
from bokeh.layouts import row

output_file("WordTranslate.html")

def load_vec(emb_path, nmax=50000):
    vectors = []
    word2id = {}
    with io.open(emb_path, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
        next(f)
        for i, line in enumerate(f):
            word, vect = line.rstrip().split(' ', 1)
            vect = np.fromstring(vect, sep=' ')
            assert word not in word2id, 'word found twice'
            vectors.append(vect)
            word2id[word] = len(word2id)
            if len(word2id) == nmax:
                break
    id2word = {v: k for k, v in word2id.items()}
    embeddings = np.vstack(vectors)
    return embeddings, id2word, word2id


src_path = 'data/wiki.multi.en.vec'
tgt_path = 'data/wiki.multi.fr.vec'
nmax = 50000  # maximum number of word embeddings to load

src_embeddings, src_id2word, src_word2id = load_vec(src_path, nmax)
tgt_embeddings, tgt_id2word, tgt_word2id = load_vec(tgt_path, nmax)
t_w = []

#getting k nearest neighbors
def get_nn(word, src_emb, src_id2word, tgt_emb, tgt_id2word, K=5):
    print("Nearest neighbors of \"%s\":" % word)
    word2id = {v: k for k, v in src_id2word.items()}
    word_emb = src_emb[word2id[word]]
    scores = (tgt_emb / np.linalg.norm(tgt_emb, 2, 1)[:, None]).dot(word_emb / np.linalg.norm(word_emb))
    k_best = scores.argsort()[-K:][::-1]
    for i, idx in enumerate(k_best):
        print('%.4f - %s' % (scores[idx], tgt_id2word[idx]))
        t_w.append(tgt_id2word[idx])

src_word = raw_input('Enter a word in English: ')
s_w= src_word
get_nn(src_word, src_embeddings, src_id2word, tgt_embeddings, tgt_id2word, K=5)


#Visualize cross lingual embeddings using PCA
from sklearn.decomposition import PCA
pca = PCA(n_components=2, whiten=True)  
pca.fit(np.vstack([src_embeddings, tgt_embeddings]))


def plot_similar_word(src_words, src_word2id, src_emb, tgt_words, tgt_word2id, tgt_emb, pca):

    Y = []
    word_labels = []
    Y.append(src_emb[src_word2id[src_words]])
    word_labels.append(src_words)
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
    s1 = ColumnDataSource(data = dict(x=x,y=y,names=word_labels, color = ['black','red','red','red','red','red'])) # src   words in black / tgt words in red
    p1= figure(plot_width = 1000, plot_height = 600, tools="lasso_select", title="Select")
    p1.circle('x','y',source = s1, alpha = 0.6)                                     
    labels1 = LabelSet(x='x', y='y', text='names', level='glyph', text_color = 'color',
                  x_offset=5, y_offset=5, source=s1, render_mode='canvas')
    
    p1.add_layout(labels1)
    text_input = TextInput(value="Eg: Cat", title="Enter a word in English: ")
    layout = row(p1, text_input)
    show(layout)

src_words = s_w
tgt_words = t_w
for sw in src_words:
    assert sw in src_word2id, '"%s" not in source dictionary' % sw
for tw in tgt_words:
    assert tw in tgt_word2id, '"%s" not in target dictionary' % sw


plot_similar_word(src_words, src_word2id, src_embeddings, tgt_words, tgt_word2id, tgt_embeddings, pca)


