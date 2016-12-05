#https://repl.it/EfVg/0
import sys
from collections import deque
from munkres import Munkres, print_matrix


class TeppichFaerberBnB():
    def __init__(self, data, start_upper_bound=None):
        self.nr_nodes = 0
        root = self.Node(parent=None, fixed=[], bnb=self)
        self.root = root
        self.data = data
        self.n = len(data['pi'])
        self.upper_bound = start_upper_bound
        
    def branch_at_node(self, node):
        branch_pos = len(node.fixed)
        if branch_pos == (self.n):
            # we are at a leaf, return
            return
                    
    def bound_at_node(self, node):
        sum_pj = sum(self.data['pi'])
        LB = sum_pj
        # add the length we have already
        pre = 0
        for j in node.fixed:
            LB += self.data['pij'][pre][j+1]
            pre = j+1
        if len(node.fixed) == self.n:
            # we are at leaf
            LB += self.data['pij'][node.fixed[-1]+1][0]
            print(LB)
            if LB < self.upper_bound:
                self.upper_bound = LB
            return False
        # add minimas of all rows where i have not added already to lb (= all rows not in pre's)
        rows = [i+1 for i in range(self.n) if i not in node.fixed[:-1]]
        cols = [0] + [v+1 for v in range(self.n) if v not in node.fixed]
        matrix = ([[self.data['pij'][row][col] for col in cols] for row in rows])
        for line in matrix:
            assert len(matrix) == len(line)
        zop_value = self.zop(matrix)
        LB += zop_value
        print('Lowerbound: {} (sum pj={} + fixed={} + zop={})'.format(
            LB, sum_pj, LB-zop_value-sum_pj, zop_value))
        return LB < self.upper_bound
        
    def zop(self, matrix):
        """ solves a Linear ZOP and returns its value"""
        m = Munkres()
        sum = 0
        for row, col in m.compute(matrix):
            sum += matrix[row][col]
        return sum
        
    def solve(self):
        count = 0
        queue = deque([self.root])
        while (len(queue) > 0):
            node = queue.pop() #using as real queue
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
                for child in reversed(node.childs):
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
            n = self.bnb.n
            return ''.join(str(j+1) for j in self.fixed) + 'x' * (n - len(self.fixed))
        
if __name__ == '__main__':
    _ = 10000
    data = {
        'pij':[
            [_, 2, 5, 3, 6],
            [2, _, 4, 2, 0],
            [5, 4, _, 6, _],
            [3, 2, 6, _, 1],
            [6, _, _, 1, _]],
        'pi': [10, 8, 2, 9]
        }
    bnb = TeppichFaerberBnB(data, start_upper_bound=48)
    bnb.solve()