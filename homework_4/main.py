import csv
import math
from operator import inv

# As a warm up task, you should first compute the eigenvectors and
# eigenvalues of a set of graphs, and find out how many communities
# do these graphs have.

"""
Implementation of K-eigenvector Algorithm
"""
sigma = 0.4


def column(matrix, i):
    return [row[i] for row in matrix]


def load_matrix_from_csv_file(file_path: str):
    matrix = []
    with open(file_path, "r") as f:
        for line in csv.reader(f):
            matrix.append(list(map(int, line)))
        # yield from csv.reader(f)
    return matrix


def gaussian_kernel(p1, p2):
    return math.exp(-(math.dist(p1, p2) ** 2 / (2 * sigma ** 2)))


def form_affinity_matrix(edge_list: list):
    """Convert edge list to affinity matrix
    Step 1.
    """
    # col1 = column(edge_list, 1)
    # col2 = column(edge_list, 2)
    #
    n = len(edge_list[0])
    A = []
    for i in range(n):
        A.append([0] * n)
        for j in range(n):
            if i == j:
                continue
            A[i][j] = gaussian_kernel(edge_list[i], edge_list[j])
    return A

    # for j in range(n)
    # for v, u in load_matrix_from_csv_file('./example1.dat'):

def elementwise(matrix, func):
    ''''''
    n_rows = len(matrix)
    result = []
    for i in range(n_rows):
        row = list(map(func, matrix[i]))
        result.append(row)
    return result


def construct_l(adjacency_matrix: list[list]):
    n = len(adjacency_matrix[0])
    D = [[0]*n for _ in range(n)]
    L = [[0]*n for _ in range(n)]
    for i in range(n):
        D[i][i] = sum(adjacency_matrix[i])
        inv_D = D[i][i]**(-1/2) 
        L[i][i] = inv_D * adjacency_matrix[i][i] * inv_D
    return L
    #D_i = elementwise(D, lambda x: x**(-1/2))

def k_largest_eigenvectors(L):
    pass

if __name__ == "__main__":
    matrix = load_matrix_from_csv_file("./example1.dat")
    adjacency_matrix = form_affinity_matrix(matrix)
    L = construct_l(adjacency_matrix)
