from collections import deque

    
class AbstractBranchAndBoundTree:
    def __init__(self, root):
        self.root = root
        
    def solve(self):
        self.calc_upper_bound()
        count = 0
        queue = deque([self.root])
        while (len(queue) > 0):
            node = queue.pop()
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
                    queue.appendleft(child)
        print('Best solution found: ', self.upper_bound)
        print('number of branch and bound nodes looked at:', count)

        
    def bound_at_node(self, node):
        raise NotImplementedError()
            
    def calcLeafSolution(self, node):
        raise NotImplementedError()
        
    def branch_at_node(self, node):
        raise NotImplementedError()
                    
                
    def calc_upper_bound(self):
        raise NotImplementedError()
        
    
class AbstractNode:
    def __init__(self, parent):
        self.parent = parent
        self.childs = []
        
    def __repr__(self):
        if self.parent is None:
            return 'ROOT'
        else:
            return 'CHILD'