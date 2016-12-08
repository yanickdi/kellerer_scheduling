import numpy as np
import sys

from floyd_warshall import floyd_warshall

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
        self.nodes = [self.start, self.end]
        self.n_machines, self.n_jobs = pij_matrix.shape
        self.job_sequence = {job_nr: [] for job_nr in range(self.n_jobs)}
        self.added_conjunctive_arcs = []
        
        for job_nr, job_sequence in enumerate(sequences):
            pre_node = self.start
            for i in range(len(job_sequence)):
                machine_nr = job_sequence[i]
                if machine_nr < 0: continue
                self.job_sequence[job_nr].append(machine_nr)
                weight = pij_matrix[machine_nr, job_nr]
                node = DisjunctiveGraph.Node(machine_nr, job_nr, weight=weight)
                self.nodes.append(node)
                pre_node.addOutgoing(node)
                pre_node = node
            # pre_node is last machine of this job, also connect to end
            pre_node.addOutgoing(self.end)
        
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
    
    def findOperation(self, machine, job):
        for node in self.nodes:
            if not node.is_start_or_end and node.machine == machine and node.job == job:
                return node
        return False
        
    def createAdjMatrix(self, no_edge_val=sys.maxsize, diag_val=None):
        arr = np.empty( (len(self.nodes), len(self.nodes)) )
        for i, from_node in enumerate(self.nodes):
            for j, to_node in enumerate(self.nodes):
                if to_node in from_node.outgoing_arcs:
                    arr[i,j] = from_node.weight
                else:
                    arr[i,j] = no_edge_val
        if diag_val is not None:
            for i in range(len(arr)):
                arr[i,i] = diag_val
        return arr
        
    def get_nr_edges(self):
        arr = self.createAdjMatrix(no_edge_val=-1)
        arr += 1
        print(np.count_nonzero(arr))
            
        
    def addConjunctiveArcsFromOperation(self, operation_node):
        added_arcs = self.added_conjunctive_arcs
        machine = operation_node.machine
        count_arcs_added = 0
        for node in self.nodes:
            if node != operation_node and node.machine == machine:
                # add here an outgoing arc from operation_node to node
                arc = {'from': operation_node, 'to': node}
                opposite_arc = {'from': node, 'to': operation_node}
                if arc in added_arcs or opposite_arc in added_arcs:
                    continue
                assert node not in operation_node.outgoing_arcs
                operation_node.addOutgoing(node)
                count_arcs_added += 1
                self.added_conjunctive_arcs.append(arc)
        return count_arcs_added
        
    def clearConjunctiveArcs(self):
        nr_cleared = 0
        for arc in self.added_conjunctive_arcs:
            arc['from'].removeOutgoing(arc['to'])
            nr_cleared += 1
        assert nr_cleared == len(self.added_conjunctive_arcs)
        self.added_conjunctive_arcs.clear()
        return nr_cleared
        
    def longest_path(self, start, end):
        adj = self.createAdjMatrix(no_edge_val=-sys.maxsize) * -1
        fl = floyd_warshall(adj)
        from_index = self.nodes.index(start)
        end_index = self.nodes.index(end)
        return fl[from_index, end_index] * -1
        
        
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
            self.incoming_arcs = []
            
        def addOutgoing(self, node):
            assert not self.is_end
            self.outgoing_arcs.append(node)
            node.incoming_arcs.append(self)
            
        def removeOutgoing(self, node):
            assert node in self.outgoing_arcs
            self.outgoing_arcs.remove(node)
            node.incoming_arcs.remove(self)
            
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
    graph.has_cycles()
    print(graph.longest_path(graph.start, graph.end))