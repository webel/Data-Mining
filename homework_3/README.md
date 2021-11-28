# Homework 3

## Toy Dataset

![Toy graph](toy_graph.png)
*Graph borrowed from [research gate].*


## Streaming Triangles

Two primary data structures:

- edge reservoir

        Uniform random sample of edges observed so far

- wedge reservoir

        Aims to select a uniform sample of wedges.
        Specifically, it maintains a uniform sample of the wedges created by the edge reservoir at any step of the process. (The wedge reservoir may include wedges whose edges are no longer in the edge reservoir.)

Two parameters:

- $s_e$

- $s_w$

**...to be continued...**

[research gate]: https://www.researchgate.net/figure/Example-graph-with-12-wedges-and-1-triangle_fig1_221666184

## Reservoir sampling pseudocode

    (* S has items to sample, R will contain the result *)
    ReservoirSample(S[1..n], R[1..k])
    // fill the reservoir array
    for i := 1 to k
        R[i] := S[i]

    // replace elements with gradually decreasing probability
    for i := k+1 to n
        (* randomInteger(a, b) generates a uniform integer from the inclusive range {a, ..., b} *)
        j := randomInteger(1, i)
        if j <= k
            R[j] := S[i]
