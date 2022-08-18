#!/bin/sh
#SBATCH -J REMD
#SBATCH -p gpu
#SBATCH -N 4
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=12

nvcc -V
echo begin
python setconfigfile.py --np 48 python testREMD.py -debug
echo mpibegin
mpiexec.hydra -f hostfile -configfile configfile
echo allend

