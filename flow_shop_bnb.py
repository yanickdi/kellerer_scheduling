import sys
from collections import deque
import numpy as np

from disjunctive_graph import DisjunctiveGraph

class FlowShopBnb():
    def __init__(self, disj_graph, start_upper_bound=None):
        self.nr_nodes = 0
        self.disj_graph = disj_graph
        root = self.Node(parent=None, fixed=[], bnb=self)
        self.root = root
        self.upper_bound = start_upper_bound
        
    def branch_at_node(self, node):
        m2j2 = self.disj_graph.start[1]
        m1j1 = self.disj_graph.start[0]
        m1j2 = m2j2[0]
        
        # all first operations
        for operation in self.getOmegas(node.fixed):
            fixed = node.fixed[:] + [operation]
            new_node = FlowShopBnb.Node(parent=node, fixed=fixed, bnb=self)
            node.childs.append(new_node)
                
    def getOmegas(self, fixed_operations):
        graph = self.disj_graph
        omegas = []
        for job in range(graph.n_jobs):
            sequence = graph.job_sequence[job]
            fixed_machines_of_job = [op.machine for op in fixed_operations if op.job == job]
            sequence_pos = 0
            for i, fixed_machine in enumerate(fixed_machines_of_job):
                if sequence[i] == fixed_machine:
                    sequence_pos += 1
            if sequence_pos < len(sequence):
                operation = graph.findOperation(sequence[sequence_pos], job)
                omegas.append(operation)
        return omegas
                    
    def bound_at_node(self, node):
        graph = self.disj_graph
        arcs_added = []
        for operation in node.fixed:
            arcs_added.extend(graph.addConjunctiveArcsFromOperation(operation))
        
        if graph.has_cycles():
            # infeasible
            LB = False
        else:
            LB = graph.longest_path(graph.start, graph.end)
        graph.removeConjunctiveArcs(arcs_added)
        print('LB: {}'.format(LB))
        return LB
        
        
    def solve(self):
        count = 0
        queue = deque([self.root])
        while (len(queue) > 0):
            node = queue.popleft() #using as real queue
            print()
            print(node)
            count += 1
            if count % 10000 == 0:
                print(count)
            shallBranch = True # default: branch (at root node e.g.)
            if node != self.root:
                shallBranch = self.bound_at_node(node)
            
            if shallBranch:
                self.branch_at_node(node)
                for child in node.childs:
                    queue.append(child)
        print('Best solution found: ', self.upper_bound)
        print('number of branch and bound nodes looked at:', count)
        
    class Node():
        def __init__(self, parent, fixed, bnb):
            self.parent = parent
            self.childs = []
            self.fixed = fixed
            self.bnb = bnb
            self.node_id = bnb.nr_nodes
            bnb.nr_nodes += 1
        
        def __str__(self):
            if self.parent is None:
                return 'ROOT'
            str_fixed = ['({},{})'.format(op.machine+1, op.job+1) for op in self.fixed]
            return ' , '.join(str_fixed)
        
if __name__ == '__main__':
    _ = 0
    pij_matrix = np.array([
        [10,  3,  4], #Machine 1
        [ 8,  8,  7], #Machine 2
        [ 4,  6,  _], #Machine 4
        [ _,  5,  3]])#Machine 3
        
    sequences = np.array([
        [1,2,3, _], #Job 1
        [2,1,4,3], #Job 2
        [1,2,4, _]])   #Job 3
    sequences -= 1 # job one has to be 0, etc.
        
    graph = DisjunctiveGraph(pij_matrix, sequences)
    bnb = FlowShopBnb(graph, start_upper_bound=500)
    bnb.solve()