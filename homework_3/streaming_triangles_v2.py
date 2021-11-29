import collections
from dataclasses import dataclass
import math
import random
from itertools import tee
import gzip


def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@dataclass
class Edge:
    left: int
    right: int

    @staticmethod
    def from_line(line):
        return Edge(line[0], line[3])


@dataclass
class Wedge:
    left: int
    middle: int
    right: int

    @staticmethod
    def from_edges(x, y):
        if x == y:
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
        return False


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


def get_wedge(edge1, edge2):
    """Check if two edges forms a wedge, and if so returns the wedge.

    :param edge1    : An edge on the form [u,v].
    :param edge2    : An edge on the form [u,v].
    :return         : (True, wedge) if the edges form a wedge, otherwise (False, None).
                        wedge is given on the form (a,b,c), where a < c
    """

    if edge1 == edge2:
        return False, None

    for i in range(2):
        for j in range(2):
            if edge1[i] == edge2[j]:
                t = sorted((edge1[1 - i], edge2[1 - j]))
                return True, (t[0], edge1[i], t[1])

    return False, None


def get_tot_wedges(edge_res):
    """Get the total number of wedges formed by the edges in edge_res.

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

    return len(tot_wedges)


def get_new_wedges(edge_t, edge_res):
    """Get the new wedges formed by edge_t and all edges in edge_res.

    :param edge_t:
    :param edge_res:
    :return: A list of wedges
    """
    new_wedges = []

    for edge in edge_res:
        if edge is not None:
            is_wedge, wedge = get_wedge(edge, edge_t)
            if is_wedge:
                new_wedges.append(wedge)

    return new_wedges


class StreamingTriangles:
    edge_res: list
    """len(s_e) This is the array of reservoir edges and is the subsample of the stream maintained"""
    new_wedges_t: list  # NOTE: not used in current implementation!
    """This is a list of all wedges involving e_t formed only by edges in edge_res. 
    This may often be empty, if e_t is not added to the edge_res. 
    We do not necessarily maintain this list explicitly, 
    and we discuss implementation details later."""
    tot_wedges: int
    """This is the total number of wedges formed by edges in the current edge_res"""
    wedge_res: list
    """This is an array of reservoir wedges of size s_w"""
    is_closed: list
    """This is a boolean array. We set isClosed[i] to be true if wedge 
    wedge_res[i] is detected as closed"""
    s_e: int
    """Length of edge reservour"""
    s_w: int
    """Length of wedge reservour"""
    t: int
    """The time, i.e. e_t"""

    def __init__(self, s_e, s_w, open_file):
        self.s_e = s_e
        self.s_w = s_w

        # Initialize edge_res of size s_e and wedge_res of size s_w.
        self.edge_res = [None] * s_e
        self.wedge_res = [None] * s_w
        self.is_closed = [False] * s_w

        # Init the current number of total wedges
        self.tot_wedges = 0
        # Init the current t
        self.t = 1

        # For each edge e_t in stream call update
        # for i in range(1000):
        while True:
            line = open_file.readline()
            if not line or line == b"\n":
                break
            if line.startswith(b"#"):
                continue
            edge = self.edge_from_line(line)
            # if not edge:
            #     continue
            self.update(edge)
            self.t += 1
            # if self.t % 10000 == 0:
            #     self.__print_stats()
        self.__print_stats()

    def __print_stats(self):
        # Let p be the fraction of entries in isClosed set to true
        # import ipdb; ipdb.set_trace()
        p = sum(self.is_closed) / len(self.is_closed)
        print(p)
        # set k_t = 3p
        k_t = 3 * p
        # k_t is the transitivity at t
        print(f"k_{self.t}: {k_t}")
        # set T_t = [pt^2/s_e(s_e-1)] x tot_wedges
        T_t = ((p * self.t ** 2) / (self.s_e * (self.s_e - 1))) * self.tot_wedges
        tau_t = ((p * self.t ** 2) / (self.s_e * (self.s_e - 1))) * self.tot_wedges
        # T_t is the number of triangles at t
        print(f"T_{self.t}: {T_t} \n")

    def get_wedges(self):
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
        """
        edge_mapping = collections.defaultdict(set)
        for edge in self.edge_res:
            edge_mapping[edge[0]].add(edge[1])
            edge_mapping[edge[1]].add(edge[0])
        candidates = list(
            filter(lambda vertice: len(edge_mapping[vertice]) >= 2, list(edge_mapping))
        )
        wedges = []
        for vertice in candidates:
            other_vertices = edge_mapping[vertice]
            # Insert our vertice inbetween the other two to create a wedge
            if len(other_vertices) > 2:
                # Although, if we connect to more than 2 other vertices
                # create all the paths exhaustively
                for pair in pairwise(other_vertices):
                    pair = sorted(list(pair))
                    pair.insert(1, vertice)
                    wedges.append(tuple(pair))
            else:
                other_vertices = sorted(list(other_vertices))
                other_vertices.insert(1, vertice)
                wedges.append(tuple(other_vertices))
        #self.tot_wedges = len(wedges)
        return wedges

    @staticmethod
    def edge_from_line(line):
        """Get an edge in the form of a tuple from a line
        Assumes verticies are \t delimited
        """
        decoded = sorted(line.decode().strip().split("\t"))
        edge = (int(decoded[0]), int(decoded[1]))
        return edge

    def update(self, e_t):
        # Steps 1-3 determines all the wedges in the wedge reservoir that are closed by e_t
        # and updates is_closed accordingly.
        for i in range(self.s_w):
            if self.wedge_res[i] and e_t == (
                self.wedge_res[i][0],
                self.wedge_res[i][2],
            ):
                self.is_closed[i] = True

        # if self.t % 100000 == 0:
        #     print(self.wedge_res)

        # Steps 4-7 we perform reservoir sampling on edge_res. This involved replacing each entry by
        # e_t with probability 1/t, remaining steps are executed iff this leads to any changes in edge_res
        edge_res_was_updated = False

        for i in range(self.s_e):
            x = random.random()
            if x <= 1 / self.t:
                edge_res_was_updated = True
                self.edge_res[i] = e_t
                # print("Updated edge_res!", self.edge_res)

        # We perform some updates to tot wedges and determine the new wedges Nt (new_wedges_t).
        # Finally, in Steps 11-16, we perform reservoir sampling on wedge res, where each entry is
        # randomly replaced with some wedge in Nt. Note that we may remove wedges that have already closed.
        if edge_res_was_updated:
            # self.wedge_res
            all_wedges = get_tot_wedges(self.edge_res)
            #all_wedges = self.get_wedges()
            new_wedges = get_new_wedges(e_t, self.edge_res)
            # new_wedges = list(
            #     filter(lambda wedge: wedge not in self.wedge_res, all_wedges)
            # )
            #new_wedges = get_new_wedges(e_t, self.edge_res)
            self.tot_wedges = all_wedges

            # samples = self.sample_wedges()
            # new_wedges = list(
            #     filter(lambda wedge: wedge not in self.wedge_res, samples)
            # )
            # len_new_wedges = len(new_wedges)
            # If no new wedges?
            for i in range(self.s_w):
                if not len(new_wedges):
                    return
                x = random.random()
                if x <= len(new_wedges) / self.tot_wedges:
                    w_index = random.randint(0, len(new_wedges) - 1)
                    self.wedge_res[i] = new_wedges[w_index]
                    self.is_closed[i] = False


# StreamingTriangles(4, 3, open("toy_graph.txt", "r"))
# for i in range(10):
#     StreamingTriangles(200, 200, gzip.open("ca-AstroPh.txt.gz", "rb"))

StreamingTriangles(450, 450, gzip.open("ca-AstroPh.txt.gz", "rb"))


# for i in [100, 200, 300, 400]:
#     StreamingTriangles(i, i, gzip.open("ca-AstroPh.txt.gz", "rb"))

# for i in [500, 600, 700]:
#     StreamingTriangles(i, i, gzip.open("ca-AstroPh.txt.gz", "rb"))


# CondMat
# Average clustering coefficient	0.6334
# Number of triangles	173361

# Astro
# Average clustering coefficient	0.6306
# Number of triangles	1 351 441

# 1 380 156.7405113066
# 4 251 647.682809698

# 5 062 318
