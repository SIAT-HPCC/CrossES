
def read_txt(file):
    pair_list = []
    word = open(file, 'r').readlines()
    slist = word[0].split(',')
    slist = [int(i) for i in slist]
    mlist = word[1].split(',')
    mlist = [int(i) for i in mlist]

    pair_list.append(slist)
    pair_list.append(mlist)
    return pair_list

def write_txt(file, word):
    with open(file, 'w', encoding='utf-8') as file1:
        for w in word:
            print(w,file=file1)

def read_ndx(file, pair_num, group_id):
    pair_list = []
    now = -1
    for line in open(file, 'r'):
        if line[0] == '[':
            now += 1
            if now > group_id:
                break
            continue
        if now == group_id:
            values = [int(s) for s in line.split()]
            for i in range(0, len(values), pair_num):
                pair = values[i: i+pair_num]
                pair_list.append(pair)
    return pair_list


def read_xvg(file):
    numbs = []
    for line in open(file, 'r'):
        if line[0] == '#' or line[0] == '@':
            continue
        values = [float(s) for s in line.split()]
        numbs = values[2:]
       # print(len(values))
    return numbs


def get_angel(file_ndx, file_xvg):
    angle_list = read_ndx(file_ndx, 3, 1)

    angle_num = read_xvg(file_xvg)
    for i in range(len(angle_list)):
        angle_list[i].append(angle_num[i])
    return angle_list


def get_dihedral(file_ndx, file_xvg):
    dihedral_list = read_ndx(file_ndx, 4, 0)
    dihedral_num = read_xvg(file_xvg)
    for i in range(len(dihedral_list)):
        dihedral_list[i].append(dihedral_num[i])
    # print(dihedral_list[0])
    return dihedral_list

# angle_list, angle_num = get_angel("../input/angle.ndx", "../input/angle.xvg")
# print(angle_list)
# print(angle_num)
#dihedral_list = get_dihedral("../input/dihedral.ndx", "../input/dihedral.xvg")
#print(dihedral_list)
# print(dihedral_num)
#read_txt('../input/particle.txt')
