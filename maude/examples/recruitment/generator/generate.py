import os
from pathlib import Path


def create_file(hr: int, assistant: int, technical_staff: int):
    # Get path
    path = Path(os.path.dirname(os.path.abspath(__file__)))

    # Read stub
    file = open(path.joinpath('recruitment.stub'), 'r')
    content = file.read()
    file.close()

    # Generate self file path
    trace_file = f'./trace-{hr}-{assistant}-{technical_staff}.csv'

    # Generate output file path
    output_file = f'bpmn-run-recruitment-{hr}-{assistant}-{technical_staff}'
    output_file = str(path.parent.joinpath('traces').joinpath(output_file + '.maude'))

    # Replace information in content
    content = content.replace('<self-file>', trace_file)
    content = content.replace('<max-hr>', str(hr))
    content = content.replace('<max-assistant>', str(assistant))
    content = content.replace('<max-technical-staff>', str(technical_staff))

    # Get file to write
    fw = open(output_file, 'w')
    fw.write(content)
    fw.close()


def main():
    for hr in range(5, 50 + 1, 5):
        for assistant in range(2, 20 + 1, 2):
            # Create file
            create_file(hr, assistant, technical_staff=2)


if __name__ == '__main__':
    main()

# for f in *.maude; do ~/maude/maude.linux64 -random-seed=1 -trust "$f"; done
