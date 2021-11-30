import collections
#from itertools import pairwise
from itertools import tee


def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def get_wedges(edge_res):
    """Get all wedges from our current self.edge_res

    First create an edge_mapping, i.e. for each vertice x in
    (x, y) set a dictionary key to x and the value to the list
    of vertices the vertice x has an edge with.

    Example:
    (1, 2), (1, 3), (2, 4)

    Edge mapping:
    {1: [2, 3], 2: [4]}

    Create a candidate list of possible keys from our edge mapping
    filtering on values that are atleast 2.
    """
    edge_mapping = collections.defaultdict(set)
    for edge in edge_res:
        edge_mapping[edge[0]].add(edge[1])
        edge_mapping[edge[1]].add(edge[0])
    candidates = list(
        filter(lambda vertice: len(edge_mapping[vertice]) >= 2, list(edge_mapping))
    )
    print(edge_mapping)
    print(candidates)
    samples = []
    for vertice in candidates:
        other_vertices = edge_mapping[vertice]
        # Insert our vertice inbetween the other two to create a wedge
        if len(other_vertices) > 2:
            # Although, if we connect to more than 2 other vertices
            # create all the paths exhaustively
            for pair in pairwise(other_vertices):
                pair = list(pair)
                pair.insert(1, vertice)
                samples.append(tuple(pair))
        else:
            other_vertices = list(other_vertices)
            other_vertices.insert(1, vertice)
            samples.append(tuple(other_vertices))
    print(samples)
    return len(samples)


def get_wedge(edge1, edge2):
    """ Check if two edges forms a wedge, and if so returns the wedge.

    :param edge1    : An edge on the form [u,v].
    :param edge2    : An edge on the form [u,v].
    :return         : (True, wedge) if the edges form a wedge, otherwise (False, None).
                        wedge is given on the form (a,b,c), where a < c
    """

    if edge1 == edge2:
        return False, None

    for i in range(2):
        for j in range(2):
            try:
                if edge1[i] == edge2[j]:
                    t = sorted((edge1[1-i], edge2[1-j]))
                    return True, (t[0], edge1[i], t[1])
            except:
                print('Exception occured')
                print(edge1, edge2)

    return False, None

def get_tot_wedges(edge_res):
    """ Get the total number of wedges formed by the edges in edge_res.

    :param edge_res: A list of edges.
    :return: The total numbers of wedges in edge_res.
    """
    tot_wedges = set()

    for i in range(len(edge_res)):
        if edge_res[i] is None:
            continue
        for j in range(i):
            if edge_res[j] is None:
                continue
            is_wedge, wedge = get_wedge(edge_res[i], edge_res[j])
            if is_wedge:
                tot_wedges.add(wedge)
    print(tot_wedges)
    return len(tot_wedges)


edge_res = [(1,2), (1,3), (2,4), (3,4), (5,6)]
print(get_tot_wedges(edge_res))

print(get_wedges(edge_res))


