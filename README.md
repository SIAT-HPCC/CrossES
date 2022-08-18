# Enhance Sampling

This program is based on OpenMM implementation of cross-node GPU parallel Enhance Sampling framework.

## Catalog

- [Instructions](#Instructions)
- [Problem to be developed](#Problem to be developed)


### Instructions
You can implement any enhanced sampling algorithm through our framework. We provide two important types of modules, including Replica and Force Constraint. To solve the communication problem, we also provide the MPI library for replica swapping. There are three special implementations you can use, including TMD, SMD, TREMD.

#### 1. SMD
``` python enhance/runSMD.py -n 500000 ```
``` 
optional arguments:
  -h, --help            show this help message and exit
  -f INPUT_FILE, --input INPUT_FILE
  -pf PARTICLE_FILE, --particlefile PARTICLE_FILE
  -n N_STEP, --n_step N_STEP
  -ks K_STAY, --k_stay K_STAY
  -km K_MOV, --k_mov K_MOV
  -v SPEED, --speed SPEED (nm/ps)
  -cf CONSTANT_FORCE, --constant_force CONSTANT_FORCE
  -o OUTPUT_FILE, --output OUTPUT_FILE
```
#### 2. TMD
``` python enhance/runSMD.py -n 500000 ```
```
optional arguments:
  -h, --help            show this help message and exit
  -f INPUT_FILE, --input INPUT_FILE
  -ta TARGET_PATH, --target_path TARGET_PATH
  -n N_STEP, --n_step N_STEP
  -ka K_ANGLE, --k_angle K_ANGLE
  -kd K_DIHE, --k_di K_DIHE
  -o OUTPUT_FILE, --output OUTPUT_FILE

```
#### 3. T-REMD

##### 3.1.Install
Make sure the following tools are included in your current environment before you use them
- MPICH: Version later than 3.3
- SWIG
- Anaconda,Install the Python Numpy MPI4PY OpenMM package
- GCC
- Make
- CUDA
- OpenMM
- python >= 3.7

##### 3.2.C++ partial compilation


- Enter the command  ``` make build ``` in the source file to begin the compilation process.

- If there is no error. Mpiplus_wrap. CXX, mpiplus.py and _mpiplus.so files generated in the directory indicate that the compilation is successful and the c++ extension code can be used as a Python package
- If you want to remove compiled code, type ``` make clean```.
- In line 22 of the Makefile, you can set whether to enable debug mode and output C++ messages. If you do not want to enable debug mode, comment out ${debug} on line 22.
- If you are worried about C++ code compiling, you can write a simple test script to see if the C++ part works properly.
  You can use ``` ctest.sh``` as an example in the appendix .If the paramlist and id of the C++ and Python codes correspond to each other, the C++ codes are compiled successfully and function properly(test.py getExchange_func() in line 26 is the call interface provided by the mpiplus module to Python. Comm is MPI.COMM.I stands for the current iteration number,state stands for the state array that the current process needs to pass to the main process,paramlist is the parameter list of the process,ex_kind and md_kind are the options for subsequent development, currently only (1,1) are supported.

##### 3.3REMD 

- The resource allocation commands run across nodes as a script with four replicas of testremd.py are as follows:
   ```python setconfigfile.py --np 4 python testREMD.py -debug```
   In the command, -np specifies the number of copies to run, testremd. py specifies the REMD program that needs to allocate node resources to run, and -debug specifies whether to output debugging information. After the command is executed, the configfile and hostfile files are generated to save the running information of the process.
- Run the code on the specified node and GPU, and enter the following command in the script:
    ```  mpiexec.hydra -f hostfile -configfile configfile```
     For actual scripts, see ```run.sh/ rerun```
- Result output: Take the output of the test result of sample testremd.py as an example:
PDB	out/out0.pdb, out/out1.pdb....
Simulation information out/md0.log, out/md1.log....
The Debug information the Debug log
Ex_pair.out is exchanged each time
Temperature replica parameter replica.out
Breakpoint file Checkpoint0.44 (replica 0, breakpoint for iteration 44)
It is worth explaining that the last act of replica.out is the order of the next iteration and the ID of the temperature list that should be used by each replica. Therefore, this file is also an important basis for breakpoint restart.
##### 3.4.Checkpoint Restart
If you need a breakpoint restart, set the restart parameter of remd.run () to True to resume the original program. Note that the output file of the simulation result should be numbered. Take replica 0 as an example. The PBD for the first restart can be named out0-1.pdb and the PBD for the second restart can be out0-2.pdb. If this is the case, you can use the provided mergepdb.py for PDB integration. Out0.pdb, out0-1.pdb,... , out0-n.pdb and the restart.log file that holds the restart information are put together with the Mergepdb program using the get_pDB (pdb_numb, rank, pdb_Iteration, n_iteration) function defined in mergerPDB. Pdb_numb indicates the number of PDB files to be consolidated, rank indicates the current replica number, pdb_Iteration indicates the interval between PDB files to be consolidated, and n_iteration indicates the total number of PDB files to be consolidated.
The actual running program can refer to restartremd.py and submit the script as rerun.sh.


#### 3.5 Problem to be developed

- Lets the user specify whether the temperature is continuous or the trajectory is continuous
- Compressed storage of the result PDB
- Matches Gromacs

