#Makefile

.PHONY: default
default: build test clean

PYTHON = python
PYTHON_CONFIG = ${PYTHON} ./python-config
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}
NUMPY_INCLUDE = ${shell ${PYTHON} -c 'import numpy; print( numpy.get_include() )'}

SWIG = swig
SWIG_PY = ${SWIG} -python
SWIG_PYC = ${SWIG_PY} -c++
.PHONY: src
src: mpiplus_wrap.cxx
mpiplus_wrap.cxx: mpiplus.i
	${SWIG_PYC} -I${MPI4PY_INCLUDE} -o $@ $< 

MPICC = mpicc
MPICXX = mpicxx
DEBUG = -DDEBUG 
CFLAGS = -fPIC ${shell ${PYTHON_CONFIG} --includes} ${DEBUG}
LDFLAGS = -shared ${shell ${PYTHON_CONFIG} --libs}
#LDFLAGS = -fPIC -shared -lpthread -ldl -lutil
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
#SO = .so
#${shell ${PYTHON_CONFIG} --extension-suffix}
.PHONY: build
build: _mpiplus${SO}
_mpiplus${SO}: mpiplus_wrap.cxx mpiplus.cpp
	${MPICXX} ${CFLAGS} -I${MPI4PY_INCLUDE} -I${NUMPY_INCLUDE} -o $@ $^ ${LDFLAGS}


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 2
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} mpiplus_wrap.cxx mpiplus.py* _mpiplus${SO}
