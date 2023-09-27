from sys import stdin

import matplotlib.pyplot as plt

SOURCE = None
FIGPRE1 = 'type1'
FIGPRE2 = 'type2'
COSTSSUF = 'costs'
HEADER_NAME = 'header'
SUMMARY_EXT = 'summary'


def mklist(pcnt):
    t1, s1 = list(), list()
    tok0 = stdin.readline().split()
    t1.append(float(tok0[0]))
    s1.append(float(tok0[1]))
    for i in range(pcnt - 1):
        tok1 = stdin.readline().split()
        t1.append(float(tok1[0]) - 0.0001)
        s1.append(float(tok0[1]) - 0.0001)
        t1.append(float(tok1[0]))
        s1.append(float(tok1[1]))
        tok0 = tok1
    return t1, s1, float(tok1[0]), float(tok1[1])


def main():
    FILEPRE = stdin.readline().strip()
    COSTS = stdin.readline().split()
    resource_cnt = int(stdin.readline())
    names = dict()
    for rcnt in range(resource_cnt):
        v = stdin.readline()
        if True:
            # if len(v.strip())!=0:
            name, p1cnt, p2cnt, p3cnt, p4cnt, p5cnt = v.split()
            p1cnt, p2cnt, p3cnt, p4cnt, p5cnt = int(p1cnt), int(p2cnt), int(p3cnt), int(p4cnt), float(p5cnt)
            t1, s1, l1, v1 = mklist(p1cnt)
            t2, s2, l2, v2 = mklist(p2cnt)
            t3, s3, l3, v3 = mklist(p3cnt)
            t4, s4, l4, v4 = mklist(p4cnt)
            names[name] = p5cnt
            t1.append(l1)
            s1.append(v1)
            t2.append(l2)
            s2.append(v2)
            t3.append(l3)
            s3.append(v3)
            t4.append(l4)
            s4.append(v4)
            fig, ax = plt.subplots()
            ax.plot(t1, s1)
            ax.set_ylabel(name)
            ax.set_xlabel('time')
            ax.grid(True)
            # ax.axis([0, 2100, 0, 10])
            fig2, usages = plt.subplots()
            usages.plot(t4, s4)
            usages.set_ylabel(name)
            usages.set_xlabel('time')
            usages.grid(True)
            # usages.axis([0, 2100, 0, 150])
            fig.savefig('{0}-{1}-{2}'.format(FILEPRE, name, FIGPRE1))
            fig2.savefig('{0}-{1}-{2}'.format(FILEPRE, name, FIGPRE2))
    f = open('{0}-{1}.{2}'.format(FILEPRE, COSTSSUF, SUMMARY_EXT), 'w')
    f.write('{0}\t{1:.5f}\t{2:.5f}\t{3:.5f}'.format(FILEPRE, float(COSTS[0]), float(COSTS[1]), float(COSTS[2])))
    for k in names: f.write('\t{0:.5f}'.format(names[k]))
    f.write('\n')
    f = open('{0}'.format(HEADER_NAME), 'w')
    f.write('AVGEXECT\tVAREXECT\tTOTALCOST')
    for k in names: f.write('\t{0}'.format(k))
    f.write('\n')
    f.close()


if __name__ == '__main__':
    main()
