import argparse
import json
import os
import sys
from scipy.stats import shapiro

sys.path.append('.')

from sacrerouge.commands.correlate import load_metrics, merge_metrics, filter_metrics, convert_to_matrices


def main(args):
    metrics_list = load_metrics(args.input_jsonls)
    metrics_list = merge_metrics(metrics_list)
    for metrics in metrics_list:
        metrics.flatten_keys()
    metrics_list = filter_metrics(metrics_list, 'peer', *args.metrics)
    for metrics in metrics_list:
        metrics.select_metrics(args.metrics)
        metrics.average_values()

    Xs = convert_to_matrices(metrics_list, *args.metrics)
    results = {}
    for name, X in zip(args.metrics, Xs):
        X_global = X.flatten()
        X_system = X.mean(axis=1)
        X_summaries = []
        for j in range(X.shape[1]):
            X_summaries.append(X[:, j])

        p_global = shapiro(X_global)[1]
        p_system = shapiro(X_system)[1]
        p_summaries = [shapiro(X[:, j])[1] for j in range(X.shape[1])]
        summaries_count = sum(1 if p <= 0.05 else 0 for p in p_summaries)
        summary_prop = summaries_count / X.shape[1]

        results[name] = {
            'global': p_global,
            'system': p_system,
            'summary_proportion': summary_prop
        }

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, 'w') as out:
        out.write(json.dumps(results, indent=2))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--input-jsonls', nargs='+')
    argp.add_argument('--metrics', nargs='+')
    argp.add_argument('--output-file')
    args = argp.parse_args()
    main(args)