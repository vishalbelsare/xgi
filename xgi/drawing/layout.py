import networkx as nx
from networkx.utils import random_state

import xgi

__all__ = [
    "random_layout",
    "barycenter_spring_layout",
]

@random_state(3)
def random_layout(H, center=None, dim=2, seed=None):
    """Position nodes uniformly at random in the unit square. Exactly as networkx does.
    For every node, a position is generated by choosing each of dim
    coordinates uniformly at random on the interval [0.0, 1.0).
    NumPy (http://scipy.org) is required for this function.
    
    Parameters
    ----------
    H : xgi HyperGraph or list of nodes
        A position will be assigned to every node in HG.
    center : array-like or None
        Coordinate pair around which to center the layout.
    dim : int
        Dimension of layout.
    seed : int, RandomState instance or None  optional (default=None)
        Set the random state for deterministic node layouts.
        If int, `seed` is the seed used by the random number generator,
        if numpy.random.RandomState instance, `seed` is the random
        number generator,
        if None, the random number generator is the RandomState instance used
        by numpy.random.
        
    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node
        
    Examples
    --------
    >>> H = nx.stupid_hypergraph()
    >>> pos = nx.random_layout(H)
    """
    import numpy as np

    H, center = nx.drawing. nx.drawing.layout._process_params(H, center, dim)
    pos = seed.rand(len(H), dim) + center
    pos = pos.astype(np.float32)
    pos = dict(zip(HG, pos))

    return pos

def barycenter_spring_layout(H, return_phantom_graph=False):
    
    # Creating the projected networkx Graph, I will fill it manually
    G = nx.Graph()
    # Adding real nodes
    G.add_nodes_from(list(H.nodes))
    
    phantom_node_id = H.number_of_nodes() #the first id is N (the first node is 0)
    #Looping over the hyperedges of different order
    for d in range(1, H.max_edge_order()+1):  
        #Hyperedges of order d (d=1: links, etc.)
        for he in H.edges_of_order(d).values():
            #Adding one phantom node for each hyperedge and linking it to the nodes of the hyperedge
            for n in he:
                G.add_edge(phantom_node_id, n)
            phantom_node_id+=1
                
    # Creating a dictionary for the position of the nodes with the standard spring layout
    pos_with_phantom_nodes = nx.spring_layout(G)
    
    # Retaining only the positions of the real nodes
    pos = {k: pos_with_phantom_nodes[k] for k in list(H.nodes)}
    
    if return_phantom_graph:
        return pos, G
    else:
        return pos
