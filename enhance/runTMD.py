from sys import stdout
import argparse
from simtk.unit import *
from simtk.openmm.app import *
from tool.readconfig import *
from tmdforce import *

plat = Platform.getPlatformByName('CUDA')
prop = {'Precision': 'single'}

def tmd(input_file, output_file, target_path, n_step=10000,  k_angle=0.01, k_dihe=0.1):

    input_path = target_path
    pdb = PDBFile(input_file)
    forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
            nonbondedCutoff=1*nanometer, constraints=HBonds)
    integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
    angle_list = get_angel(input_path+"angle.ndx", input_path+"angle.xvg")
    dih_list = get_dihedral(input_path+"dihedral.ndx", input_path+"dihedral.xvg")
    con_force = TMDForce(angle_list, dih_list, k_angle, k_dihe)
    con_force.add_force_system(system)
    simulation = Simulation(pdb.topology, system, integrator, plat, prop)
    simulation.context.setPositions(pdb.positions)
    simulation.minimizeEnergy()
    simulation.reporters.append(PDBReporter(output_file, 5000))
    simulation.reporters.append(StateDataReporter(stdout, 5000, step=True,
            potentialEnergy=True, temperature=True))

    simulation.step(n_step)

def main():
    arg = argparse.ArgumentParser()
    arg.add_argument('-f', '--input',  dest="input_file", default='./input/tmd_i.pdb')
    arg.add_argument('-ta', '--target_path', dest="target_path", default='./input/')
    arg.add_argument('-n', '--n_step', dest='n_step', type=int, default=500000)
    arg.add_argument('-ka', '--k_angle', dest='k_angle', type=float, default=0.001)
    arg.add_argument('-kd', '--k_di', dest='k_dihe', type=float, default=1.0)
    arg.add_argument('-o', '--output', dest='output_file', default='output_tmd.pdb')
    arg = arg.parse_args()
    pram = arg.__dict__
    tmd(**pram)

if __name__ == '__main__':
    main()


