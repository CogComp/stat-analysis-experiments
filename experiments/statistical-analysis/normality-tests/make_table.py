import argparse
import json
import os


def main(args):
    tac2008 = json.load(open(args.tac2008, 'r'))
    fabbri2020 = json.load(open(args.fabbri2020, 'r'))
    bhandari2020 = json.load(open(args.bhandari2020, 'r'))

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, 'w') as out:
        for i, name in enumerate(args.metrics):
            if name == 'QAEval':
                name = 'QAEval-F$_1$'

            row = [name]
            for j, dataset in enumerate([tac2008, fabbri2020, bhandari2020]):
                row.append(f'{dataset[args.metrics[i]]["summary_proportion"] * 100:.1f}')
                row.append(f'{dataset[args.metrics[i]]["system"]:.2f}')
                if j != 2:
                    row.append(' ')
            out.write(' & '.join(row) + '\\\\\n')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--tac2008', required=True)
    argp.add_argument('--fabbri2020', required=True)
    argp.add_argument('--bhandari2020', required=True)
    argp.add_argument('--metrics', nargs='+', required=True)
    argp.add_argument('--output-file', required=True)
    args = argp.parse_args()
    main(args)