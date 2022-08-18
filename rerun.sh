#!/bin/sh
#SBATCH -J restart
#SBATCH -p gpu
#SBATCH -N 4
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=12

nvcc -V
echo begin
#python -m simtk.testInstallation
python setconfigfile.py --np 48 python restartREMD.py -debug
echo mpibegin
mpiexec.hydra -f hostfile -configfile configfile
echo allend
####srun -n $SLURM_NTASKS python mysim.py >runrettwocg.log 2>&1
