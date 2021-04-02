import argparse
import json
from glob import glob


def main(args):
    metrics = set()
    pvalues_dict = {}
    for file_path in glob(f'{args.results_dir}/*/*.json'):
        path = file_path.split('/')
        metric1 = path[-2]
        metric2 = path[-1][:-5]
        pvalues = json.load(open(file_path, 'r'))

        metrics.add(metric1)
        metrics.add(metric2)
        pvalues_dict[(metric1, metric2)] = pvalues['system_level']['pearson']['pvalue']

    top_metrics = set()
    for metric1 in sorted(metrics):
        is_lower = False
        for metric2 in sorted(metrics):
            if metric1 == metric2:
                continue
            # Check if metric2 > metric1
            if pvalues_dict[(metric2, metric1)] < 0.05:
                is_lower = True
                break

        if not is_lower:
            top_metrics.add(metric1)

    num_sig, num_notsig = 0, 0
    for i, metric1 in enumerate(sorted(metrics)):
        for j, metric2 in enumerate(sorted(metrics)):
            if i <= j:
                continue
            if pvalues_dict[(metric1, metric2)] < 0.05 or pvalues_dict[(metric2, metric1)] < 0.05:
                num_sig += 1
            else:
                num_notsig += 1

    with open(args.output_file, 'w') as out:
        out.write(json.dumps({
            'top_metrics': sorted(top_metrics),
            'num_sig': num_sig,
            'num_not_sig': num_notsig,
            'total': num_sig + num_notsig
        }, indent=2))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--results-dir', required=True)
    argp.add_argument('--output-file', required=True)
    args = argp.parse_args()