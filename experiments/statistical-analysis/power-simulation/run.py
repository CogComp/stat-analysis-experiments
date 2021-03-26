import argparse
import functools
import json
import os
import random
import sys
from collections import defaultdict
from joblib import Parallel, delayed
from scipy.stats import pearsonr
from typing import List

sys.path.append('.')

from sacrerouge.commands.correlate import load_metrics, filter_metrics, merge_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader, JsonlWriter
from sacrerouge.simulations import preprocess_instances_for_rouge_simulation, score_instances_with_ablated_rouge
from sacrerouge.stats import convert_to_matrices, system_level_corr, corr_diff_test, summary_level_corr


def _save_to_jsonl(data: List, output_file: str) -> None:
    with JsonlWriter(output_file) as out:
        for item in data:
            out.write(item)


def _save_to_json(data: List, output_file: str) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as out:
        out.write(json.dumps(data))


def _filter_instances(instances: List, metrics_list: List) -> List:
    seen = set()
    for metrics in metrics_list:
        seen.add((metrics.instance_id, metrics.summarizer_id))

    filtered = []
    for instance in instances:
        if (instance['instance_id'], instance['summarizer_id']) in seen:
            filtered.append(instance)
    return filtered


def _run_simulation(summaries_file: str,
                    metrics_file: str,
                    corr_func,
                    proportion: float,
                    method: str,
                    ground_truth: str,
                    rouge_variant: str,
                    alpha: float,
                    random_seed: int) -> int:
    random.seed(random_seed)
    instances = json.load(open(summaries_file, 'r'))
    metrics_list = JsonlReader(metrics_file, Metrics).read()

    metrics_list.extend(score_instances_with_ablated_rouge(instances, proportion, rouge_variant))
    metrics_list = merge_metrics(metrics_list)

    X, Y, Z = convert_to_matrices(metrics_list, 'ROUGE-1', 'ablated_rouge', ground_truth)

    pvalue = corr_diff_test(corr_func, X, Y, Z, method, False)
    if pvalue <= alpha:
        return 1
    return 0


def main(args):
    metrics_list = load_metrics(args.metrics_jsonls)
    metrics_list = merge_metrics(metrics_list)
    for metrics in metrics_list:
        metrics.flatten_keys()
    metrics_list = filter_metrics(metrics_list, 'peer', args.ground_truth, 'ROUGE-1')
    for metrics in metrics_list:
        metrics.select_metrics([args.ground_truth, 'ROUGE-1'])
        metrics.average_values()
    metrics_file = '/dev/shm/metrics.jsonl'
    _save_to_jsonl(metrics_list, metrics_file)

    instances = JsonlReader(args.summaries_jsonl).read()
    instances = _filter_instances(instances, metrics_list)
    instances = preprocess_instances_for_rouge_simulation(instances)
    summaries_file = '/dev/shm/summaries.json'
    _save_to_json(instances, summaries_file)

    num_iterations = 1000
    alpha = 0.05
    seed = 5

    for level_name, level in zip(['system_level', 'summary_level'], [system_level_corr, summary_level_corr]):
        results_dict = defaultdict(lambda: defaultdict(dict))
        for coef_name, coef_func in zip(['pearson'], [pearsonr]):
            corr_func = functools.partial(level, coef_func)
            for proportion in [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]:
                for method in ['williams', 'bootstrap-both', 'permutation-both']:
                    job_results = Parallel(n_jobs=args.num_processes)(
                        delayed(_run_simulation)(summaries_file, metrics_file, corr_func, proportion, method,
                                                 args.ground_truth, args.rouge_variant,
                                                 alpha, seed + i) for i in range(num_iterations))
                    power = sum(job_results) / len(job_results)
                    seed += len(job_results)
                    print(level_name, coef_name, method, proportion, power)
                    results_dict[coef_name][method][proportion] = power

        os.makedirs(args.output_dir, exist_ok=True)
        with open(f'{args.output_dir}/{level_name}.json', 'w') as out:
            out.write(json.dumps(results_dict, indent=2))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--summaries-jsonl', required=True)
    argp.add_argument('--metrics-jsonls', nargs='+', required=True)
    argp.add_argument('--ground-truth', required=True)
    argp.add_argument('--rouge-variant', required=True, choices=['recall', 'f1'])
    argp.add_argument('--num-processes', type=int, default=1)
    argp.add_argument('--output-dir', required=True)
    args = argp.parse_args()
    main(args)