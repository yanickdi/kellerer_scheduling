import sys
from abstract_branch_and_bound import AbstractBranchAndBoundTree, AbstractNode


class SumTjBnB(AbstractBranchAndBoundTree):
    def __init__(self, data):
        self.nr_nodes = 0
        root = self.Node(parent=None, fixed=[], bnb=self)
        super().__init__(root)
        self.data = data
        self.n = len(data['j'])
        
    def calc_upper_bound(self):
        self.upper_bound = 26
        
    def branch_at_node(self, node):
        branch_pos = len(node.fixed)
        if branch_pos == (self.n):
            # we are at a leaf, return
            return
        else:
            for j in self.data['j']:
                if j not in node.fixed:
                    child = self.Node(parent=node, fixed=node.fixed + [j], bnb=self)
                    node.childs.append(child)
                    
    def bound_at_node(self, node):
        if len(node.fixed) == self.n:
            sol = self._leaf_solution(node)
            print('Bin am Ende angelangt, SumTJ: {}'.format(sol))
            if sol < self.upper_bound:
                self.upper_bound = sol
                print('NEUER UPPER BOUND: {}'.format(sol))
            return False
        else:
            #lb: sum over all j elem of N2 (fixed from behind): max{P1 + pj - dj, 0}
            N2 = set(node.fixed)
            N1 = set(j for j in self.data['j'] if j not in N2)
            processing_time_n1 = sum(self._pj(j) for j in N1)
            sum_due_dates = 0
            for j in N2:
                dj = max(processing_time_n1 + self._pj(j) - self._dj(j), 0)
                sum_due_dates += dj
            lb = sum_due_dates
            print('Lower Bound fuer Knoten {}: {}'.format(node, lb))
            if lb >= self.upper_bound:
                print('Hier nicht weiter verzweigen, da lb >= ub')
                return False
            else:
                print('Hier sollte weiter verzweigen, Chance, dass hier wo optimale Loesung enthalten ist gegeben')
                return True
        
    def _leaf_solution(self, node):
        cum_cj = 0
        cum_tj = 0
        for j in reversed(node.fixed):
            cum_cj += self._pj(j)
            cum_tj += max(cum_cj - self._dj(j), 0)
        return cum_tj
        
    def _pj(self, job_id):
        #find index:
        index = self.data['j'].index(job_id)
        return self.data['pj'][index]
        
    def _dj(self, job_id):
        #find index:
        index = self.data['j'].index(job_id)
        return self.data['dj'][index]
        
    class Node(AbstractNode):
        def __init__(self, parent, fixed, bnb):
            super().__init__(parent)
            self.fixed = fixed
            self.bnb = bnb
            self.node_id = bnb.nr_nodes
            bnb.nr_nodes += 1
        
        def __str__(self):
            n = len(self.bnb.data['j'])
            return 'x' * (n - len(self.fixed)) + ''.join(str(j) for j in reversed(self.fixed))
        
if __name__ == '__main__':
    data = {'j' : [1,2,3,4],
        'pj': [14,12,7,9],
        'dj': [23, 19, 23, 15]
        }
    bnb = SumTjBnB(data)
    bnb.solve()