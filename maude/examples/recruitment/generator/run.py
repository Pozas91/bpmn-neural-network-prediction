import os
import shutil
from os.path import isfile
from pathlib import Path


def main():
    # Get path
    path = Path(os.path.dirname(os.path.abspath(__file__))).parent.joinpath('traces')

    # Get traces
    traces_file = [f for f in os.listdir(path) if isfile(path.joinpath(f))]

    # Filter traces
    traces_file = filter(lambda f: 'trace' in f and '-trace' not in f, traces_file)

    for file in traces_file:
        shutil.move(path.joinpath(str(file)), path.joinpath(f'4-{file}'))


if __name__ == '__main__':
    main()
