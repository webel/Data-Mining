import gzip
import random


def reservoir_sampling(se):
    file = gzip.open("youtube.ungraph.txt.gz", "rb")
    #file = open("toy_graph.txt", "r")
    # init the reservoir array
    edge_res = [None] * se

    # fill the reservoir array
    for i in range(se):
        contents = file.readline()
        from_node = contents[0]
        to_node = contents[3]
        edge = (from_node, to_node)
        edge_res[i] = edge

    n = se
    while True:
        contents = file.readline()
        if not contents:
            break
        from_node = contents[0]
        to_node = contents[3]
        edge = (from_node, to_node)
        k = random.random()
        #print("random number: " + str(k))
        #print(str(se) + "over" + str(n) + " = " + str(se / n))
        if k < (se / n):
            # save this edge
            # print("save edge: " + str(edge))
            j = random.randint(0, se - 1)
            edge_res[j] = edge
        else:
            #print("dont save edge")
            pass

        n += 1
    file.close()
    return edge_res


edge_reservoir = reservoir_sampling(100)
print(edge_reservoir)
