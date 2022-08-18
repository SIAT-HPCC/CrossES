/*  Example of wrapping a C function that takes a C double array as input using
 *  numpy typemaps for SWIG. */

%module mpiplus
%{
    /* the resulting C file should be built as a python extension */
    #define SWIG_FILE_WITH_INIT
    /*  Includes the header in the wrapper code */
    #include "mpiplus.h"
%}

/*  include the numpy typemaps */
%include "numpy.i"

%include "mpi4py/mpi4py.i"

/*  need this for correct module initialization */
%init %{
    import_array();
%}
%mpi4py_typemap(Comm, MPI_Comm);

/*  typemaps for the two arrays, the second will be modified in-place */
%apply (double* IN_ARRAY1, int DIM1) {(double * a, int size_a)}
%apply (long* INPLACE_ARRAY1, int DIM1) {(long * b, int size_b)}

/*  Wrapper for cos_doubles that massages the types */
%inline %{
    /*  takes as input two numpy arrays */
    long getExchange_func(MPI_Comm comm, int nowitera, double * a, int size_a, long * b, int size_b, int ex_kind, int md_kind) {
        /*  calls the original funcion, providing only the size of the first */
		return getExchange(comm, nowitera, a, size_a, b, size_b, ex_kind, md_kind);
    }
%}
