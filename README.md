# Wiki2Viz

 A Multi-lingual Information Retrieval System: a searchable interface for growing collection of multilingual online information.
 
 ## Requirements
 
 For the word-similarity evaluation script you will need:

    Python version 2.7 or >=3.4
    NumPy, SciPy, fastText & MUSE

To run demo.py you will need:

    Python version 2.7 or >=3.4
    NumPy, SciPy, Scikit-learn & Bokeh
    
   
## Usage Instructions

### To use the word-similarity evaluation script:

   1. Download the wikipedia data dumps for English, French and Arabic from https://dumps.wikimedia.org/.
   2. Use fastText to obtain monolingual word vectors from these dump files 
   
     $ mkdir data
     $ cd data
     $ wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
     $ bzip2 https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2 -d
     $ perl wikifil.pl data/enwiki.xml > data/processed
     $ ./fasttext skipgram -input data/processed -output data/wiki.en
     
   alternatively, use facebook's pretrained word vectors from: https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md

   3. Use MUSE to obtain multi-lingual word vectors 
   
     $ python supervised.py --src_lang en --tgt_lang es --src_emb data/wiki.en.vec --tgt_emb data/wiki.es.vec --n_refinement 5 --dico_train default
     
   alternatively, use facebook's supervised word embedding's aligned in a single vector space: https://github.com/facebookresearch/MUSE
     
   4. Run the word-similarity script to visualize the cross-lingual word embeddings.
       
     $ python ./word_similarity.py
     
     
     
 ### To run the demo application (Multi-Lingual Information Retrieval System):
 
   1. Preprocess the xml file to get the titles:
   
     $ python ./preprocess.py
     
   2. Compute the average of vectors of the words in the title:
    
     $ python ./compute.py
     
   3. Finally, run the demo application:
   
     $ bokeh serve demo.py
     
     
## References
  
   Datasets: https://dumps.wikimedia.org

   Word embeddings generation: https://fasttext.cc/docs/en/unsupervised-tutorial.html
                              https://github.com/facebookresearch/fastText

   Monolingual word embeddings allignment: https://github.com/facebookresearch/MUSE

   KNN Algorithm: https://www.analyticsvidhya.com/blog/2018/03/introduction-k-neighbours-algorithm-clustering/

   Visualization:
                 http://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
                 https://bokeh.pydata.org/en/latest/
                 
                 
#### Contact: julia.ann.1997@hotmail.com               
 
  
    
 
