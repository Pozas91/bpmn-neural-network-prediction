import os
from pathlib import Path


def create_file(instances: list):
    # Get path
    path = Path(os.path.dirname(os.path.abspath(__file__)))

    # Read stub
    file = open(path.joinpath('delivery.stub'), 'r')
    content = file.read()
    file.close()

    # Generate trace file path
    trace_file = './trace-'
    trace_file += '-'.join(str(i) for i in instances)
    trace_file += '.csv'

    # Generate output file path
    output_file = 'bpmn-run-delivery-'
    output_file += '-'.join(str(i) for i in instances)
    output_file = str(path.parent.joinpath('traces').joinpath(output_file + '.maude'))

    # Replace information in content
    content = content.replace('<trace-file>', trace_file)
    content = content.replace('<clerk>', str(instances[0]))
    content = content.replace('<worker>', str(instances[1]))
    content = content.replace('<courier>', str(instances[2]))
    content = content.replace('<car>', str(instances[3]))
    content = content.replace('<drone>', str(instances[4]))

    # Get file to write
    fw = open(output_file, 'w')
    fw.write(content)
    fw.close()


def main():
    for i1 in range(1, 5):
        for i2 in range(1, 5):
            for i3 in range(1, 5):
                for i4 in range(1, 5):
                    for i5 in range(1, 5):
                        # Get instances
                        instances = [i1, i2, i3, i4, i5]
                        # Create file
                        create_file(instances)


if __name__ == '__main__':
    main()
