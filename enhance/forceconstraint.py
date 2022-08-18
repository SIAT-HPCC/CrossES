

from simtk.openmm import CustomExternalForce

class ForceConstraint(object):
    def __init__(self):
        self.force_list = []
        self.add_force()

    def add_force(self):
        force = CustomExternalForce("k*(x-x0)")
        force.addGlobalParameter("x0", 0)
        force.addGlobalParameter("k", 1.0)
        self.force_list.append(force)

    def add_force_system(self, system):
        # add all force to  system
        # this op must before simulation build
        for f in self.force_list:
            system.addForce(f)