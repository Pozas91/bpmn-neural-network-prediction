import os
import subprocess
from datetime import datetime
from sys import stdin

MAUDE_SUFFIX = '.maude'
UNCLEAN_SUFFIX = '.unclean'
CLEAN_SUFFIX = '.clean'
SUMMARY_EXT = 'summary'
HEADER_NAME = 'header'
SUMMARY_NAME = 'all_results.txt'


def create_filename_template(header):
    ans, first = [], True
    for x in header:
        ans.append('{' if first else '-{')
        first = False
        ans.append(x)
        ans.append('}')
    return ''.join(ans)


def load_file(name):
    ans = list()
    f = open('{0}.premaude'.format(name), 'r')
    for x in f: ans.append(x)
    return ''.join(ans)


def save_file(name, s, extra):
    f = open(name, 'w')
    f.write(s)
    if len(extra) != 0: f.write(extra)
    f.close()


def main():
    header = [x for x in stdin.readline().split()]
    # print(header, len(header))
    fnt = create_filename_template(header)
    line = stdin.readline()
    exp_prefix = None
    exp_cnt = 0
    while len(line) != 0:
        print('Running experiment {0}'.format(exp_cnt), "current time =", datetime.now().strftime("%H:%M:%S"))
        d = dict()
        tok = line.split()
        for i in range(len(header)): d[header[i]] = tok[i]
        file_name = fnt.format(**d)
        print('    experiment identifier: {0}'.format(file_name))
        maude_name, unclean_name, clean_name = file_name + MAUDE_SUFFIX, file_name + UNCLEAN_SUFFIX, file_name + CLEAN_SUFFIX
        # generate maude specification
        print('    instantiating the Maude template: ', end='')
        d['EEXXPPIIDD'] = file_name
        save_file(maude_name, load_file(tok[0] + '-' + tok[1]).format(**d), '\nerew { complete initState } .\nq')
        print('OK')
        # execute the maude specification and save the unclean output
        print('    executing the Maude specification: ', end='')
        result = subprocess.run(['maude', maude_name], capture_output=True, text=True)
        save_file(unclean_name, result.stdout, '')
        print('OK')
        # generate clean output from the unclean one
        print('    cleaning the output: ', end='')
        with open(unclean_name, 'r') as unclean_file:
            result = subprocess.run(['python3', 'unclean2clean.py'], stdin=unclean_file, capture_output=True, text=True)
            save_file(clean_name, result.stdout, '')
            print('OK')
        # generate plots from the clean output
        print('    generating the plots: ', end='')
        with open(clean_name, 'r') as clean_file:
            result = subprocess.run(['python3', 'clean2plot.py'], stdin=clean_file)
            print('OK')
        line, exp_cnt = stdin.readline(), exp_cnt + 1
    # generate summary of all experiments
    print('\nGenerating summary file: '.format(exp_cnt), end='')
    os.system('cat {0} *.{1} > {2}'.format(HEADER_NAME, SUMMARY_EXT, SUMMARY_NAME))  # ; rm {0}
    # with open(SUMMARY_NAME, 'w') as summary_file:
    #   result = subprocess.run(['cat','*.summary' ], capture_output=True, text=True)
    #   summary_file.write(result.stdout)
    #   summary_file.close()
    print('OK')
    print('\nTotal number of experiments: {0}'.format(exp_cnt))


if __name__ == '__main__':
    main()
