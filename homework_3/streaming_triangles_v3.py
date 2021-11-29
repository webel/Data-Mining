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


@dataclass
class Edge:
    left: int
    right: int

    @staticmethod
    def from_line(line):
        decoded = sorted(line.decode().strip().split("\t"))
        edge = (int(decoded[0]), int(decoded[1]))
        return Edge(edge[0], edge[1])

    def as_tuple(self):
        return (self.left, self.right)


@dataclass
class Wedge:
    left: int
    middle: int
    right: int

    @staticmethod
    def from_edges(x, y):
        if len(set(flatten([x.as_tuple(), y.as_tuple()]))) != 3:
            # Short circuit by checking if the set of our edges isn't 3,
            # i.e. the set is 2, x == y, or 4 -> they have nothing in common
            return False
        if x.left == y.left:
            return Wedge(x.right, x.left, y.right)
        if x.right == y.right:
            return Wedge(y.left, y.right, x.left)
        if x.left == y.right:
            return Wedge(y.left, x.left, x.right)
        if y.left == x.right:
            return Wedge(x.left, x.right, y.right)
        return False

    def closed_by(self, z):
        if self.left == z.left and self.right == z.right:
            return True
        # NOTE: shouldn't need to check other way as both are sorted... but will do
        if self.left == z.right and self.right == z.left:
            return True
        return False

    def __hash__(self):
        return hash((self.left, self.middle, self.right))


def get_wedges(edge_res):
    """Get all wedges from our current self.edge_res

    NOTE: when testing, this verboseness served faster than
    iterating over edge_res in two loops.

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
        edge_mapping[edge.left].add(edge.right)
        edge_mapping[edge.right].add(edge.left)
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
                wedges.add(Wedge(*pair))
        else:
            other_vertices = sorted(list(other_vertices))
            other_vertices.insert(1, vertice)
            wedges.add(Wedge(*other_vertices))
    return len(wedges)


def get_new_wedges(edge_t, edge_res):
    """Get the new wedges formed by edge_t and all edges in edge_res."""
    new_wedges = []

    for edge in edge_res:
        wedge = Wedge.from_edges(edge, edge_t)
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
        edge = Edge.from_line(line)
        tot_wedges = update(
            edge, t, s_e, s_w, edge_res, wedge_res, tot_wedges, is_closed
        )
        t += 1

        if t % 1000 == 0:
            __print_stats(is_closed, s_e, t, tot_wedges)

    __print_stats(is_closed, s_e, t, tot_wedges)


def update(
    edge: Edge,
    t: int,
    s_e: int,
    s_w: int,
    edge_res: list[Edge],
    wedge_res: list[Wedge],
    tot_wedges: int,
    is_closed: list[bool],
):
    """The update stage of the algorithm, the "steps" comments are directly taken from the paper"""

    # Steps 1-3 determines all the wedges in the wedge reservoir that are closed by e_t
    # and updates is_closed accordingly.
    for i in range(s_w):
        if wedge_res[i] and wedge_res[i].closed_by(edge):
            is_closed[i] = True

    # Steps 4-7 we perform reservoir sampling on edge_res. This involved replacing each entry by
    # e_t with probability 1/t, remaining steps are executed iff this leads to any changes in edge_res
    updated = False
    for i in range(s_e):
        x = random.random()
        if x <= 1 / t:
            updated = True
            edge_res[i] = edge

    # We perform some updates to tot_wedges and determine the new wedges Nt (new_wedges_t).
    # Finally, in Steps 11-16, we perform reservoir sampling on wedge_res, where each entry is
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


def tests():
    assert Wedge.from_edges(Edge(3, 4), Edge(3, 5)).closed_by(
        Edge(4, 5)
    ), "(3,4) (3,5) should be closed by (4,5)"
    assert Wedge.from_edges(Edge(2, 3), Edge(1, 2)).closed_by(
        Edge(1, 3)
    ), "(2,3) (1,2) should be closed by (1,3)"
    assert Wedge.from_edges(Edge(1, 2), Edge(2, 3)).closed_by(
        Edge(1, 3)
    ), "(1,2) (2,3) should be closed by (1,3)"
    assert Wedge.from_edges(Edge(3, 4), Edge(2, 4)).closed_by(
        Edge(2, 3)
    ), "(3,4) (2,4) should be closed by (2,3)"


if __name__ == "__main__":
    tests()
    main(gzip.open("web-NotreDame.txt.gz", "rb"), 20000, 20000)

## web-NotreDame
# Average clustering coefficient	0.2346
# Number of triangles	8910005
# Fraction of closed triangles	0.03104
