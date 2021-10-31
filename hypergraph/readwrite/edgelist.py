import csv
import hypergraph as hg
from hypergraph.exception import HypergraphError
from ast import literal_eval

__all__ = [
    "read_edgelist",
    "write_edgelist",
    "read_weighted_edgelist",
    "write_weighted_edgelist",
]


def generate_edgelist(H, delimiter=" ", data=True):
    """
    A helper function to generate a hyperedge list from a Hypergraph object.

    Parameters
    ----------
    H: Hypergraph object
        The hypergraph of interest
    delimiter: char, default: space (" ")
        Specifies the delimiter between hyperedge members
    data: bool, default: True
        Specifies whether to output the edge attributes

    Returns
    -------
    A iterator of strings
    """
    if data is True:
        for id in H.edges:
            e = *H.edges[id], dict(H._edge_attr[id])
            yield delimiter.join(map(str, e))
    elif data is False:
        for id in H.edges:
            e = H.edges[id]
            yield delimiter.join(map(str, e))
    else:
        for id in H.edges:
            e = H.edges[id]
            try:
                e.extend([H._edge_attr[id][k] for k in data])
            except KeyError:
                pass  # missing data for this edge, should warn?
            yield delimiter.join(map(str, e))


def write_edgelist(H, path, delimiter=" ", data=False, encoding="utf-8"):
    """
    A function to output a file containing a hyperedge list from a Hypergraph object.

    Parameters
    ----------
    H: Hypergraph object
        The hypergraph of interest
    path: string
        The path of the file to write to
    delimiter: char, default: space (" ")
        Specifies the delimiter between hyperedge members
    data: bool, default: True
        Specifies whether to output the edge attributes
    encoding: string, default: "utf-8"
        Encoding of the file

    Returns
    -------
    A file containing a hyperedge list

    Example
    -------

        >>> import hypergraph as hg
        >>> n = 1000
        >>> m = n
        >>> p = 0.01
        >>> H = hg.erdos_renyi_hypergraph(n, m, p)
        >>> hg.write_edgelist(H, "test.csv", delimiter=",")
    """
    with open(path, "wb") as file:
        for line in generate_edgelist(H, delimiter, data):
            line += "\n"
            file.write(line.encode(encoding))


def write_weighted_edgelist(H, path, delimiter=" ", encoding="utf-8"):
    """
    A function to output a file containing a weighted hyperedge list from a
    Hypergraph object using the "weight" attribute.

    Parameters
    ----------
    H: Hypergraph object
        The hypergraph of interest
    path: string
        The path of the file to write to
    delimiter: char, default: space (" ")
        Specifies the delimiter between hyperedge members
    encoding: string, default: "utf-8"
        Encoding of the file

    Returns
    -------
    A file containing a hyperedge list

    Example
    -------
        >>> import hypergraph as hg
        >>> n = 1000
        >>> m = n
        >>> p = 0.01
        >>> H = hg.erdos_renyi_hypergraph(n, m, p)
        >>> hg.write_weighted_edgelist(H, "test.csv", delimiter=",")
    """
    write_edgelist(H, path, delimiter=delimiter, data=("weight",), encoding=encoding)


def read_edgelist(
    path,
    comments="#",
    delimiter=None,
    create_using=None,
    nodetype=None,
    data=False,
    encoding="utf-8",
):
    """
    A function to read a file containing a hyperedge list and
    convert it to a Hypergraph object.

    Parameters
    ----------
    path: string
        The path of the file to read from
    comments: string, default: "#"
        The token that denotes comments in the file
    delimiter: char, default: space (" ")
        Specifies the delimiter between hyperedge members
    create_using:
    nodetype: type
        type that the node labels will be cast to
    data: bool, default: False
        Specifies whether there is a dictionary of data at the end of the line.
    encoding: string, default: "utf-8"
        Encoding of the file

    Returns
    -------
    A Hypergraph object

    Example
    -------
        >>> import hypergraph as hg
        >>> H = hg.read_edgelist("test.csv", delimiter=",")
    """
    with open(path, "rb") as file:
        lines = (
            line if isinstance(line, str) else line.decode(encoding) for line in file
        )
        return parse_edgelist(
            lines,
            comments=comments,
            delimiter=delimiter,
            create_using=create_using,
            nodetype=nodetype,
            data=data,
        )


def read_weighted_edgelist(
    path,
    comments="#",
    delimiter=None,
    create_using=None,
    nodetype=None,
    encoding="utf-8",
):
    """
    A function to read a file containing a weighted hyperedge list and
    convert it to a Hypergraph object using the "weight" attribute.

    Parameters
    ----------
    path: string
        The path of the file to read from
    comments: string, default: "#"
        The token that denotes comments in the file
    delimiter: char, default: space (" ")
        Specifies the delimiter between hyperedge members
    create_using:
    nodetype: type
        type that the node labels will be cast to
    encoding: string, default: "utf-8"
        Encoding of the file

    Returns
    -------
    A Hypergraph object

    Example
    -------
        >>> import hypergraph as hg
        >>> H = hg.read_weighted_edgelist("test.csv", delimiter=",")
    """
    return read_edgelist(
        path,
        comments=comments,
        delimiter=delimiter,
        create_using=create_using,
        nodetype=nodetype,
        data=(("weight", float),),
        encoding=encoding,
    )


def parse_edgelist(
    lines, comments="#", delimiter=None, create_using=None, nodetype=None, data=False
):
    """
    A helper function to read a iterable of strings containing a hyperedge list and
    convert it to a Hypergraph object.

    Parameters
    ----------
    lines: iterable of strings
        Lines where each line is an edge
    comments: string, default: "#"
        The token that denotes comments to ignore
    delimiter: char, default: space (" ")
        Specifies the delimiter between hyperedge members
    create_using:
    nodetype: type
        type that the node labels will be cast to
    data: bool, default: False
        Specifies whether there is a dictionary of data at the end of the line.

    Returns
    -------
    A Hypergraph object
    """
    H = hg.empty_hypergraph(create_using)
    for line in lines:
        if comments is not None:
            p = line.find(comments)
            if p >= 0:
                line = line[:p]
            if not line:
                continue
        s = line.strip().split(delimiter)

        if data is False:
            # no data or data type specified
            edge = s
            edgedata = {}
        elif data is True:
            edge = s[:-1]
            d = s[-1]
            # no edge types specified
            try:  # try to evaluate as dictionary
                if delimiter == ",":
                    edgedata_str = ",".join(d)
                else:
                    edgedata_str = " ".join(d)
                edgedata = dict(literal_eval(edgedata_str.strip()))
            except Exception as e:
                raise TypeError(
                    f"Failed to convert edge data ({d}) to dictionary."
                ) from e
        else:
            try:
                d = s[-len(data) :]
                edge = s[: -len(data)]
            except:
                raise HypergraphError("Too many data columns specified.")
            edgedata = {}
            for (edge_key, edge_type), edge_value in zip(data, d):
                try:
                    edge_value = edge_type(edge_value)
                except Exception as e:
                    raise TypeError(
                        f"Failed to convert {edge_key} data {edge_value} "
                        f"to type {edge_type}."
                    ) from e
                edgedata.update({edge_key: edge_value})

        if nodetype is not None:
            try:
                edge = [nodetype(node) for node in edge]
            except Exception as e:
                raise TypeError(f"Failed to convert nodes to type {nodetype}.") from e

        H.add_edge(edge, **edgedata)
    return H
