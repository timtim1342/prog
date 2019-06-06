import gensim
import networkx as nx
import urllib.request
import matplotlib.pyplot as plt
from networkx.algorithms import community

from flask import Flask, render_template, request
from os.path import join

def download_model():
    '''urllib.request.urlretrieve(
        "http://rusvectores.org/static/models/rusvectores2/ruscorpora_mystem_cbow_300_2_2015.bin.gz",
        "ruscorpora_mystem_cbow_300_2_2015.bin.gz")'''
    m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'
    model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=True)
    return model

def words_neighbors(word):
    model = download_model()
    if word in model:
        res = []
        for i in model.most_similar(positive=[word], topn=10):
            res.append((str(i[0]), i[1]))
        return res
    else:
        return 'no %s' % word

def grph(word, res):
    g = nx.Graph()
    g.add_node(word)
    for w in res:
        g.add_node(w[0], label=w[0])
        g.add_edge(word, w[0], weight=w[1])
        res2 = words_neighbors(w[0])
        for n in res2:
            g.add_node(n[0], label=n[0])
            g.add_edge(w[0], n[0], weight=n[1])
    return g

def vis(g, word):
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_color='red', node_size=50)
    nx.draw_networkx_edges(g, pos, edge_color='yellow')
    nx.draw_networkx_labels(g, pos, font_size=5, font_family='Arial')
    plt.axis('off')
    #plt.show()
    file_name = word + '.png'
    pth = join('static', file_name)
    plt.savefig(pth, dpi=400)
    plt.clf()

def centr(g):
    deg = nx.degree_centrality(g)
    dc = [nodeid for nodeid in sorted(deg, key=deg.get, reverse=True)]
    deg = nx.closeness_centrality(g)
    cc = [nodeid for nodeid in sorted(deg, key=deg.get, reverse=True)]
    deg = nx.betweenness_centrality(g)
    bc = [nodeid for nodeid in sorted(deg, key=deg.get, reverse=True)]
    deg = nx.eigenvector_centrality(g)
    ec = [nodeid for nodeid in sorted(deg, key=deg.get, reverse=True)]
    return dc, cc, bc, ec

def more_inf(g):
    r = nx.radius(g)
    d = nx.diameter(g)
    ka = nx.degree_pearson_correlation_coefficient(g)
    p = nx.density(g)
    kc = nx.average_clustering(g)
    nn = g.number_of_nodes()
    ne = g.number_of_edges()
    return r, d, p, ka, kc, nn, ne

def comm(g):
    com = community.greedy_modularity_communities(g)
    return com




app = Flask(__name__)

@app.route('/')
def index():
    if request.args:
        wrd = str(request.args['word'])
        try:
            g = grph(wrd, words_neighbors(wrd))
            vis(g, wrd)
            file_name = wrd + '.png'
            r, d, p, ka, kc, nn, ne = more_inf(g)
            dc, cc, bc, ec = centr(g)
            l = range(5)
            return render_template('results.html', filename=file_name, r=r, d=d, p=p, ka=ka, kc=kc, nn=nn, ne=ne, l=l,
                                   dc=dc[:5], cc=cc[:5], bc=bc[:5], ec=ec[:5])
        except IndexError:
            return render_template('oops.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)
    #g = grph('дом_S', words_neighbors('дом_S'))
    #vis(g)
    #centr(g)
    #print(more_inf(g))
    #print(comm(g))
