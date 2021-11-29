import collections
from dataclasses import dataclass
import random
from itertools import tee, chain
import gzip


def pairwise(iterable):
    """pairwise('ABCDEFG') --> AB BC CD DE EF FG
    Borrowed directly from python itertools (pairwise was introcued in 3.10
    and we don't want to update python)"""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def flatten(list_of_lists):
    """Flatten one level of nesting
    Borrowed directly from python itertools recipes
    """
    return chain.from_iterable(list_of_lists)


def get_wedges(edge_res):
    """Get all wedges from our current self.edge_res

    First create an edge_mapping, i.e. for each vertice x in
    (x, y) set a dictionary key to x and the value to the list
    of vertices the vertice x has an edge with.

    Example:
    (1, 2), (1, 3), (2, 4)

    Edge mapping:
    {1: [2, 3], 2: [4], 3: [1], 4: [2]}

    Create a candidate list of possible keys from our edge mapping
    filtering on values that are atleast 2.

    Then create all possible wedges given these candidates.
    """
    edge_mapping = collections.defaultdict(set)
    for edge in edge_res:
        edge_mapping[edge[0]].add(edge[1])
        edge_mapping[edge[1]].add(edge[0])
    candidates = list(
        filter(lambda vertice: len(edge_mapping[vertice]) >= 2, list(edge_mapping))
    )
    wedges = set()
    for vertice in candidates:
        other_vertices = sorted(edge_mapping[vertice])
        # Insert our vertice inbetween the other two to create a wedge
        if len(other_vertices) > 2:
            # Although, if we connect to more than 2 other vertices
            # create all the paths exhaustively
            for pair in pairwise(other_vertices):
                pair = list(pair)
                pair.insert(1, vertice)
                wedges.add(tuple(pair))
        else:
            other_vertices.insert(1, vertice)
            wedges.add(tuple(other_vertices))
    return len(wedges)


def get_wedge(edge1, edge2):
    """Check if two edges forms a wedge, return false or a wedge."""

    if edge1 == edge2:
        return False

    for i in range(2):
        for j in range(2):
            if edge1[i] == edge2[j]:
                edges = sorted((edge1[1 - i], edge2[1 - j]))
                return (edges[0], edge1[i], edges[1])

    return False


def get_new_wedges(edge_t, edge_res):
    """Get the new wedges formed by edge_t and all edges in edge_res."""
    new_wedges = []

    for edge in edge_res:
        wedge = get_wedge(edge, edge_t)
        if wedge:
            new_wedges.append(wedge)

    return new_wedges


def __print_stats(is_closed: list[bool], s_e: int, t: int, tot_wedges: int):
    # Let p be the fraction of entries in isClosed set to true
    p = sum(is_closed) / len(is_closed)
    # set k_t = 3p
    k_t = 3 * p
    # k_t is the transitivity at t
    print(f"k_{t}: {k_t}")
    # set T_t = [pt^2/s_e(s_e-1)] x tot_wedges
    T_t = ((p * (t ** 2)) / (s_e * (s_e - 1))) * tot_wedges
    # T_t is the number of triangles at t
    print(f"T_{t}: {T_t} \n")


def main(open_file, s_e: int, s_w: int):
    """The main part of the algorithm which calls update on every edge from the stream"""

    # Initialise our data structures
    edge_res = [None] * s_e
    wedge_res = [None] * s_w
    is_closed = [False] * s_w
    tot_wedges = 0

    # Iterate over every vertice in our file
    t = 1
    while True:
        line = open_file.readline()
        if not line or line == b"\n":
            break
        if line.startswith(b"#"):
            # Don't bother with comments
            continue
        decoded = sorted(line.decode().strip().split("\t"))
        edge = (int(decoded[0]), int(decoded[1]))
        tot_wedges = update(
            edge, t, s_e, s_w, edge_res, wedge_res, tot_wedges, is_closed
        )
        t += 1

        if t % 1000 == 0:
            __print_stats(is_closed, s_e, t, tot_wedges)

    __print_stats(is_closed, s_e, t, tot_wedges)


def update(
    edge: tuple,
    t: int,
    s_e: int,
    s_w: int,
    edge_res: list[tuple],
    wedge_res: list[tuple],
    tot_wedges: int,
    is_closed: list[bool],
):
    """The update stage of the algorithm, the "steps" comments are directly taken from the paper"""

    # Steps 1-3 determines all the wedges in the wedge reservoir that are closed by e_t
    # and updates is_closed accordingly.
    for i in range(s_w):
        if wedge_res[i]:
            is_closed[i] = (
                edge[0] == wedge_res[i][0] and edge[1] == wedge_res[i][2]
            ) or (edge[0] == wedge_res[i][2] and edge[1] == wedge_res[i][0])

    # Steps 4-7 we perform reservoir sampling on edge_res. This involved replacing each entry by
    # e_t with probability 1/t, remaining steps are executed iff this leads to any changes in edge_res
    updated = False
    for i in range(s_e):
        x = random.random()
        if x <= 1 / t:
            updated = True
            edge_res[i] = edge

    # We perform some updates to tot wedges and determine the new wedges Nt (new_wedges_t).
    # Finally, in Steps 11-16, we perform reservoir sampling on wedge res, where each entry is
    # randomly replaced with some wedge in Nt. Note that we may remove wedges that have already closed.
    if updated:
        tot_wedges = get_wedges(edge_res)
        new_wedges = get_new_wedges(edge, edge_res)
        if not new_wedges:
            return tot_wedges
        for i in range(s_w):
            x = random.random()
            if x <= len(new_wedges) / tot_wedges:
                index = random.randint(0, len(new_wedges) - 1)
                wedge_res[i] = new_wedges[index]
                is_closed[i] = False
    return tot_wedges


if __name__ == "__main__":
    main(gzip.open("web-NotreDame.txt.gz", "rb"), 20000, 20000)

## web-NotreDame
# Average clustering coefficient	0.2346
# Number of triangles	8910005
# Fraction of closed triangles	0.03104
