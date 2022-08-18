from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from enhance.replicaexchange import ReplicaExchange
from mpi4py import MPI
import logging
import sys
import os
import socket

# -- Get MPI --
comm =  MPI.COMM_WORLD
rank =  comm.Get_rank()
n_proc = comm.Get_size()
#logging.basicConfig(level = logging.DEBUG)
begintime = MPI.Wtime()
#output GPU and  host
device_index = os.environ.get("CUDA_VISIBLE_DEVICES")
nodename = socket.gethostname()

print("    !------!!! rank is %i, nodename = %s, idx = %s!!----- "%(rank, nodename, device_index))


restart_time = 1
n_replicas = n_proc
n_iterations = 20000
savelogstep = 5000
savepdbstep = 5000
ex_interval = 5000
input_path = "xxxx/include/"
include_path = "xxx/top"
_OUTPUT_PATH = "out/"
templist = [300.0, 303.07, 306.18, 309.33, 312.51, 315.73, 318.98, 322.28, 325.61, 328.97, 332.37, 335.81, 339.28, 342.79, 346.33, 349.91, 353.52, 357.17, 360.84, 364.55, 368.3, 372.07, 375.87, 379.71, 383.58, 387.47, 391.4, 395.35, 399.33, 403.34, 407.38, 411.44, 415.52, 419.64, 423.77, 427.93, 432.12, 436.32, 440.55, 444.8, 449.07, 453.36, 457.67, 462.0, 466.34, 470.71, 475.09, 479.49]

plat= Platform.getPlatformByName('CUDA')

prop = {'Precision': 'single'}
#prop = {'Precision': 'double'}
gro = GromacsGroFile(input_path+'init%d.gro'%(3 + rank%8))
top = GromacsTopFile(input_path+'fws_plus.top', periodicBoxVectors=gro.getPeriodicBoxVectors(),
        includeDir=include_path)
system = top.createSystem(nonbondedMethod=PME, nonbondedCutoff=1.2*nanometer,
        constraints=HBonds)
temp = templist[rank] * kelvin
integrator = VerletIntegrator(0.002*picoseconds)
tstat = AndersenThermostat(templist[rank], 1/picosecond)
system.addForce(tstat)

#integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
simulation = Simulation(top.topology, system, integrator, plat, prop)

simulation.context.setPositions(gro.positions)
simulation.context.setVelocitiesToTemperature(temp)
#simulation.minimizeEnergy()

simulation.reporters.append(PDBReporter('out/out%i-%i.pdb' % (comm.Get_rank(),restart_time), savepdbstep))
simulation.reporters.append(StateDataReporter('out/md%i-%i.log' % (comm.Get_rank(),restart_time), savelogstep, step=True, potentialEnergy=True, kineticEnergy = True, totalEnergy = True, temperature=True, speed = True))
print("now inint REMD")
remd = ReplicaExchange(this_simulation = simulation, n_replica= n_replicas, exchange_interval = ex_interval)
replicaslist = ReplicaExchange.create_replica_paramlist(n_replicas = n_replicas, templist = templist)
remd.run(replica_parameters=replicaslist, n_iterations = n_iterations, restart = True)
if rank == 0:
   time = MPI.Wtime()-begintime
   print("\n #-----  hhhh  all using time is %f  -----#\n "%(time))
print("all end!")


