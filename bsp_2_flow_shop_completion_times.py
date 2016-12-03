# https://repl.it/Ed4N/2

def main():
    time_matrix = [
        [5, 3, 4, 5], #aj's
        [1, 6, 3, 5], #bj's
        [7, 2, 1, 3]] #cj's
    schedule = [1,2,4,3]
    
    c_matrix = calc_compl_times(time_matrix, [i-1 for i in schedule])
    print_c_matrix(c_matrix, schedule)

def calc_compl_times(time_matrix, schedule):
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
            c_matrix[j][i] = max(c_matrix[j][pre_i], c_matrix[pre_j][i]) + time_matrix[i][job]
    return c_matrix
    
def print_c_matrix(c_matrix, schedule):
    greeks = ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta')
    nr_machines = len(c_matrix[0])
    nr_jobs = len(c_matrix)
    print(' c_j_i | {} |'.format('|'.join('{}'.format((l+'_j').ljust(10).rjust(15)) for l in greeks[0:nr_machines])))
    for i, line in enumerate(c_matrix):
        job = schedule[i]
        print(' {}     | {} |'.format(job, '|'.join('{:7d}  '.format(elem).ljust(15) for elem in line)))
        
    print('\nCMax: {}'.format(c_matrix[-1][-1]))
    
if __name__ == '__main__':
    main()