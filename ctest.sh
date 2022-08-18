#!/bin/sh
#SBATCH -J Testmpi
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --gres=gpu:1


echo begin
python setconfigfile.py --np 4 python testmpi.py
echo mpibegin
mpiexec.hydra -f hostfile -configfile configfile
echo endall
