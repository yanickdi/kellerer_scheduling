# https://repl.it/EdSX
import sys
from collections import deque


class SumTjBnB():
    def __init__(self, data, start_upper_bound=None):
        self.nr_nodes = 0
        root = self.Node(parent=None, fixed=[], bnb=self)
        self.root = root
        self.data = data
        self.n = len(data['j'])
        self.upper_bound = start_upper_bound
        
    def calc_upper_bound(self):
        if self.upper_bound == None:
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
                    # only one unfixed? fix em
                    if len(child.fixed) == self.n - 1:
                        last_unfixed = (set(job for job in self.data['j']) - set(child.fixed)).pop()
                        child.fixed.append(last_unfixed)
                    node.childs.append(child)
                    
    def bound_at_node(self, node):
        if len(node.fixed) == self.n:
            sol = self._leaf_solution(node)
            print('Bin am Ende angelangt, SumTJ: {}'.format(sol))
            self._print_leaf_sol(node)
            if sol < self.upper_bound:
                self.upper_bound = sol
                print('NEUER UPPER BOUND: {}'.format(sol))
            return False
        else:
            #lb: sum over all j elem of N2 (fixed from behind): max{P1 + pj - dj, 0}
            N2 = set(node.fixed)
            N1 = set(j for j in self.data['j'] if j not in N2)
            processing_time_n1 = sum(self._pj(j) for j in N1)
            sum_delays = 0
            for j in N2:
                dj = max(processing_time_n1 + self._pj(j) - self._dj(j), 0)
                sum_delays += dj
            print('N1: {}, P1: {}'.format(N1, processing_time_n1))
            lb = sum_delays
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
        
    def _print_leaf_sol(self, node):
        time = 0
        jobs, cj, tj = [], [], []
        for j in reversed(node.fixed):
            time += self._pj(j)
            jobs.append(j)
            cj.append(time)
            tj.append(max(time - self._dj(j), 0))
        print('jobs: |{}|'.format('|'.join('{:7d}  '.format(num) for num in jobs)))
        print('  cj: |{}|'.format('|'.join('{:7d}  '.format(num) for num in cj)))
        print('  tj: |{}|  sum_tj={}'.format('|'.join('{:7d}  '.format(num) for num in tj),sum(tj)))
        
    def _pj(self, job_id):
        #find index:
        index = self.data['j'].index(job_id)
        return self.data['pj'][index]
        
    def _dj(self, job_id):
        #find index:
        index = self.data['j'].index(job_id)
        return self.data['dj'][index]
        
    def solve(self):
        self.calc_upper_bound()
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
            n = len(self.bnb.data['j'])
            return 'x' * (n - len(self.fixed)) + ''.join(str(j) for j in reversed(self.fixed))
        
if __name__ == '__main__':
    data = {'j' : [1,2,3,4],
        'pj': [14,12,7,9],
        'dj': [23, 19, 23, 15]
        }
    bnb = SumTjBnB(data, start_upper_bound=28)
    bnb.solve()