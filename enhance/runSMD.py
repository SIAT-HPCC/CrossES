from sys import stdout
import argparse
from simtk.unit import *
from simtk.openmm import *
from simtk.openmm.app import *
from smdforce import SMDForce
from tool.readconfig import read_txt

plat = Platform.getPlatformByName('CUDA')
prop = {'Precision': 'single'}

def smd(input_file, particle_file, n_step=1000, k_stay=1.0, k_mov=1.0,speed=-0.02, constant_force=False,output_file='output-smd.pdb'):

    pdb = PDBFile(input_file)
    forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
            nonbondedCutoff=1*nanometer, constraints=HBonds)
    integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
    all_list = read_txt(particle_file)
    stay_list = all_list[0] #[i for i in range(1, 61)]
    mov_list =  all_list[1] #[i for i in range(501, 561)]
    constant_force = constant_force
    con_force = SMDForce(pdb.positions, stay_list, mov_list, k_stay, k_mov, constant_force)
    con_force.add_force_system(system)
    simulation = Simulation(pdb.topology, system, integrator, plat, prop)
    simulation.context.setPositions(pdb.positions)
    max_pos = 0.0 # box x min
    speed = speed
    con_force.chang_constantV(simulation=simulation, speed=speed, max_pos=max_pos)
    simulation.minimizeEnergy()
    simulation.reporters.append(PDBReporter(output_file, 1000))
    simulation.reporters.append(StateDataReporter(stdout, 1000, step=True,
            potentialEnergy=True, temperature=True))

    simulation.step(n_step)

def main():
    arg = argparse.ArgumentParser()
    arg.add_argument('-f', '--input',  dest="input_file", default='./input/smd_i.pdb')
    arg.add_argument('-pf', '--particlefile', dest="particle_file", default='./input/particle.txt')
    arg.add_argument('-n', '--n_step', dest='n_step', type=int, default=500000)
    arg.add_argument('-ks', '--k_stay', dest='k_stay', type=float, default=1.0)
    arg.add_argument('-km', '--k_mov', dest='k_mov', type=float, default=1.0)
    arg.add_argument('-v', '--speed', dest='speed', type=float, default=-0.02)
    arg.add_argument('-cf', '--constant_force', dest='constant_force', type=bool, default=0)
    arg.add_argument('-o', '--output', dest='output_file', default='output_smd.pdb')
    arg = arg.parse_args()
    pram = arg.__dict__
    smd(**pram)

if __name__ == '__main__':
    main()

