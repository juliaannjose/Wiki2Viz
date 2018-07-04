# Wiki2Viz
Multi-lingual Information Retrieval System

1. For multi-lingual word visualization (to use Eng_to_Fr.py):

Download the wikipedia data dumps for English and French (also Arabic) from https://dumps.wikimedia.org/.
 Use facebook's fastText to obtain monolingual word vectors from these dump files.
 Use facebook's MUSE to obtain multi-lingual word vectors (for Eng, Fr and Ar).
 Run Eng_to_Fr.py.
 
2. For multi-lingual document retrieval system:

Using the multi-lingual word vectors obtained above, compute the average of word vectors of title inorder to get a vector that represents the article - run wiki_compute.py using the files in /data.
 Hence obtain document vectors for English, French and Arabic wikipedia docs (in /results).
 Visualize a particular query for an article (in source language:English) and its k nearest neighbors (in target language:Fr or Ar) - run wiki2viz.py
