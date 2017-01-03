import string
import math
import networkx as nx
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import RegexpStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords


def strip_non_ascii(word):
    return ''.join([ch for ch in word if (0 < ord(ch) < 128)])

# Iterate through the text of the document sentence by sentence,
# perform Porter Stemming, eliminate punctuation and stop words,
# set to lower case and create a graph vertex for each sentence.
# Return the resulting graph.


def normalize(sentences, stem_type):
    G = nx.DiGraph()

    # Create stemmer object of the type specified by stem_type
    stemmers = {
        '-p': PorterStemmer(),
        '-l': LancasterStemmer(),
        '-s': SnowballStemmer('english'),
        '-w': WordNetLemmatizer(),
        '-r': RegexpStemmer('ing$|s$|e$|able$', min=4)
    }

    try:
        stemmer = stemmers[stem_type]
    except KeyError:
        print('\nInvalid stemmer type passed as argument.\n')
        return

    # Define collections to reference during
    # normalization and initialize stemmer
    punc = set(string.punctuation)
    stop = stopwords.words('english')
    # Iterate over sentences, normalizing and
    # creating vertices for our graph as we go
    i = 0
    for s in sentences:
        if len(s) > 1:
            l = (s.lower()).split(' ')
            # eliminate stop words
            norm = [w for w in l if w not in stop]
            # apply stemming to each word
            if stem_type == '-w':
                norm = [stemmer.lemmatize(w) for w in norm]
            else:
                norm = [stemmer.stem(w) for w in norm]
            # remove punctuation from each word
            temp = []
            for w in norm:
                w = ''.join([l for l in w if l not in punc])
                temp += w
                temp += ' '
                norm = ''.join(temp)
            G.add_node(i, iden=i, raw=s, nrm=norm)
            i += 1
    return G

# Iterate through the vertices in the graph, for each vertex, v1,
# compute similarity to each other vertex in the list, v2. If the
# content overlap between two sentences is greater than 0 words,
# compute similarity (using the formula described by Mihalcea
# and Tarau (2004)) between them. If this is greater than zero,
# add to the graph an edge going from v1 to v2 with weight
# equal to their similarity


def similarity(graph):
    for node_i in graph.nodes():
        for node_j in graph.nodes():
            if node_i != node_j:
                norm_i = set((graph.node[node_i]['nrm']).split())
                norm_j = set((graph.node[node_j]['nrm']).split())
                # find the number of common tokens between normalized
                # sentences contained in node_i and node_j
                inter = norm_i.intersection(norm_j)
                inter_len = len(inter)
                if(inter_len > 0):
                    div = (math.log(len(norm_i)) + math.log(len(norm_j)))
                    if div != 0:
                        sim = inter_len / div
                        graph.add_edge(graph.node[node_i]['iden'], graph.node[
                                       node_j]['iden'], wgt=sim)
    return graph
