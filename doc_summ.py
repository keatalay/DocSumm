import sys
import math
import codecs
import tr_func
import operator
import networkx as nx
from nltk.tokenize.punkt import PunktSentenceTokenizer

# Assign variables to contain arguments passed
# to script and read in target document.
if len(sys.argv) < 4:
    stem_type = '-p'
else:
    stem_type = sys.argv[3]

doc_path = sys.argv[1]
sum_perc = float(sys.argv[2])
doc = open(doc_path, 'r')
doc = codecs.open(doc_path, encoding='utf-8', mode='r')

text = doc.read()
text = text.encode('ascii', 'ignore')

# Tokenize the document to be summarized
tok = PunktSentenceTokenizer()

doc = ' '.join(text.strip().split('\n'))
sentences = tok.tokenize(doc)

# Pass tokenized document to tr_func.normalize
# which generates a graph containing vertices
# for each sentence in the document
graph = tr_func.normalize(sentences, stem_type)

# Compute the similarty between each vertex,
# use these similarities to create edges.
graph = tr_func.similarity(graph)

# Use the nltk pagerank algorithm to generate
# rankings.
rankings = nx.pagerank(graph, weight='wgt')

# Sort rankings in descending order.
sorted_rankings = sorted(
    rankings.items(), key=operator.itemgetter(1), reverse=True)

# Open a new file and write the document summary.
out = open(doc_path.replace('.txt', '') + '_Summary.txt', 'w')
sum_length = int(sum_perc * len(sentences))
out.write('\t')
for x in range(0, sum_length):
    out.write(graph.node[sorted_rankings[x][0]]['raw'] + ' ')
