# -*- coding: utf-8 -*-
import io
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, LabelSet, Label, CustomJS, OpenURL, TapTool, Range1d, HoverTool, Div
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import TextInput, Slider, PreText, DataTable, TableColumn, HTMLTemplateFormatter, Button
from bokeh.layouts import row
from sklearn.decomposition import PCA
from bokeh.io import curdoc
from os.path import dirname, join

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)


#load the trained title vectors obtained previously
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

nmax = 50000  # maximum number of word embeddings to load
src_path = 'results/eng_titles.vec' 
tgt_path = 'results/fr_titles.vec'            #ar_titles.vec for arabic
src_embeddings, src_id2word, src_word2id = load_vec(src_path, nmax)
tgt_embeddings, tgt_id2word, tgt_word2id = load_vec(tgt_path, nmax)



#User interface and visualization (using Bokeh)
user_query = TextInput(value = 'medicine', title="Search for an article: ")
no_of_articles = Slider(title="Number of articles", start=1, end=50, value=5, step=1)
source = ColumnDataSource(data = dict(x=[],y=[],names=[],size=[],word_labels_display=[],rank=[])) 
columns = [
        TableColumn(field="rank", title="No.",width = 2),
       TableColumn(field="names", title="Articles", formatter = HTMLTemplateFormatter(template=
    '<a href="https://fr.wikipedia.org/wiki/<%= names %>" target="_blank"><%= value %></a>')),
    ]
data_table = DataTable(source=source, columns=columns, width=280, height=380, selectable= True,  index_position = None)
hover = HoverTool(
        tooltips=[
            ("Title", "@names"),
        ]
)
p1= figure(plot_width = 700, plot_height = 500, tools=[hover,'tap','reset','box_zoom'], title="Click to view")
p1.circle('x','y',source = source, alpha = 0.6,size='size', color = '#0d8ba1', nonselection_fill_color="#0d8ba1")  
labels1 = LabelSet(x='x', y='y', text='word_labels_display', level='glyph', text_color = '#0d8ba1',
                 x_offset=5, y_offset=5, source=source, render_mode='canvas')

url = "https://fr.wikipedia.org/wiki/@names"       #https://ar.wikipedia.org/wiki/@names
taptool = p1.select(type=TapTool)
taptool.callback = OpenURL(url=url)

p1.x_range = Range1d(-2,1.5)
p1.y_range = Range1d(-2,2)
p1.add_layout(labels1)


#function that selects articles according to users query (finding K nearest neighbors)
def select_articles():
    s_w = " "
    g = 1
    K = no_of_articles.value
    u = user_query.value
    src_word = u.encode('utf-8')
    src_word = src_word.lower()
    src_word = src_word.replace('–',' ')
    src_word = src_word.replace('-',' ')
    if g == 1:
        print "====================================="
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

    #PCA to reduce dimensions
    pca = PCA(n_components=2, whiten=True)  
    pca.fit(np.vstack([tgt_embeddings]))
    
    Y = []
    word_labels = []
    for tw in t_w:
        Y.append(tgt_embeddings[tgt_word2id[tw]])
        word_labels.append(tw)
        
    #get x and y coordinates for the selected articles
    Y = pca.transform(Y)
    x_coords = Y[:, 0]
    y_coords = Y[:, 1]
    x = x_coords
    y = y_coords
    S = ColumnDataSource(data = dict(x=x,y=y,names=word_labels))
    k_s = []
    word_labels_display2 = []
    rank_of_articles = []
    for i in range(K, 0, -1):
        if i>=15:
            k_s.append(15*3)
        else:
            k_s.append(i*3)
    #print k_s
    for i in word_labels:
        i = i[:5] + "..."
        word_labels_display2.append(i)
    for i in range(1,K+1,1):
        rank_of_articles.append(i)
    return x,y,word_labels,k_s,word_labels_display2,rank_of_articles


#function that updates the source according to users query (or slider value)
def update(): 
    x,y,names1,sz,word_labels_display1,rank_of_articles = select_articles()
    print rank_of_articles
    source.data = dict(
        x=x,
        y=y,
        names=names1,
        size=sz,
        word_labels_display = word_labels_display1,
        rank = rank_of_articles
    )
    


controls = [user_query,no_of_articles,data_table]
for control in controls: 
    if control != data_table:
        control.on_change('value', lambda attr, old, new: update())

#layout of plot and widgets
sizing_mode = 'fixed'  
inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs,p1],
], sizing_mode=sizing_mode)

update()   
curdoc().add_root(l)
curdoc().title = "Multi-lingual IR system"
