import gzip
from reservoir_sampling import *

class wedgeSampling:
    edge_res: list
    wedge_res: list
    tot_wedges: int
    new_wedges: list
    isClosed: list
    t: int

    def __init__(self, se, sw):
        self.file = gzip.open("youtube.ungraph.txt.gz", "rb")
        self.edge_res = [None]*se
        self.wedge_res = []*sw
        self.new_wedges = []
        self.tot_wedges = len(self.wedge_res)  # konstigt
        self.isClosed = [False]*sw
        self.t = 1
        self.se = se
        self.sw = sw


    def streaming_triangles(self, se, sw):
        edge_res = reservoir_sampling(se)
        # generate random wedges from edge_res?
        self.create_wedges()
        for et in edge_res:
            self.update(et)
            self.t+=1


    def update(self, et):
        for i in range(self.sw):
            #if wedge_res[i] is closed by et
            wedge = self.wedge_res[i] # wedge: [start, middle, end]
            if et == (wedge[0], wedge[2]):
                self.isClosed[i]=True
        for i in range(self.se):
            x = random.random()
            if x <= 1/self.t:  # detta är ju reservoir sampling? igen?
                self.edge_res[i] = et
                self.create_wedges()
                N = self.update_new_wedges(et)
        for i in range(self.sw):
            x = random.random()
            if x<=(N/self.tot_wedges):
                j = random.randrange(0, len(self.new_wedges))
                w = self.new_wedges[j]
                self.isClosed[i] = False




    def create_wedges(self):
        "from these edges we generate a random wedge by doing a second level of reservoir sampling. eh, what??"
        # self.wedge_res is updated
        # update self.tot_wedges
        pass


    def update_new_wedges(self, et):
        "all wedges involving et, formed only by wedges in edge_res"
        self.new_wedges=[]
        for wedge in self.wedge_res:
            if et in wedge:
                self.new_wedges.append(wedge)
        N = len(self.new_wedges)

        return N
    
# Make test to check that number of triangles are 8910005
