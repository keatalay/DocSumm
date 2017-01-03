import sys
import re
import codecs
import tr_func
import operator
import networkx as nx
import urllib2
from goose import Goose
from nltk.tokenize.punkt import PunktSentenceTokenizer

# Assign variables to contain arguments passed
# to script and read in target document.
if len(sys.argv) < 5:
    stem_type = '-p'
else:
    stem_type = sys.argv[4]

doc_path = sys.argv[1]
doc_type = sys.argv[3]
sum_perc = float(sys.argv[2])

# Determine if the target document is a webpage or
# a text document stored locally
if doc_type == '-l':
    doc = open(doc_path, 'r')
    doc = codecs.open(doc_path, encoding='utf-8', mode='r')
    text = doc.read()
    text = text.encode('ascii', 'ignore')
elif doc_type == '-w':
    g = Goose()
    # determine if this is a New York Times url, in which case
    # we cannot use goose alone and must also rely on urllib2
    sites = 'www.(nytimes)|(theonion)'
    if re.search(sites, doc_path):
        print('handling special case')
        # do the nytimes thing
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(doc_path)
        raw_html = response.read()
        article = g.extract(raw_html=raw_html)
        text = article.cleaned_text.encode('ascii', 'ignore')
    else:
        # just use goose
        article = g.extract(url=doc_path)
        text = article.cleaned_text.encode('ascii', 'ignore')

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

if doc_type == '-w':
    out_name = article.title.replace(' ', '_') + '_summaryary.txt'

out = open(out_name, 'w')
sum_length = int(sum_perc * len(sentences))
out.write('\t')
for x in range(0, sum_length):
    out.write(graph.node[sorted_rankings[x][0]]['raw'] + ' ')
