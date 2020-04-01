import argparse
import itertools
import json
import os
from scipy.stats import pearsonr, spearmanr
from typing import Any, Dict, List

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlReader


def load_metrics(metrics_files: List[str]) -> List[Metrics]:
    metrics_lists = []
    for metrics_file in metrics_files:
        metrics_lists.append(JsonlReader(metrics_file, Metrics).read())

    # Merge >= 1 into 0
    for metrics_list in metrics_lists[1:]:
        for i, metrics in enumerate(metrics_list):
            metrics_lists[0][i].merge(metrics)

    return metrics_lists[0]


def filter_metrics(metrics_list: List[Metrics], summarizer_type: str, metric1: str, metric2: str):
    filtered = []
    skipped = 0
    for metrics in metrics_list:
        if summarizer_type == 'all' or summarizer_type == metrics.summarizer_type:
            if metric1 in metrics.metrics and metric2 in metrics.metrics:
                filtered.append(metrics)
            else:
                skipped += 1

    if skipped > 0:
        print(f'Warning: Skipped {skipped} inputs because at least one metric was missing')
    return filtered


def aggregate_metrics(metrics_list: List[Metrics]) -> Dict[str, MetricsDict]:
    # The instances must be sorted by the key in order to use itertools.groupby
    metrics_list = sorted(metrics_list, key=lambda metrics: metrics.summarizer_id)
    key_to_metrics = {}
    for key, group in itertools.groupby(metrics_list, lambda metrics: metrics.summarizer_id):
        group_metrics = [member.metrics for member in group]
        key_to_metrics[key] = sum(group_metrics) / len(group_metrics)
    return key_to_metrics


def compute_summary_level_correlations(metrics_list: List[Dict[str, Any]],
                                       metric1: str,
                                       metric2: str) -> Dict[str, float]:
    pearsons = []
    spearmans = []

    metrics_list = sorted(metrics_list, key=lambda metrics: metrics.instance_id)
    for _, group in itertools.groupby(metrics_list, key=lambda metrics: metrics.instance_id):
        group = list(group)
        values1 = [member.metrics[metric1] for member in group]
        values2 = [member.metrics[metric2] for member in group]

        r, _ = pearsonr(values1, values2)
        rho, _ = spearmanr(values1, values2)

        pearsons.append(r)
        spearmans.append(rho)

    pearson = sum(pearsons) / len(pearsons)
    spearman = sum(spearmans) / len(spearmans)
    return {
        'pearson': {
            'r': pearson
        },
        'spearman': {
            'rho': spearman
        }
    }


def compute_system_level_correlations(metrics_list: List[Dict[str, Any]],
                                      metric1: str,
                                      metric2: str) -> Dict[str, float]:
    metrics_list = list(aggregate_metrics(metrics_list).values())

    values1 = [metrics[metric1] for metrics in metrics_list]
    values2 = [metrics[metric2] for metrics in metrics_list]

    r, r_pvalue = pearsonr(values1, values2)
    rho, rho_pvalue = spearmanr(values1, values2)
    num_summarizers = len(metrics_list)

    return {
        'pearson': {
            'r': r,
            'p_value': r_pvalue
        },
        'spearman': {
            'rho': rho,
            'p_value': rho_pvalue
        },
        'num_summarizers': num_summarizers
    }


def main(args):
    metrics_list = load_metrics(args.metrics_jsonl_files)
    for metrics in metrics_list:
        metrics.flatten_keys()
        metrics.average_values()

    metric1, metric2 = args.metrics
    metrics_list = filter_metrics(metrics_list, args.summarizer_type, metric1, metric2)

    summary_level = compute_summary_level_correlations(metrics_list, metric1, metric2)
    system_level = compute_system_level_correlations(metrics_list, metric1, metric2)
    results = {
        'summary_level': summary_level,
        'system_level': system_level
    }

    if args.output_file:
        dirname = os.path.dirname(args.output_file)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(args.output_file, 'w') as out:
            out.write(json.dumps(results, indent=2))

    if not args.silent:
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--metrics-jsonl-files', nargs='+')
    argp.add_argument('--metrics', nargs=2)
    argp.add_argument('--summarizer-type', choices=['all', 'reference', 'peer'])
    argp.add_argument('--output-file')
    argp.add_argument('--silent', action='store_true')
    args = argp.parse_args()
    main(args)
