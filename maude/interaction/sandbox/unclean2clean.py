from re import *
from sys import stdin

INPUT = None
RES_TOK = 'resource('
PATTERN = ('resource\('
           'id\((?P<resname>("\w+"))\),'
           '\s*(?P<minnum>\d+),'
           '\s*(?P<maxnum>\d+),'
           '\s*(?P<alloct>\d+),'
           '\s*(?P<totalnum>\d+),'
           '\s*(?P<totrep>(\(\s*\d\.\d+(e(\+|-)\d+)?\s*,\s*\d+\s*\)\s*)*),'
           '\s*(?P<resavl>(\d+)),'
           '\s*(?P<nbavl>(\(\s*\d\.\d+(e(\+|-)\d+)?\s*,\s*\d+\s*\)\s*)*),'
           '\s*(?P<idle>(\s*((idle)|(delayed\(idle,\s*\d+(/\d+)?\s*\))|(\(\s*((idle)|(delayed\(idle,\s*\d+(/\d+)?\s*\)))\s*(;\s*((idle)|(delayed\(idle,\s*\d+(/\d+)?\s*\)))\s*)*\)))\s*)),'
           '\s*(?P<queueinitsize>(\d+)),'
           '\s*(?P<queuesize>(\(\s*\d\.\d+(e(\+|-)\d+)?\s*,\s*\d+\s*\)\s*)*),'
           '\s*(?P<usages>(\(\s*\d\.\d+(e(\+|-)\d+)?\s*,\s*\d\.\d+(e(\+|-)?\d+)?\s*\)\s*)*),'
           '\s*(?P<timer>\d+(/\d+)?\s*),'
           '\s*(?P<timeinuse>\d+(/\d+)\s*)\s*\)')

EXP_ID_TOK = 'ExperimentId('
AET_TOK = 'average execution time : '
VET_TOK = 'variance execution time : '
TC_TOK = 'total cost : '
RES_US_TOK = 'resource usage :'


def read_input():
    global INPUT
    tmp = [x.strip() for x in stdin.readlines()]
    INPUT = list()
    for x in tmp:
        INPUT.append(x)
        if x[-1] == ')':
            INPUT.append(' ')
    INPUT = ''.join(INPUT)


def read_file(file_path):
    global INPUT
    INPUT = []

    with open(file_path, 'r') as f:
        for line in f.readlines():
            INPUT.append(line.strip())
            if line == ')':
                INPUT.append(' ')

    INPUT = ''.join(INPUT)


def extract_header_alt(s):
    ans = list()
    idx, i, ok, tmp = INPUT.find(AET_TOK) + len(AET_TOK), 0, True, list()
    while ok:
        tmp.append(INPUT[idx + i])
        ok, i = INPUT[idx + i + 1] in '0123456789.+-e', i + 1
    ans.append(''.join(tmp))
    idx, i, ok, tmp = INPUT.find(VET_TOK) + len(VET_TOK), 0, True, list()
    while ok:
        tmp.append(INPUT[idx + i])
        ok, i = INPUT[idx + i + 1] in '0123456789.+-e', i + 1
    ans.append(''.join(tmp))
    idx, i, ok, tmp = INPUT.find(TC_TOK) + len(TC_TOK), 0, True, list()
    while ok:
        tmp.append(INPUT[idx + i])
        ok, i = INPUT[idx + i + 1] in '0123456789.+-e', i + 1
    ans.append(''.join(tmp))
    return ans


def extract_header(s):
    ans = list()
    idx, i = INPUT.find(EXP_ID_TOK) + len(EXP_ID_TOK), 0
    # process experiment id
    while INPUT[idx + i] != ')': i = i + 1
    ans.append(INPUT[idx:idx + i])
    idx, i, ok, tmp = INPUT.find(AET_TOK) + len(AET_TOK), 0, True, list()
    while ok:
        tmp.append(INPUT[idx + i])
        ok, i = INPUT[idx + i + 1] in '0123456789.+-e', i + 1
    ans.append(''.join(tmp))
    idx, i, ok, tmp = INPUT.find(VET_TOK) + len(VET_TOK), 0, True, list()
    while ok:
        tmp.append(INPUT[idx + i])
        ok, i = INPUT[idx + i + 1] in '0123456789.+-e', i + 1
    ans.append(''.join(tmp))
    idx, i, ok, tmp = INPUT.find(TC_TOK) + len(TC_TOK), 0, True, list()
    while ok:
        tmp.append(INPUT[idx + i])
        ok, i = INPUT[idx + i + 1] in '0123456789.+-e', i + 1
    ans.append(''.join(tmp))
    return ans


def extract_resource_usage(s):
    ans = dict()
    low = s.find(RES_US_TOK) + len(RES_US_TOK)
    hi = s[low:].find(RES_US_TOK)
    toparse = s[low:low + hi].split(',')
    for x in toparse:
        l, r = x.split('|->');
        l, r = l.strip(), r.strip()
        name = l[4:-2]
        ans[name] = r
    return ans


def find_resource_str(s):
    ans, tmp = list(), list()
    i = 0
    while i != -1:
        i = s.find(RES_TOK, i + 1)
        if i != -1: tmp.append(i)
    tmp.append(len(INPUT))
    for i in range(1, len(tmp)):
        ans.append(s[tmp[i - 1]:tmp[i]])
    return ans


def process_pair_list(s):
    ans = list()
    for x in s.split():
        pair = x.split(',')
        ans.append((pair[0][1:], pair[1][:-1]))
    return ans


def parse_resource(s):
    ans = list()
    for match in finditer(PATTERN, s):
        res = list()
        res.append(match.group('resname')[1:-1])
        res.append(process_pair_list(match.group('totrep')))
        res.append(process_pair_list(match.group('nbavl')))
        res.append(process_pair_list(match.group('queuesize')))
        res.append(process_pair_list(match.group('usages')))
        ans.append(res)
    return ans


def main():
    read_input()
    header = extract_header(INPUT)

    print(header[0])
    print(' '.join(header[1:]))
    res_usage = extract_resource_usage(INPUT)
    res = find_resource_str(INPUT)
    print(len(res))
    for s in res:
        for n, l1, l2, l3, l4 in parse_resource(s):
            print('{0} {1} {2} {3} {4} {5}'.format(n, len(l1), len(l2), len(l3), len(l4), res_usage[n]))
            print('\n'.join('{0} {1}'.format(x, y) for x, y in l1))
            print('\n'.join('{0} {1}'.format(x, y) for x, y in l2))
            print('\n'.join('{0} {1}'.format(x, y) for x, y in l3))
            print('\n'.join('{0} {1}'.format(x, y) for x, y in l4))


def main_alt():
    from utils.paths import OUTPUTS_PATH

    file_name = 'predictive-ml-usage-5-25-20'
    file_in_path = OUTPUTS_PATH.joinpath(f'{file_name}.unclean')
    file_out_path = OUTPUTS_PATH.joinpath(f'{file_name}.clean')

    read_file(file_in_path)
    header = extract_header_alt(INPUT)

    with open(file_out_path, 'w') as f:
        # Write header
        f.write(file_name + '\n')

        # Write resources usage
        f.write(' '.join(header) + '\n')

        res_usage = extract_resource_usage(INPUT)
        res = find_resource_str(INPUT)

        # Write number of resources
        f.write(str(len(res)) + '\n')

        for s in res:
            for n, l1, l2, l3, l4 in parse_resource(s):
                f.write(f'{n} {len(l1)} {len(l2)} {len(l3)} {len(l4)} {res_usage[n]} \n')
                f.write('\n'.join('{0} {1}'.format(x, y) for x, y in l1))
                f.write('\n'.join('{0} {1}'.format(x, y) for x, y in l2))
                f.write('\n'.join('{0} {1}'.format(x, y) for x, y in l3))
                f.write('\n'.join('{0} {1}'.format(x, y) for x, y in l4))


if __name__ == '__main__':
    main()
