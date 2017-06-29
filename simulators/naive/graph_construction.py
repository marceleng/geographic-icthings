import random as rand
import networkx as nx
import numpy as np
from math import sqrt
import logging, string

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

def distance (n1, n2):
    return sqrt((n1.x-n2.x)**2. + (n1.y-n2.y)**2)

class Node:
    def __init__(self, x, y, name, ident):
        self.x = x
        self.y = y
        self.neigh = []
        self.seen = False
        self.name = name
        self.id=ident

    def is_neigh(self, other):
        return distance(self, other) < 1

    @staticmethod
    def uniform_node(size_x, size_y, name, ident):
        return Node(rand.uniform(0,size_x), rand.uniform(0,size_y), name, ident)

    @staticmethod
    def create_graph (number_of_nodes, node_degree):
        space_size = int(sqrt(np.pi*float(number_of_nodes)/node_degree))
        nodes=[]
        for i in xrange(number_of_nodes):
            name = ''.join(rand.choice(string.ascii_lowercase) for _ in xrange(0,number_of_nodes))
            node = Node.uniform_node(space_size, space_size, name, i)
            for n in nodes:
                if n.is_neigh(node):
                    n.neigh.append(node)
                    node.neigh.append(n)
            nodes.append(node)
        return nodes

    def __eq__(self, other):
        return self.x is other.x and self.y is other.y and self.name==other.name

    def __hash__(self):
        return hash((self.x, self.y, self.name))

def graph_from_topo(topo):
    G=nx.Graph()
    G.add_nodes_from(map(lambda x : x.id, topo))
    for node in topo:
        for n in node.neigh:
            if n.id > node.id:
                G.add_edge(node.id, n)
    return G

def plot_graph(topo):
    import matplotlib.pyplot as plt
    plt.close()
    pos={}
    label = {}
    for node in topo:
        pos[node.id] = (node.x, node.y)
        label[node.id] = node.id
    nx.draw_networkx_labels(graph_from_topo(topo), pos, label)
    nx.draw(graph_from_topo(topo), pos)
    plt.show()
