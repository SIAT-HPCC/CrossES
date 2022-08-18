from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from simtk.unit.constants import BOLTZMANN_CONSTANT_kB, AVOGADRO_CONSTANT_NA
from mpi4py import MPI
import numpy as np
import math
import logging
import mpilib.mpiplus as mp
import sys
import os
class ReplicaExchange(object):
    """

    Parameters
    ----------
    n_iterations :
    replica_mixing_scheme:


    """

    def __init__(self, this_simulation, n_replica = 2, exchange_interval = 1000, replica_file = "replica.out",comm = MPI.COMM_WORLD):

        assert n_replica % 2 == 0, "Number of replicas must be divisible by 2!"
        self.n_replica = n_replica

        self.comm = comm
        self.exchange_interval = exchange_interval
        self.simulation = this_simulation
        self.restart = False
        self.restartpre = False
        self.replica_file = replica_file
        self.itera = 0
        if len(sys.argv) >= 2:
            logging.basicConfig(format='DEBUG[Python]: %(process)d-%(message)s ', filename='debug.log', level=logging.DEBUG)
        else:
            logging.basicConfig(format='INFO:%(process)d- %(message)s', level=logging.INFO)
        #getlog
        self.logger = logging.getLogger()


    # get init master
    def _get_master_parameter(self, ex_schemes):
        ex_kind = 1
        md_kind = 1
        if ex_schemes == "swap-neighbors":
            ex_kind = 1
        return ex_kind, md_kind

    def run(self, replica_parameters, n_iterations = 1, restart = False, ex_schemes = "swap-neighbors"):

        rank = self.comm.Get_rank()
        size = self.comm.Get_size()
        assert size == self.n_replica  , "The number of process must equal number of replica !"
        if restart:
            self.restart = True
        
            
        #init gromacs md.log
        if rank == 0 :
           gromacs_mdlog_mode= 'r+' if self.restart else 'w'
           gromacs_mdlog_file = open("md.log", gromacs_mdlog_mode)
           if self.restart != 0 :
              gromacs_mdlog_file.write("Replica exchange interval: " + str(n_iterations) + "\n")
              gromacs_mdlog_file.close()
        #read information in replica.out file
        paramlist, replica_file , start_iterations= self._init_paramlist_file(rank, size)

        idx = paramlist[rank]
        pre_param_idx = idx
        extime = 0
        self.logger.debug("rank %d, idx is %d, start_iteration=%d"%(rank, idx, start_iterations))

        for itera in range(start_iterations, n_iterations):

            #save gromacs md.log
            if rank == 0 :
               gromacs_mdlog_file = open('md.log', 'a')
               gromacs_mdlog_file.write("Replica exchange at step " + str(self.exchange_interval * (itera + 1 )) + "  time " + str(self.exchange_interval * (itera + 1) * 2 / 1000)+ "\n")
               gromacs_mdlog_file.flush()

            # step 1:init_parameter
            #print("rank %d in range(%d) get param %d" % (rank, itera, idx))
            self.setParameters(self.simulation, replica_parameters, idx)
            # setp 2: md
            self.simulation.step(self.exchange_interval)

            # step 3:exchange
            state = self._get_state_to_master(replica_parameters, idx)
            ex_kind, md_kind = self._get_master_parameter(ex_schemes)
            # call
            idx = mp.getExchange_func(self.comm, itera, state, paramlist, ex_kind, md_kind)
            #print("rank %d in range(%d) send %f  recv new idx = %d!!" % (rank, itera, state[0], idx))

             # step 4: rescale
            if pre_param_idx != idx:
                extime += 1
                self.rescaleVelocities(replica_parameters, idx)
            pre_param_idx = idx

            #step 5: save tmp
            self.saveRestartfile(rank, itera)

            if rank == 0 and itera + 1 != n_iterations :
               self._write_paramlist_file(replica_file, paramlist, itera+1)

            
            

        #save
        #self.logger.info("The exchange proportion of replia %d is %f !"%(rank, 1.0 * extime/n_iterations))

    def getRestartfile(self, rank, nowitera):
        filename = 'checkPoint' + str(rank) + '.' + str(nowitera)
        exists = os.path.isfile(filename)
        assert exists, "Checkpoint file not exist!"
        self.simulation.loadCheckpoint(filename)
        if rank == 0:
            restartlog = open('restart.log', 'a')
            restartlog.write(str(nowitera) + "\n")
            restartlog.flush()
            self.logger.debug("write restartlog  beginwith %d"%(nowitera) )
        self.logger.debug("Load checkPoint %s" % str(filename))

    def saveRestartfile(self, rank, itera):
        import os
        new_file = 'checkPoint' + str(rank) + '.' + str(itera)  # change checkpoint to precheckpoint
        # save now
        self.simulation.saveCheckpoint(new_file)
        self.logger.debug("save checkPoint %s" % str(new_file))
        pre_file = 'checkPoint' + str(rank) + '.' + str(itera - 2) # pre checkpoint delete
        if os.path.exists(pre_file):  # if exists
            # delete
            os.remove(pre_file)  #
            self.logger.debug("delete checkPoint %s" % str(pre_file))

   
    def _get_state_to_master(self, replica_parameters, idx):
        potential_energy = self.simulation.context.getState(getEnergy=True).getPotentialEnergy()
        temp = self._get_temper_in_param(replica_parameters, idx)
        state = np.arange(2).astype(float)
        state[0] = potential_energy._value
        state[1] = temp._value
        #print("state is potentinal_energy is %f , T = %f" % (state[0], state[1]))
        return state

    def rescaleVelocities(self, replica_param,  newidx):
        #Calculate percentage
        Tnew = self._get_temper_in_param(replica_param, newidx)._value#replica_param[AndersenThermostat.Temperature()][newidx]
        Told = self.calculateTemperature()
        p = sqrt(Tnew/Told)
        #print("rescale p is %f"% p )
        # Rescale velocitiess
        self.itera += 1
        if self.comm.Get_rank() == 0:
            self.logger.debug(" [%d] :Tnew = %f ,Told = %frank0\n" % (self.itera, Tnew, Told))
        velocities = self.simulation.context.getState(getVelocities=True).getVelocities(asNumpy=True)
        self.simulation.context.setVelocities(p * velocities)

    def setParameters(self, simulation, parameters, which):

        for param_name in parameters:
            if callable(param_name):
                param_name(parameters[param_name])
            else:
                simulation.context.setParameter(param_name, parameters[param_name][which])

    def _init_paramlist_file(self, rank, size):
        replica_file_mode = 'r+' if self.restart else 'w'
        replica_file = open(self.replica_file, replica_file_mode)
        start_interations = 0
        # paramlist
        if self.restart:
            self.logger.info("Now is restart !!!!")
            all_line = replica_file.readlines()
            last_line = all_line[-1]
            splitline = last_line.split(":")
            start_interations = int(splitline[0].strip())  #get new start interation
            paramlist = np.array([int(e.strip()) for e in splitline[1].split(",")], dtype = np.int) #get new paramlist
            #judge whether all progress save the checkpoint
            if start_interations !=0 :
                for i in range(size):
                    filename = 'checkPoint' + str(i) + '.' + str(start_interations - 1)
                    exists = os.path.isfile(filename)
                    if not exists:     #must exists
                        if start_interations == 1:
                            start_interations = 0
                            paramlist = np.arange(self.n_replica).astype(int)
                        else:
                            start_interations = start_interations - 1
                            last_line = all_line[-2]
                            splitline = last_line.split(":")
                            paramlist = np.array([int(e.strip()) for e in splitline[1].split(",")], dtype=np.int)
                            self.logger.debug("2 last_line is %s"%str(last_line))
                            #1  2  1 error
                            self.restartpre = True
                        break

            self.getRestartfile(rank, start_interations - 1)

           # Do nothing for exchange file
        else:
            restartlog = open('restart.log', 'w')
            # Initially, each replica just has its corresponding
            # parameter set.
            paramlist = np.arange(self.n_replica).astype(int)
            # Write headers
            replica_file.write("Iteration, "+", ".join(["Replica %i" % i for i in range(self.n_replica)]) + "\n")
            replica_file.write("0: "+", ".join([str(i) for i in range(self.n_replica)]) + "\n")
            #replica_file.write("-0: "+", ".join(["Replica %i" % i for i in range(self.n_replica)]) + "\n")
            replica_file.flush()
        return paramlist, replica_file, start_interations

    def _write_paramlist_file(self,replica_file, paramlist , itera):
        if self.restartpre:
            self.restartpre = False
            self.logger.debug("rewrite paramlist!")
            return
        replica_file.write("%d: "%(itera) + ", ".join([str(e) for e in paramlist]) + "\n")
        replica_file.flush()
        

    @staticmethod
    def create_replica_paramlist(n_replicas, templist = None):

        replicas = {
            AndersenThermostat.Temperature(): [ _ * kelvin for _ in templist],
            # PairDistanceCouplingForce.Lambda : np.linspace(0.1, 0.0, n_replicas),
            # PairDistanceCouplingForce.Lambda : [  0.1, 0.05, 0.01, 0, 0,   0.01, 0.05, 0.1 ]
        }
        return replicas

    def _get_temper_in_param(self, replica_param, idx):
        T = replica_param[AndersenThermostat.Temperature()][idx]
        return T

    def calculateTemperature(self):
        import simtk.openmm as mm
        import simtk.unit as unit
        system = self.simulation.context.getSystem()
        state = self.simulation.context.getState(getEnergy=True)
        dof = 0
        for i in range(system.getNumParticles()):
            if system.getParticleMass(i) > 0 * unit.dalton:
                dof += 3
        dof -= system.getNumConstraints()
        if any(type(system.getForce(i)) == mm.CMMotionRemover for i in range(system.getNumForces())):
            dof -= 3
        temper = (2 * state.getKineticEnergy() / (dof * unit.MOLAR_GAS_CONSTANT_R)).value_in_unit(unit.kelvin)
        return temper


