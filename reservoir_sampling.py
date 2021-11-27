import gzip
import random


def reservoir_sampling(se):
    file = gzip.open("web-NotreDame.txt.gz", "rb")
    edge_res = [None]*se

    for i in range(4):
        contents=file.readline()
        print(contents)

    for i in range(se):
        contents=file.readline()
        #contents=str(contents).replace("b'", "").replace("r", "").replace("n'", "")
        #content = contents.replace("/", "").strip()
        #print(content)
        #from_node, to_node = contents.split('/')
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
        #print(str(se)+"over"+str(n)+" = " + str(se/n))
        if k < (se/n):
            # save this edge
            #print("save edge: " + str(edge))
            j = random.randint(0, se-1)
            edge_res[j] = edge
        else:
            print("dont save edge")

        n+=1
    file.close()
    return edge_res


edge_reservoir = reservoir_sampling(100)
print(edge_reservoir)
