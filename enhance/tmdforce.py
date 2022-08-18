

from simtk.openmm import *
from forceReporter import ForceChangeReporter
from forceconstraint import ForceConstraint
class TMDForce(ForceConstraint):
    def __init__(self, angle_list, dihedral_list, k_angle=0.001, k_dihe=1.0):
        #super(TMDForce,self).__init__()
        self.force_list = []
        self.simulation = None
        self.angle_list = angle_list
        self.dihedral_list = dihedral_list
        self.k_angle = k_angle
        self.k_dihe = k_dihe
        self.add_force()

    def add_force(self):
        force_angle = CustomAngleForce("k*(theta-theta0)^2")
        force_angle.addGlobalParameter("k", self.k_angle )
        force_angle.addPerAngleParameter("theta0")

        for i in range(len(self.angle_list)):  # 修改为指定原子idxlist
            force_angle.addAngle(self.angle_list[i][0], self.angle_list[i][1], self.angle_list[i][2], [self.angle_list[i][3]])  # 为力增加原子
        self.force_list.append(force_angle)
        force_dihedral = CustomCompoundBondForce(4,
                                                 "k*(theta1-theta0)^2;" "theta1=pointdihedral(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4);")
        # force_dihedral.setPermutationMode(CustomManyParticleForce.UniqueCentralParticle)
        force_dihedral.addGlobalParameter("k",self.k_dihe)
        force_dihedral.addPerBondParameter("theta0")

        for i in range(len(self.dihedral_list)):  # system.getNumParticles()修改为指定原子idxlist
            force_dihedral.addBond(self.dihedral_list[i][:4], [self.dihedral_list[i][4]])  # 为力增加原子
        self.force_list.append(force_dihedral)

