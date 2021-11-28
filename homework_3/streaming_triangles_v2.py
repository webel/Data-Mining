import collections
import math
import random
from itertools import tee

def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class StreamingTriangles:
    edge_res: list
    """len(s_e) This is the array of reservoir edges and is the subsample of the stream maintained"""
    new_wedges_t: list # NOTE: not used in current implementation!
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
    s_w : int
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

        # Assuming sampling up to s_e is a part of initialisation...
        for i in range(s_e):
            line = open_file.readline()
            edge = self.edge_from_line(line)
            self.edge_res[i] = edge
        print('Initial edge_res', self.edge_res)

        # NOTE: testing by resetting after initing edge_res...
        # which doesn't seem to work either as all edge_res 
        # are the same in update 

        # Init the number of lines we've read
        self.t = i+1 # 0
        # We set the pointer to the top of the file
        #open_file.seek(0)
        # NOTE: From these edges, we generate a random wedge by doing a second level of reservoir sampling.
        # This process implicitly treats the wedges created in the edge reservoir as a stream,
        # and performs reservoir sampling on that. Overall, this method approxi- mates uniform
        # random wedge sampling... <- Not really what we're doing, but we are creating wedges.
        self.wedge_res = self.sample_wedges()
        print('Initial wedge_res', self.wedge_res)

        # For each edge e_t in stream call update
        while True:
            line = open_file.readline()
            if not line:
                break
            edge = self.edge_from_line(line)
            self.t += 1
            self.update(edge)
            # Let p be the fraction of entries in isClosed set to true
            p = sum(self.is_closed)/len(self.is_closed)
            print(self.wedge_res)
            print(self.is_closed)
            # set k_t = 3p
            k_t = 3*p
            # k_t is the transitivity at t
            print(f"k_{self.t}: {k_t}")
            # set T_t = [pt^2/s_e(s_e-1)] x tot_wedges
            T_t = p**2/(self.s_e*(self.s_e-1)) * self.tot_wedges
            # T_t is the number of triangles at t
            print(f"T_{self.t}: {T_t} \n")


    def sample_wedges(self):
        """Sample wedges from our current self.edge_res

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
        edge_mapping = collections.defaultdict(list)
        for edge in self.edge_res:
            edge_mapping[edge[0]].append(edge[1])
            edge_mapping[edge[1]].append(edge[0])
        candidates = list(
            filter(lambda vertice: len(edge_mapping[vertice]) >= 2, list(edge_mapping))
        )
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
                other_vertices.insert(1, vertice)
                samples.append(tuple(other_vertices))
        self.tot_wedges = len(samples)
        assert self.tot_wedges != 0, print("Total wedges shouldn't be zero", edge_mapping)

        # Sampling should suffice with this random int method seeing as it picks 
        # an int uniformally...
        if self.tot_wedges > self.s_w:
            truncated_samples = []
            indices = set()
            while len(indices) < self.s_w:
                index = random.randint(0, self.s_w)
                indices.add(index)
            for index in indices:
                truncated_samples.append(samples[index])
            assert len(truncated_samples) == self.s_w, "Should pick s_w of wedges"
            return truncated_samples

        return samples        


    @staticmethod
    def edge_from_line(line):
        """Get an edge in the form of a tuple from a line
        Assumes verticies are \t delimited
        """
        return (line[0], line[3])

    def update(self, e_t):
        # Steps 1-3 determines all the wedges in the wedge reservoir that are closed by e_t
        # and updates is_closed accordingly.
        # Steps 4-7 we perform reservoir sampling on edge_res. This involved replacing each entry by
        # e_t with probability 1/t, remaining steps are executed iff this leads to any changes in edge_res
        # We perform some updates to tot wedges and determine the new wedges Nt (new_wedges_t).
        # Finally, in Steps 11-16, we perform reservoir sampling on wedge res, where each entry is
        # randomly replaced with some wedge in Nt. Note that we may remove wedges that have already closed.
        for i in range(self.s_w):
            # if wedge_res[i] is closed by e_t, Steps 1-3.
            wedge = self.wedge_res[i] # wedge: [start, middle, end]
            if e_t == (wedge[0], wedge[2]):
                self.isClosed[i]=True

        edge_res_was_updated = False
        # Perform reservoir sampling, steps 4-7
        for i in range(self.s_e):
            #import ipdb; ipdb.set_trace()
            x = random.random()
            if x <= 1/self.t:
                edge_res_was_updated = True
                # TODO: I don't get this, could become
                # self.edge_res = [same, same, same...] if <= 1/self.t is
                # high as in the beginning if we reset file and t = 0
                self.edge_res[i] = e_t
                print('Updated edge_res!', self.edge_res)
        # Remaining steps
        if(edge_res_was_updated):
            self.wedge_res
            samples = self.sample_wedges()
            new_wedges = list(filter(lambda wedge: wedge not in self.wedge_res, samples))
            len_new_wedges = len(new_wedges)
            # If no new wedges?
            if not len_new_wedges:
                return
            for i in range(self.s_w):
                x = random.random()
                if x <= len_new_wedges/self.tot_wedges:
                    w_index = random.randint(0, len_new_wedges-1)
                    self.wedge_res[i] = new_wedges[w_index]
                    self.is_closed[i] = False


StreamingTriangles(3, 2, open("toy_graph.txt", "r"))
