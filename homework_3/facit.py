import numpy as np
from tqdm import tqdm

"""
Implementation of the paper:
'A space efficient streaming algorithm for estimating transitivity and
triangle counts using the birthday paradox'
"""


def get_sorted_tuple_from_row(row):
    row_list = list(map(int, row.split()))
    return tuple(sorted(row_list))


def is_closed_by(wedge, edge):
    """ Check if a wedge is closed by an edge.

    :param wedge : A wedge on the form (a,b,c), a < c.
    :param edge  : A sorted edge on the form [u,v].
    :return      : True if the wedge is closed by the edge, otherwise False.
    """
    if (edge[0] == wedge[0] and edge[1] == wedge[2]) or (edge[0] == wedge[2] and edge[1] == wedge[0]):
        return True

    return False


def is_wedge(edge1, edge2):
    """
    Check if edge1 and edge2 form a wedge.
    :param edge1:
    :param edge2:
    :return:
    """
    if edge1 != edge2:
        for i in range(2):
            for j in range(2):
                if edge1[i] == edge2[j]:
                    return True
    return False


def get_wedge(edge1, edge2):
    """ Check if two edges forms a wedge, and if so returns the wedge.

    :param edge1    : An edge on the form [u,v].
    :param edge2    : An edge on the form [u,v].
    :return         : Returns a wedge if the edges form a wedge, otherwise None. The wedge is given on the form (a,b,c), where a < c
    """
    if is_wedge(edge1, edge2):
        nodes = edge1 + edge2
        connecting_node = -1
        leaf_nodes = []
        for n in nodes:
            if nodes.count(n) > 1:
                connecting_node = n
            else:
                leaf_nodes.append(n)

        leaf_nodes.sort()

        return tuple([leaf_nodes.pop(), connecting_node, leaf_nodes.pop()])
    return None


def get_nof_deleted_wedges_for_edge(edge, deleted_edges):
    """
    Get the number of wedges formed by the edge and the edges in deleted_edges.
    :param edge:
    :param deleted_edges:
    :return: A number of deleted wedges.
    """
    nof_deleted_wedges = 0
    for edge_i in deleted_edges:
        if is_wedge(edge, edge_i):
            nof_deleted_wedges += 1

    return nof_deleted_wedges


def get_new_wedges_and_diff(edge_t, deleted_edges, edge_res):
    """
    Get new wedges and the diff in total wedges after additions and deletions.
    :param edge_t:
    :param deleted_edges:
    :param edge_res:
    :return: A list of new wedges and the difference in total wedges as an integer.
    """
    tot_wedges_diff = 0
    seen = set()
    seen.add(edge_t)
    new_wedges = []
    for edge_i in edge_res:
        if edge_i is not None and edge_i not in seen:
            seen.add(edge_i)

            tot_wedges_diff -= get_nof_deleted_wedges_for_edge(edge_i, deleted_edges)

            wedge = get_wedge(edge_i, edge_t)

            if wedge is not None:
                new_wedges.append(wedge)

    tot_wedges_diff += len(new_wedges)
    return new_wedges, tot_wedges_diff


def get_deleted_edges(edge_res, possibly_deleted_edges):
    for i in range(edge_res_len):
        if edge_res[i] in possibly_deleted_edges:
            possibly_deleted_edges.remove(edge_res[i])
    return possibly_deleted_edges


def update(edge_t, t, edge_res, wedge_res, is_closed, tot_wedges):
    """ One step of update. Algorithm 2 (p. 7)

    :param edge_t     : Edge observed at time t.
    :param t          : Time t.
    :edge_res         : Reservoir of edges.
    :param wedge_res  : Reservoir of wedges.
    :param is_closed  : is_closed[i] = True iff wedge_res[i] is closed.
    :param tot_wedges : Total number of wedges.
    :return           : Total number of wedges after update.
    """

    edge_res_len = len(edge_res)
    wedge_res_len = len(wedge_res)

    for i in range(wedge_res_len):
        if wedge_res[i] is not None and is_closed_by(wedge_res[i], edge_t):
            is_closed[i] = True

    random_numbers_1 = np.random.uniform(0, 1, edge_res_len)
    is_edge_res_updated = False

    possibly_deleted_edges = set()
    for i in range(edge_res_len):
        if random_numbers_1[i] <= 1.0 / t:
            if edge_res[i] is not None:
                possibly_deleted_edges.add(edge_res[i])
            edge_res[i] = edge_t
            is_edge_res_updated = True

    deleted_edges = get_deleted_edges(edge_res, possibly_deleted_edges)

    if is_edge_res_updated:
        new_wedges, tot_wedges_diff = get_new_wedges_and_diff(edge_t, deleted_edges, edge_res)
        tot_wedges += tot_wedges_diff
        random_numbers_2 = np.random.uniform(0, 1, edge_res_len)

        for i in range(wedge_res_len):
            if random_numbers_2[i] <= len(new_wedges) / (tot_wedges + 10e-5):
                random_idx = np.random.choice(len(new_wedges))
                wedge_res[i] = new_wedges[random_idx]
                is_closed[i] = False

    return tot_wedges


def get_fraction_of_closed_triangles(is_closed):
    return np.sum(is_closed) / is_closed.shape[0]


def streaming_triangles(edge_res_len, wedge_res_len):
    """
    Main algorithm.

    :param edge_res_len:
    :param wedge_res_len:
    :return:
    """
    edge_res = [None] * edge_res_len
    wedge_res = [None] * wedge_res_len
    is_closed = np.zeros(wedge_res_len, dtype=np.bool)

    tot_wedges = 0
    tau_t = 0
    kappa_t = 0

    t = 1
    with open(input_file_name, "r", encoding="utf-8") as edges_file:
        for row in tqdm(edges_file):

            edge_t = get_sorted_tuple_from_row(row)

            tot_wedges = update(edge_t, t, edge_res, wedge_res, is_closed, tot_wedges)
            rho = get_fraction_of_closed_triangles(is_closed)
            kappa_t = 3 * rho
            tau_t = ((rho * t ** 2) / (edge_res_len * (edge_res_len - 1))) * tot_wedges
            t += 1

    return kappa_t, tau_t

# Hyperparameters.
edge_res_len = 500
wedge_res_len = 500

#input_file_name = "facebook_combined.txt"
#input_file_name = "ca-CondMat.txt"
input_file_name = "wiki-Vote.txt"

n_iter = 5
kappa_list = np.zeros(n_iter)
tau_list = np.zeros(n_iter)

for i in range(n_iter):
    kappa_list[i], tau_list[i] = streaming_triangles(edge_res_len, wedge_res_len)

print(np.mean(kappa_list), np.std(kappa_list))
print(np.mean(tau_list), np.std(tau_list))

