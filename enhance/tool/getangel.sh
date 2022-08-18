gmx grompp -f md.mdp -c input.pdb -p input.top -o md.tpr
gmx mk_angndx -s md.tpr -n angle.ndx
gmx mk_angndx -s md.tpr -n dihedral.ndx -type dihedral
gmx angle -f input.pdb  -n angle.ndx  -all -ov angle.xvg
gmx angle -f input.pdb  -n dihedral.ndx  -all -ov dihedral.xvg


gmx mk_angndx -s npt-pr.tpr -n angle.ndx
gmx mk_angndx -s  npt-pr.tpr -n dihedral.ndx -type dihedral
gmx angle -f npt-pr.gro  -n angle.ndx  -all -ov angle.xvg
gmx angle -f npt-pr.gro  -n dihedral.ndx  -all -ov dihedral.xvg
