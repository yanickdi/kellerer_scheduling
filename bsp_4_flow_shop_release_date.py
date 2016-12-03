#https://repl.it/EfQt/1
import sys
from collections import deque


class FlowShopCmaxBnB():
    def __init__(self, data, upper_bound=None, non_optimality_factor=0):
        self.nr_nodes = 0
        root = self.Node(parent=None, fixed=[], bnb=self)
        self.root = root
        self.data = data
        self.n = len(data['aj'])
        assert 0 <= non_optimality_factor < 1
        self.non_optimality_factor = non_optimality_factor
        assert len(data['aj']) == len(data['bj']) == len(data['cj'])
        if data.get('rj'): assert len(data['aj']) == len(data['rj'])
        self.upper_bound = upper_bound
        
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
            print('Cmax: {}'.format(LB))
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
            if LB * (1 + self.non_optimality_factor) < (self.upper_bound):
                return True
            else:
                print('Verwerfe Knoten ({} >= {})'.format(LB*(1+self.non_optimality_factor), self.upper_bound))
                return False
        
    def calc_alpha_beta_gamma(self, fixed_jobs):
        """ returns three lists: alpha, beta, gamma of input list fixed_jobs"""
        time_matrix = [[], [], []]
        for j in fixed_jobs:
            time_matrix[0].append(self.data['aj'][j])
            time_matrix[1].append(self.data['bj'][j])
            time_matrix[2].append(self.data['cj'][j])
        release_dates = None
        if self.data.get('rj'):
            release_dates = [self.data['rj'][j] for j in fixed_jobs]
        c_matrix = calc_compl_times(time_matrix, schedule=range(len(fixed_jobs)),
            release_dates = release_dates)
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

def calc_compl_times(time_matrix, schedule, release_dates=None):
    """
        returns a matrix, where the rows are jobs, cols are machines
        the row is ordered according to schedule, i.e. schedule [2,1] -->
        first row is job 2, second row job 1
    """
    nr_machines = len(time_matrix)
    nr_jobs = len(time_matrix[0])
    c_matrix = [[0] * nr_machines for _ in range(nr_jobs)]
    for i in range(nr_machines):
        for j, job in enumerate(schedule):
            #c_i_j = max(c_i-1_j, c_i,j_1)
            pre_i = i - 1 if i > 0 else 0
            pre_j = j - 1 if j > 0 else 0
            if release_dates and i == 0:
                c_matrix[j][i] = max(c_matrix[pre_j][i], release_dates[j]) +  + time_matrix[i][job]
            else:
                c_matrix[j][i] = max(c_matrix[j][pre_i], c_matrix[pre_j][i]) + time_matrix[i][job]
                
    return c_matrix

        
if __name__ == '__main__':
    data = {
        'aj': [ 13,  7, 16,  4],
        'bj': [  5,  3,  9,  8],
        'cj': [  4, 16, 18,  2],
        'rj': [  0,  6, 14, 12]
        }
    bnb = FlowShopCmaxBnB(data, non_optimality_factor=.125, upper_bound=63)
    bnb.solve() 