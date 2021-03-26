import argparse
import gzip
import sys
from collections import defaultdict
from glob import glob

sys.path.append('.')

from sacrerouge.commands.correlate import merge_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlWriter


def main(args):
    metrics_dict = defaultdict(list)

    with open(args.input_csv, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            columns = line.strip().split()
            lp, score, system = columns
            score = float(score)
            metrics_dict[lp].append(Metrics('all', system, 'peer', {'human': score}))

    for gz in sorted(glob(f'{args.baselines_dir}/*.sys.score.gz')):
        with gzip.open(gz, 'rb') as f:
            for line in f:
                metric, lp, _, system, score = line.decode().strip().split()
                score = float(score)
                metrics_dict[lp].append(Metrics('all', system, 'peer', {metric: score}))

    for gz in sorted(glob(f'{args.metrics_dir}/*.sys.score.gz')):
        with gzip.open(gz, 'rb') as f:
            for line in f:
                metric, lp, _, system, score, _, _ = line.decode().strip().split()
                score = float(score)
                metrics_dict[lp].append(Metrics('all', system, 'peer', {metric: score}))

    for lp, metrics_list in metrics_dict.items():
        with JsonlWriter(f'{args.output_dir}/{lp}.jsonl') as out:
            metrics_list = merge_metrics(metrics_list)
            for metrics in metrics_list:
                out.write(metrics)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--input-csv', required=True)
    argp.add_argument('--baselines-dir', required=True)
    argp.add_argument('--metrics-dir', required=True)
    argp.add_argument('--output-dir', required=True)
    args = argp.parse_args()
    main(args)