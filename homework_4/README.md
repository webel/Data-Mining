# Homework 4

## Algorithm

1. Form the affinity matrix from the edge list, where

    $$A \in R^{n*n}, A_{ij} = \dfrac{exp(-||s_i-s_j||)^2}{2\sigma}$$

    if $i ≠ j$ and $A_{ii} = 0$.

2. Define D to be the diagonal matrix whose (i, i)-element is the sum of the A's i-th row, and construct the matrix $L = D^{-1/2} AD^{-1/2}$

3. Find $x_1, x_2,...,x_k$ the k largest eigenvectors of L (orthogonal to each other in the case of repeated eigenvalues), and form the matrix $X = [x_1x_2...x_3] \in R^{n * k}$ by stacking the eigenvectors in columns.

4. Form the matrix Y from X by renormalizing each of X's rows to have unit length (i.e. $Y_{ij} = X_{ij}/(\sum_j X^2_{ij})^{1/2}$).

5. Treating each row of Y as a point in $R^k$, cluster them into $k$ clusters via K-means or any other algorithm.

6. Assign the original point $s_i$ to cluster $j$ iff row $i$ of the matrix $Y$ was assigned to cluster $j$.
