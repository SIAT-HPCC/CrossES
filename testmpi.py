from mpi4py import MPI
import mpilib.mpiplus as mp
import numpy as np
import sys
import os
import socket

# -- Get MPI --
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
#logging.basicConfig(level = logging.DEBUG)

#output GPU and  host
device_index = os.environ.get("CUDA_VISIBLE_DEVICES")
nodename = socket.gethostname()
#logging.info("    !------!!! rank is %i, nodename = %s, idx = %s!!----- "%(rank, nodename, device_index))
print("    !------!!! rank is %i, nodename = %s, idx = %s!!----- "%(rank, nodename, device_index))

state = np.arange(1).astype(float)
paramlist = np.arange(size).astype(int)
state_size = len(state)
n_iteration = 3
ex_kind = 1
md_kind = 1

for i in range(n_iteration):
    print("rank %d, it %d"%(rank, i))
    x = rank * i
    for j in range(5):
      x *= 2.0
      state[0] = x
    idx = mp.getExchange_func(comm, i, state, paramlist, ex_kind, md_kind)
    print("rank %d in range(%d) send %f, and get idx = %d"%(rank, i, state[0], idx))
    for j in range(len(paramlist)):
       print("python :now%d: paramlist[%i]=%i"%(i,j,paramlist[j]))	
    print(" rank %d ok！"%rank)




