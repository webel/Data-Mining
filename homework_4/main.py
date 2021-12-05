"""
Implementation of K-eigenvector Algorithm

Citation: 
    Ng, A. Y., Jordan, M. I., & Weiss, Y. (2002). 
    On spectral clustering: Analysis and an algorithm. 
    In Advances in neural information processing systems (pp. 849-856).
"""
import numpy as np
import argparse


def kMeans(X, K, epochs=100):
    """kMeans clustering algorithm
    Tweaked from https://gist.github.com/bistaumanga/6023692
    as to not need unnecessary scipy import.
    """
    centroids = X[np.random.choice(np.arange(len(X)), K)]
    for i in range(epochs):
        # Cluster Assignment step
        C = np.array(
            [
                np.argmin([np.dot(x_i - y_k, x_i - y_k) for y_k in centroids])
                for x_i in X
            ]
        )
        # Ensure we have K clusters, otherwise reset centroids and start over
        # If there are fewer than K clusters, outcome will be nan.
        if len(np.unique(C)) < K:
            centroids = X[np.random.choice(np.arange(len(X)), K)]
        else:
            # Move centroids step
            centroids = [X[C == k].mean(axis=0) for k in range(K)]
    return np.array(centroids), C


def load_edgelist_from_csv_file(file_path: str):
    return np.loadtxt(file_path, delimiter=",", dtype=int, usecols=(0, 1))


def form_affinity_matrix(S):
    """Provided an edge_list S return the affinity matrix for the nodes"""
    # Using the fact that ||x-y||^2 = ||x||^2 + ||y||^2 - 2 * x^T * y.
    # S_norm = np.sum(S ** 2, axis=-1)
    # return np.exp(
    #     -(S_norm[:, None] + S_norm[None, :] - 2 * np.dot(S, S.T)) / 2 * sigma ** 2
    # )
    # NOTE: the above works well to cluster edges, but we want
    # to cluster the points given that there exists an edge, which is binary.
    n = np.unique(S).size  # Gives us the number of nodes
    A = np.zeros((n, n))
    for edge in S:
        A[edge[0] - 1][edge[1] - 1] = 1
        A[edge[1] - 1][edge[0] - 1] = 1
    return A


def construct_l(A):
    D = np.diag(np.sum(A, axis=1))
    D_inv = np.linalg.inv(np.sqrt(D))
    # Return the constructed L matrix
    return np.dot(np.dot(D_inv, A), D_inv)


def k_largest_eigenvectors(L, k):
    """Get the k largest eigenvectors from L"""
    # Returns eigenvectors as columns with largest to the right
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    # return k largest eigenvalues & eigenvectors
    # by slicing the matrix at the kth column from
    # the right
    return eigenvalues[-k:], eigenvectors[:, -k:]


def renormalize_x(X):
    """Step 4: Form matrix Y by renormalizing X"""
    return X / np.sqrt(np.sum(X ** 2, axis=1)).reshape(-1, 1)


def plot_graph(edge_list, labels):
    import networkx as nx
    import matplotlib.pyplot as plt

    nodes = np.unique(edge_list)
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edge_list)
    plt.figure()
    nx.draw(graph, node_color=labels, font_color="white")
    plt.show()


def nips_clustering_algorithm(data_path, k, plot=False):
    # Base step, load the edges S.
    edge_list = load_edgelist_from_csv_file(data_path)
    # Step 1: Form the affinity matrix
    adjacency_matrix = form_affinity_matrix(edge_list)
    # Step 2: Construct L
    L = construct_l(adjacency_matrix)
    # Step 3: Get the k largest eigenvectors of L
    # NOTE: potentially use eigenvalues to choose k, note
    # sure yet if the penny has dropped on how
    _, X = k_largest_eigenvectors(L, k)
    # Step 4: Form matrix Y from X by renormalizing X to unit length
    Y = renormalize_x(X)
    # Step 5: Cluster given arbitrary algorithm, here using kMeans
    # as suggested in paper
    _, labels = kMeans(Y, k)
    print("Label for each node", labels)
    if plot:
        plot_graph(edge_list, labels)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        default="example1.dat",
        help="Provide csv file path, default: example1.dat",
    )
    parser.add_argument(
        "-k",
        "--n_clusters",
        default=4,
        help="Provide number of clusters, default: 4",
    )
    parser.add_argument(
        "-plt",
        "--plot",
        default=False,
        action="store_true",
        help="Whether to plot the network and clusters, default: False",
    )
    args = parser.parse_args()
    n = 4
    print(f"Outputs from {n} runs: ")
    for i in range(n):
        nips_clustering_algorithm(args.path, int(args.n_clusters), args.plot)
