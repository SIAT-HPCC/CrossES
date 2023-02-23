

from simtk.openmm import *
from forceReporter import ForceChangeReporter
from forceconstraint import ForceConstraint
class SMDForce(ForceConstraint):
    def __init__(self, positions, stay_list, mov_list, k_stay=1.0, k_mov=1.0, constant_force=True):
        #super(SMDForce,self).__init__()
        self.force_list = []
        self.simulation = None
        self.positions = positions
        self.stay_list = stay_list
        self.mov_list = mov_list
        self.k_stay = k_stay
        self.k_mov = k_mov
        self.constant_force = constant_force
        self.add_force()

    def add_force(self):

        #positions = self.simulation.getState(getPositions=True).getPositions()
        positions = self.positions
        force_stay = CustomExternalForce("k*periodicdistance(x, y, z, x0, y0, z0)^2")
        force_stay.addGlobalParameter("k", self.k_stay);
        force_stay.addPerParticleParameter("x0");
        force_stay.addPerParticleParameter("y0");
        force_stay.addPerParticleParameter("z0");
        for i in self.stay_list:
            force_stay.addParticle(i, [positions[i - 1][0], positions[i - 1][1], positions[i - 1][2]])
        self.force_list.append(force_stay)

        #force_mov = CustomExternalForce("k*(x-x0)^2")
        if self.constant_force:
            force_mov = CustomExternalForce("k*(x-x0)")
            print(" con force")
            force_mov.addGlobalParameter("x0", 0)  #
            force_mov.addGlobalParameter("k", self.k_mov)  #
            for i in self.mov_list:  # add Particle
                force_mov.addParticle(i, [])  # add atom
        else:
            force_mov = CustomExternalForce("k*(x-x0)^2")
            force_mov.addPerParticleParameter("x0")  #

            for i in self.mov_list:
                force_mov.addParticle(i, [positions[i - 1][0]._value])  #add init pos
            force_mov.addGlobalParameter("k", self.k_mov)  #add Particle
        self.force_list.append(force_mov)


    def chang_constantV(self, simulation, speed=0.005, max_pos=0.0):
        if self.constant_force:
            speed = 0
        simulation.reporters.append(ForceChangeReporter(self.force_list[1], self.mov_list, speed, max_pos, 100))