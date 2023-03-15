"""Algorithms to compute node positions for drawing."""

import random

import networkx as nx

from .. import convert
from ..classes import SimplicialComplex, max_edge_order

__all__ = [
    "random_layout",
    "pairwise_spring_layout",
    "barycenter_spring_layout",
    "weighted_barycenter_spring_layout",
]


def random_layout(H, center=None, dim=2, seed=None):
    """Position nodes uniformly at random in the unit square. Exactly as networkx does.
    For every node, a position is generated by choosing each of dim
    coordinates uniformly at random on the interval [0.0, 1.0).
    NumPy (http://scipy.org) is required for this function.

    Parameters
    ----------
    H : HyperGraph or list of nodes
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
    >>> import xgi
    >>> N = 50
    >>> ps = [0.1, 0.01]
    >>> H = xgi.random_hypergraph(N, ps)
    >>> pos = xgi.random_layout(H)
    """
    import numpy as np

    if isinstance(H, SimplicialComplex):
        H = convert.from_simplicial_complex_to_hypergraph(H)

    if seed is not None:
        np.random.seed(seed)

    H, center = nx.drawing.layout._process_params(H, center, dim)
    pos = np.random.rand(len(H), dim) + center
    pos = pos.astype(np.float32)
    pos = dict(zip(H, pos))

    return pos


def pairwise_spring_layout(H, seed=None):
    """
    Position the nodes using Fruchterman-Reingold force-directed
    algorithm using the graph projection of the hypergraph
    or the hypergraph constructed from the simplicial complex.

    Parameters
    ----------
    H : Hypergraph or SimplicialComplex
        A position will be assigned to every node in H.
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

    Notes
    -----
    If a simplicial complex is provided the results will be based on the
    hypergraph constructed from its maximal simplices.

    See also
    --------
    barycenter_spring_layout
    weighted_barycenter_spring_layout

    Examples
    --------
    >>> import xgi
    >>> N = 50
    >>> ps = [0.1, 0.01]
    >>> H = xgi.random_hypergraph(N, ps)
    >>> pos = xgi.pairwise_spring_layout(H)
    """

    if seed is not None:
        random.seed(seed)

    if isinstance(H, SimplicialComplex):
        H = convert.from_simplicial_complex_to_hypergraph(H)
    G = convert.convert_to_graph(H)
    pos = nx.spring_layout(G, seed=seed)
    return pos


def barycenter_spring_layout(H, return_phantom_graph=False, seed=None):
    """
    Position the nodes using Fruchterman-Reingold force-directed
    algorithm using an augmented version of the the graph projection
    of the hypergraph (or simplicial complex), where phantom nodes
    (barycenters) are created for each edge composed by more than two nodes.
    If a simplicial complex is provided the results will be based on the
    hypergraph constructed from its maximal simplices.

    Parameters
    ----------
    H : xgi Hypergraph or SimplicialComplex
        A position will be assigned to every node in H.
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

    See also
    --------
    pairwise_spring_layout
    weighted_barycenter_spring_layout

    Examples
    --------
    >>> import xgi
    >>> N = 50
    >>> ps = [0.1, 0.01]
    >>> H = xgi.random_hypergraph(N, ps)
    >>> pos = xgi.barycenter_spring_layout(H)

    """
    if seed is not None:
        random.seed(seed)

    if isinstance(H, SimplicialComplex):
        H = convert.from_simplicial_complex_to_hypergraph(H)

    # Creating the projected networkx Graph, I will fill it manually
    G = nx.Graph()

    # Adding real nodes
    G.add_nodes_from(list(H.nodes))

    # Adding links (edges composed by two nodes only, for which we don't use phantom nodes
    for i, j in H.edges.filterby("order", 1).members():

        G.add_edge(i, j)

    # Adding phantom nodes and connections therein
    # I will start from the first int node-label available
    try:
        phantom_node_id = max([n for n in H.nodes if isinstance(n, int)]) + 1
    except ValueError:
        # The list of node-labels has no integers, so I start from 0
        phantom_node_id = 0

    # Looping over the hyperedges of different order (from triples up)
    for d in range(2, max_edge_order(H) + 1):
        # Hyperedges of order d (d=2: triplets, etc.)
        for he in H.edges.filterby("order", d).members():
            # Adding one phantom node for each hyperedge and linking it to the nodes of the hyperedge
            for n in he:
                G.add_edge(phantom_node_id, n)
            phantom_node_id += 1

    # Creating a dictionary for the position of the nodes with the standard spring layout
    pos_with_phantom_nodes = nx.spring_layout(G, seed=seed)

    # Retaining only the positions of the real nodes
    pos = {k: pos_with_phantom_nodes[k] for k in list(H.nodes)}

    if return_phantom_graph:
        return pos, G
    else:
        return pos


def weighted_barycenter_spring_layout(H, return_phantom_graph=False, seed=None):
    """
    Position the nodes using Fruchterman-Reingold force-directed
    algorithm using an augmented version of the the graph projection
    of the hypergraph (or simplicial complex), where phantom nodes (barycenters) are created
    for each edge of order d>1 (composed by more than two nodes).
    Weights are assigned to all hyperedges of order 1 (links) and
    to all connections to phantom nodes within each hyperedge
    to keep them together. Weights scale as the order d.
    If a simplicial complex is provided the results will be based on the
    hypergraph constructed from its maximal simplices.

    Parameters
    ----------
    H : Hypergraph or SimplicialComplex
        A position will be assigned to every node in H.
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

    See also
    --------
    pairwise_spring_layout
    barycenter_spring_layout

    Examples
    --------
    >>> import xgi
    >>> N = 50
    >>> ps = [0.1, 0.01]
    >>> H = xgi.random_hypergraph(N, ps)
    >>> pos = xgi.weighted_barycenter_spring_layout(H)
    """
    if seed is not None:
        random.seed(seed)

    if isinstance(H, SimplicialComplex):
        H = convert.from_simplicial_complex_to_hypergraph(H)

    # Creating the projected networkx Graph, I will fill it manually
    G = nx.Graph()

    # Adding real nodes
    G.add_nodes_from(list(H.nodes))

    # Adding links (edges composed by two nodes only, for which we don't use phantom nodes)
    d = 1
    for i, j in H.edges.filterby("order", d).members():
        G.add_edge(i, j, weight=d)

    # Adding phantom nodes and connections therein
    # I will start from the first int node-label available
    try:
        phantom_node_id = max([n for n in H.nodes if isinstance(n, int)]) + 1
    except ValueError:
        # The list of node-labels has no integers, so I start from 0
        phantom_node_id = 0

    # Looping over the hyperedges of different order (from triples up)
    for d in range(2, max_edge_order(H) + 1):
        # Hyperedges of order d (d=2: triplets, etc.)
        for he_id, members in H.edges.filterby("order", d).members(dtype=dict).items():
            # Adding one phantom node for each hyperedge and linking it to the nodes of the hyperedge
            for n in members:
                G.add_edge(phantom_node_id, n, weight=d)
            phantom_node_id += 1

    # Creating a dictionary for the position of the nodes with the standard spring layout
    pos_with_phantom_nodes = nx.spring_layout(G, weight="weight", seed=seed)

    # Retaining only the positions of the real nodes
    pos = {k: pos_with_phantom_nodes[k] for k in list(H.nodes)}

    if return_phantom_graph:
        return pos, G
    else:
        return pos
