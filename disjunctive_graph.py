import numpy as np
import sys

class DisjunctiveGraph:
    def __init__(self, pij_matrix, sequences):
        """
        pij_matrix: a numpy 2-dim matrix where pt_i_j is the processing time
                          on machine i of job j (rows: machines, cols: jobs)
        sequences:  a numpy 2-dim matrix  where row is job and col is the sequence,
                      like [[0, 1, 2]] is only one job that have to visit M1->M2->M3
        """
        self.start = DisjunctiveGraph.Node(machine=None, job=None, is_start=True)
        self.end = DisjunctiveGraph.Node(machine=None, job=None, is_end=True)
        self.nodes = set([self.start, self.end])
        for job_nr, job_sequence in enumerate(sequences):
            pre_node = self.start
            for i in range(len(job_sequence)):
                machine_nr = job_sequence[i]
                weight = pij_matrix[machine_nr, job_nr]
                node = DisjunctiveGraph.Node(machine_nr, job_nr, weight=weight)
                self.nodes.add(node)
                pre_node.addOutgoing(node)
                if i == len(job_sequence)-1:
                    # last machine of this job, also connect to end
                    node.addOutgoing(self.end)
                pre_node = node
        
    def has_cycles(self):
        """
            Checks whether this graph has cycles in it or not (only checks conjunctive arcs..)
            Algorithm: Graph Coloring Algorithm, DFS Traversal
            Returns True if graph has cycles, false if not
        """
        WHITE, GREY, BLACK = 0, 1, 2        
        def explore_cycles_dfs(start_node):
            colours[node] = GREY
            for adjNode in start_node.outgoing_arcs:
                if colours[adjNode] == GREY:
                    return True
                
                if colours[adjNode] == WHITE:
                    if explore_cycles_dfs(adjNode) == True:
                        return True
                        
            colours[start_node] = BLACK
            return False
        
        colours = {node: WHITE for node in self.nodes}
        for node in self.nodes:
            if colours[node] == WHITE:
                if explore_cycles_dfs(node) == True:
                    return True
        return False
        
    def shortest_path(self, start, end):
        """
          Implementation of Dijkstra's shortest path algorithm.
          adj: adjacency matrix
          start: start node
          end: end node
          Returns: The length of the shortest path
            #The first: the length of the shortest path from s to to
            #The second a list of nodes on the shortest path, first node of the list is s, last node v
        """
        INF = sys.maxsize
        Q = set(self.nodes)
        dist = {node: INF for node in self.nodes}
        dist[start] = 0
        
        while len(Q) > 0:
            u = min(Q, key= lambda node: dist[node])
            Q.remove(u)
            for v in u.outgoing_arcs:
                alt = dist[u] + u.weight
                if alt < dist[v]:
                    dist[v] = alt
        return dist[end]
        
    def longest_path(self, start, end):
        """
          Implementation of Dijkstra's shortest path algorithm.
          adj: adjacency matrix
          start: start node
          end: end node
          Returns: The length of the shortest path
            #The first: the length of the shortest path from s to to
            #The second a list of nodes on the shortest path, first node of the list is s, last node v
        """
        INF = sys.maxsize
        Q = set(self.nodes)
        dist = {node: -INF for node in self.nodes}
        dist[start] = 0
        
        while len(Q) > 0:
            u = max(Q, key= lambda node: dist[node])
            Q.remove(u)
            for v in u.outgoing_arcs:
                alt = dist[u] + u.weight
                if alt > dist[v]:
                    dist[v] = alt
        return dist[end]
        
        
    class Node:
        def __init__(self, machine, job, weight=0, is_start=False, is_end=False):
            self.machine = machine
            self.job = job
            self.weight = weight
            self.is_start = is_start
            self.is_end = is_end
            self.is_start_or_end = is_start or is_end
            # a list of tuples, the first elem in tuple is the other node,
            # the second is a integer of its weight
            self.outgoing_arcs = []
            
        def addOutgoing(self, node):
            assert not self.is_end
            self.outgoing_arcs.append(node)
            
        def __getitem__(self, key):
            return self.outgoing_arcs[key]
        
        def __repr__(self):
            if self.is_start_or_end:
                return 'START' if self.is_start else 'END'
            else:
                return 'M{}J{}[t={}]'.format(self.machine+1, self.job+1, self.weight)
                
        def to_string(self):
            """ more information than repr """
            if self.is_start_or_end:
                outgoings = [str(node) for node in self.outgoing_arcs]
                outgoings = ','.join(outgoings)
                name = 'START' if self.is_start else 'END'
                return '{}  conj:({})'.format(name, outgoings)
            else:
                outgoings = [str(node) for node in self.outgoing_arcs]
                outgoings = ','.join(outgoings)
                return 'M{}J{}  conj:({})'.format(self.machine+1, self.job+1, outgoings)
        
        
if __name__ == '__main__':
    pij_matrix = np.array([
        [4, 4, 3, 1], #Machine 1
        [3, 1, 2, 3], #Machine 2
        [2, 4, 3, 3]])#Machine 3
        
    sequences = np.array([
        [1,2,3], #Job 1
        [2,1,3], #Job 2
        [3,2,1], #Job 3
        [2,3,1]  #Job 4
        ])
        
    sequences -= 1 # job one has to be 0, etc.
        
    graph = DisjunctiveGraph(pij_matrix, sequences)
    print(graph.longest_path(graph.start, graph.end))