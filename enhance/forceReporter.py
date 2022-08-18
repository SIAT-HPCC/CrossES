from simtk.unit import *
from simtk.openmm import CustomExternalForce

class ForceChangeReporter(object):
    def __init__(self, force,  mov_list, speed,  max_pos, reportInterval=100):
        if not isinstance(force, CustomExternalForce):
            raise TypeError("%s is not an CustomExternalForce" % force)
        self.force = force
        self._reportInterval = reportInterval
        self._out = None
        self.speed = speed
        self.max_pos = max_pos
        self.mov_list = mov_list
        self.pre_pos = []

    def describeNextReport(self, simulation):
        steps = self._reportInterval - simulation.currentStep%self._reportInterval

        return (steps, False, False, True, False, None)

    def report(self, simulation, state):
        #print(self.pos)
        if self.speed == 0:
            return
        if len(self.pre_pos) == 0: # first use
            init_pos = simulation.context.getState(getPositions=True).getPositions()
            for idx, i in enumerate(self.mov_list):
                self.pre_pos.append(init_pos[i-1].x)
        v_unit = simulation.context.getState(getVelocities=True).getVelocities().unit
        speed = quantity.Quantity(self.speed, v_unit)

        for idx, i in enumerate(self.mov_list):  # system.getNumParticles()修改为指定原子idxlist
            pos = self.pre_pos[idx] + (speed * (self._reportInterval * simulation.integrator.getStepSize()))._value #nm
            self.pre_pos[idx] = pos
            if pos <= self.max_pos:
                self.speed = 0
                break
            self.force.setParticleParameters(idx, i, [pos])
        if self.speed != 0:
            self.force.updateParametersInContext(simulation.context)

