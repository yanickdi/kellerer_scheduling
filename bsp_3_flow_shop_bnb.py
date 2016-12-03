#https://repl.it/EfLm/1
import sys
from collections import deque
from bsp_2_flow_shop_completion_times import calc_compl_times


class FlowShopCmaxBnB():
    def __init__(self, data, start_upper_bound=None):
        self.nr_nodes = 0
        root = self.Node(parent=None, fixed=[], bnb=self)
        self.root = root
        self.data = data
        self.n = len(data['aj'])
        assert len(data['aj']) == len(data['bj']) == len(data['cj'])
        self.upper_bound = start_upper_bound
        
    def calc_upper_bound(self):
        if self.upper_bound == None:
            # do a heuristic here
            raise NotImplementedError()
        
    def branch_at_node(self, node):
        branch_pos = len(node.fixed)
        if branch_pos == (self.n):
            # we are at a leaf, return
            return
        else:
            for j in range(self.n):
                if j not in node.fixed:
                    child = self.Node(parent=node, fixed=node.fixed + [j], bnb=self)
                    # only one unfixed? fix em
                    if len(child.fixed) == self.n - 1:
                        last_unfixed = (set(job for job in range(self.n)) - set(child.fixed)).pop()
                        child.fixed.append(last_unfixed)
                    node.childs.append(child)
                    
    def bound_at_node(self, node):
        A = node.fixed
        B = [j for j in range(self.n) if j not in A] # unfixed jobs
        alpha, beta, gamma = self.calc_alpha_beta_gamma(A)
        k = len(A)-1 # index of last job in fixed schedule
        if len(B) <= 0:
            # this is a leaf!
            LB = gamma[k]
            if LB < self.upper_bound:
                # new best solution found!
                print('NEUER UPPER BOUND: {}'.format(LB))
                self.upper_bound = LB
            return False
        else:
            aj, bj, cj = self.data['aj'], self.data['bj'], self.data['cj']
            LB3 = gamma[k] + sum(cj[j] for j in B)
            LB2 = beta[k] + sum(bj[j] for j in B) + min(self.data['cj'][j] for j in B)
            LB1 = alpha[k] + sum(aj[j] for j in B) + min(bj[j] + cj[j] for j in B)
            LB = max(LB1, LB2, LB3)
            print('LB1: {}, LB2: {}, LB3: {} --> LB={}'.format(LB1, LB2, LB3, LB))
            if LB < self.upper_bound:
                return True
            else:
                print('Verwerfe Knoten')
                return False
        
    def calc_alpha_beta_gamma(self, fixed_jobs):
        """ returns three lists: alpha, beta, gamma of input list fixed_jobs"""
        time_matrix = [[], [], []]
        for j in fixed_jobs:
            time_matrix[0].append(self.data['aj'][j])
            time_matrix[1].append(self.data['bj'][j])
            time_matrix[2].append(self.data['cj'][j])
        c_matrix = calc_compl_times(time_matrix, schedule=range(len(fixed_jobs)))
        alpha = [c_matrix[j][0] for j in range(len(fixed_jobs))]
        beta = [c_matrix[j][1] for j in range(len(fixed_jobs))]
        gamma = [c_matrix[j][2] for j in range(len(fixed_jobs))]
        return alpha, beta, gamma
        
    def _leaf_solution(self, node):
        raise NotImplementedError()
        
    def _print_leaf_sol(self, node):
        raise NotImplementedError()
        
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
            n = self.bnb.n
            return ''.join(str(j+1) for j in self.fixed) + 'x' * (n - len(self.fixed))
        
if __name__ == '__main__':
    data = {
        'aj': [ 6,14,  3, 10],
        'bj': [ 9, 8, 17, 10],
        'cj': [ 3, 2,  5, 10]
        }
    bnb = FlowShopCmaxBnB(data, start_upper_bound=49)
    bnb.solve()