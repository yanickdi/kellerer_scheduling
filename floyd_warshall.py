import numpy as np
import sys

INFINITY = sys.maxsize

def floyd_warshall(adj):
    """
    Implementation of Floyd n Warshall's algorithm for finding the shortest path distance matrix for all pairs
    This implementation also deals with directed graph.
    Important: Assusming that there is a positive value greater than zero where
     a directed edge is available. (0 is no edge) 
    Returns: A distance matrix nxn
    """
    n = len(adj)
    #initialisiere das drei-dimensionale array dist:
    dist = []
    for i in range(n):
        dist.append([])
        for j in range(n):
            dist[i].append([])
            dist[i][j] = [None for k in range(n+1)]
            #dort wo nix steht schreibe unendlich (halbe hinein, weil ich muss ev. beide zusammenaddieren..)
            #ausser in der diagonale - da soll 0 stehen bleiben
            #alt = 0 if i == j else INFINITY/2
            #dist[i][j][0] = adj[i,j] if adj[i,j] != 0 else alt
            dist[i][j][0] = adj[i,j]
    #starte mit der rekursion:
    for k in range(n):
            for i in range(n):
                for j in range(n):
                    dist[i][j][k+1] = min(dist[i][j][k], dist[i][k][k] + dist[k][j][k])
                    #hier dist[i][k] weil dist array mit 0 beginnt!
    #fertig, in letzter dimension der distance matrix stehen nun die eintraege:
    final_dist = [ [dist[i][j][n] for j in range(n)] for i in range(n) ]
    return np.array(final_dist)