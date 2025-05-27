from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
total = 0
# master process
if rank == 0:
    data = 1
    # master process sends data to worker processes by
    # going through the ranks of all worker processes
    for i in range(0, size):
        comm.send(data, dest=i, tag=i)
        print('Process {} sent data:'.format(rank), data)

    results = 0
    for i in range(0, size): # receiving data
        result = comm.recv(source=i)
        results += result
# worker processes
else:
    # each worker process receives data from master process
    data = comm.recv(source=0, tag=rank)
    data = data+1
    comm.send(data, dest=0)
    print('Process {} received data:'.format(rank), data)
    time.sleep(10)

if rank == 0:
    print(results)