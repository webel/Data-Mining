import random

import numpy as np
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, IntegerType
from tqdm import tqdm

"""
Implementation of the paper:
'A space efficient streaming algorithm for estimating transitivity and
triangle counts using the birthday paradox'
"""


def get_sorted_tuple_from_row(row):
    row_list = list(map(int, row.split()))
    return sorted(row_list)


def get_data_frame_with_rows_as_tuples(data_frame):
    row_to_tuple_udf = udf(lambda row: get_sorted_tuple_from_row(row),
                           ArrayType(IntegerType()))
    return data_frame.select(row_to_tuple_udf(data_frame[0]).alias('edge'))


def get_data_frame(spark_session, input_file_name):
    data_frame = spark_session.read.csv(input_file_name)
    return get_data_frame_with_rows_as_tuples(data_frame)


def is_closed_by(wedge, edge):
    """ Check if a wedge is closed by an edge.

    :param wedge : A wedge on the form (a,b,c), a < c.
    :param edge  : A sorted edge on the form [u,v].
    :return      : True if the wedge is closed by the edge, otherwise False.
    """
    if (edge[0] == wedge[0] and edge[1] == wedge[2]):
        return True

    return False


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
            if edge1[i] == edge2[j]:
                t = sorted((edge1[1-i], edge2[1-j]))
                return True, (t[0], edge1[i], t[1])

    return False, None


def get_new_wedges(edge_t, edge_res):
    """ Get the new wedges formed by edge_t and all edges in edge_res.

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

    return len(tot_wedges)


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

    edge_res_len= len(edge_res)
    wedge_res_len = len(wedge_res)

    for i in range(wedge_res_len):
        if wedge_res[i] is not None and is_closed_by(wedge_res[i], edge_t):
            is_closed[i] = True

    random_numbers_1 = np.random.uniform(0, 1, edge_res_len)
    is_edge_res_updated = False

    for i in range(edge_res_len):
        if random_numbers_1[i] <= 1.0 / t:
            edge_res[i] = edge_t
            is_edge_res_updated = True

    if is_edge_res_updated:
        tot_wedges = get_tot_wedges(edge_res)
        new_wedges = get_new_wedges(edge_t, edge_res)

        random_numbers_2 = np.random.uniform(0, 1, edge_res_len)

        for i in range(wedge_res_len):

            # @TODO Don't know if 10e-5 in the denominator should be necessary
            if random_numbers_2[i] <= len(new_wedges) / (tot_wedges + 10e-5):
                random_idx = np.random.choice(len(new_wedges))
                wedge_res[i] = new_wedges[random_idx]
                is_closed[i] = False

    return tot_wedges


def get_fraction_of_closed_triangles(is_closed):
    return np.sum(is_closed) / is_closed.shape[0]


# Hyperparameters.
edge_res_len = 200
wedge_res_len = 200

sc = SparkContext()
ss = SparkSession(sc)

#input_file_name = "facebook_combined.txt"
#input_file_name = "wiki-Vote.txt"
input_file_name = "ca-CondMat.txt"
#input_file_name = "0.edges"

edges = get_data_frame(ss, input_file_name).rdd.collect()

def main_algorithm():

    edge_res = [None] * edge_res_len
    wedge_res = [None] * wedge_res_len
    is_closed = np.zeros(wedge_res_len, dtype=np.bool)

    tot_wedges = 0
    tau_t = 0
    kappa_t = 0

    # Algorithm 1 (p. 6)
    for i in enumerate(tqdm(edges), 1):
        t, e = i
        tot_wedges = update(e[0], t, edge_res, wedge_res, is_closed, tot_wedges)
        rho = get_fraction_of_closed_triangles(is_closed)
        kappa_t = 3 * rho
        tau_t = ((rho * t ** 2) / (edge_res_len * (edge_res_len - 1))) * tot_wedges

    print("kappa: " + str(kappa_t) + " and tau = " + str(tau_t))

    return kappa_t, tau_t

n_iter = 5
kappa_list = np.zeros(n_iter)
tau_list = np.zeros(n_iter)

for i in range(n_iter):
    kappa_list[i], tau_list[i] = main_algorithm()

print(np.mean(kappa_list), np.std(kappa_list))
print(np.mean(tau_list), np.std(tau_list))


