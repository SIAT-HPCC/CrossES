#!/bin/sh

swig -c++ -python -I/home/siat/workfs/TOOLS/anaconda3/include/python3.6m -I/home/siat/workfs/TOOLS/anaconda3/lib/python3.6/site-packages/mpi4py/include  mpiplus.i

mpic++ -I/home/siat/workfs/TOOLS/anaconda3/include/python3.6m -I/home/siat/workfs/TOOLS/anaconda3/lib/python3.6/site-packages/mpi4py/include  -o _mpiplus.so mpiplus.cpp mpiplus_wrap.cxx -fPIC -shared -lpthread -ldl -lutil
