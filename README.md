# Wiki2Viz
Creating a cross-lingual document retrieval system 

1. For cross-lingual word visualization (to use Eng_to_Fr.py):

Download the wikipedia data dumps for English and French from https://dumps.wikimedia.org/.
 Use facebook's fastText to obtain monolingual word vectors from these dump files.
 Use facebook's MUSE to obtain cross-lingual word vectors (for Eng and Fr).
 Place these in /data and run Eng_to_Fr.py.
 
2. For cross-lingual document retrieval system:

Using the cross-lingual word vectors obtained above, compute the average of word vectors occuring in a single article inorder to get a vector that represents the article - run wiki_compute.py using the files in /data.
 Hence obtain document vectors for English as well as French wikipedia docs (in /results).
 Visualize a particular query for an article (in eng) and its k nearest neighbors (in fr) - run wiki2viz.py
