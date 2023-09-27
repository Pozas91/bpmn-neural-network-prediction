import os
from pathlib import Path


def create_file(i: int):
    # Get path
    path = Path(os.path.dirname(os.path.abspath(__file__)))

    # Read stub
    file = open(path.joinpath('visa.stub'), 'r')
    content = file.read()
    file.close()

    # Generate self file path
    trace_file = f'./trace-{i}.csv'

    # Generate output file path
    output_file = f'bpmn-run-visa-{i}'
    output_file = str(path.parent.joinpath('traces').joinpath(output_file + '.maude'))

    # Replace information in content
    content = content.replace('<self-file>', trace_file)

    # Get file to write
    fw = open(output_file, 'w')
    fw.write(content)
    fw.close()


def main():
    for i in range(1, 500 + 1):
        # Create file
        create_file(i)


if __name__ == '__main__':
    main()

# for ((i = 1; i <= 500; i++)); do ~/maude/maude.linux64 -random-seed=$i -trust visa/traces/bpmn-run-visa-$i.maude; done
