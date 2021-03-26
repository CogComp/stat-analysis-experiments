import argparse
import functools
import json
import os
import numpy as np
import sys
from collections import Counter, defaultdict
from joblib import Parallel, delayed
from scipy.stats import pearsonr, spearmanr, kendalltau

sys.path.append('.')

from sacrerouge.commands.correlate import load_metrics, filter_metrics, merge_metrics
from sacrerouge.simulations import sample_submatrices
from sacrerouge.stats import convert_to_matrices, system_level_corr, corr_diff_test, summary_level_corr, corr_ci


def _run_simulation(X: np.ndarray, Y: np.ndarray, corr_func, method: str, alpha: float, random_seed: int) -> str:
    np.random.seed(random_seed)
    (X_A, Y_A), _, _, (X_D, Y_D) = sample_submatrices(X, Y)
    lower, upper = corr_ci(corr_func, X_A, Y_A, method, alpha=alpha)
    corr_D = corr_func(X_D, Y_D)
    if corr_D < lower:
        # The CI is too high
        return 'too_high'
    elif lower <= corr_D <= upper:
        return 'contains'
    else:
        # The CI is too low
        return 'too_low'


def main(args):
    metrics_list = load_metrics(args.metrics_jsonls)
    metrics_list = merge_metrics(metrics_list)

    for metrics in metrics_list:
        metrics.flatten_keys()

    metrics_list = filter_metrics(metrics_list, 'peer', *args.metrics)
    for metrics in metrics_list:
        metrics.select_metrics(args.metrics)
        metrics.average_values()
    X, Y = convert_to_matrices(metrics_list, *args.metrics)

    num_iterations = 1000
    alpha = 0.05
    seed = 10

    results_dict = defaultdict(lambda: defaultdict(dict))
    for coef_name, coef_func in zip(['pearson', 'spearman', 'kendall'], [pearsonr, spearmanr, kendalltau]):
        for level_name, level in zip(['system_level', 'summary_level'], [system_level_corr, summary_level_corr]):
            corr_func = functools.partial(level, coef_func)
            for method in ['bootstrap-system', 'bootstrap-input', 'bootstrap-both', 'fisher']:
                results = Parallel(n_jobs=args.num_processes)(delayed(_run_simulation)(X, Y, corr_func, method, alpha, seed + i) for i in range(num_iterations))
                counts = Counter(results)
                proportions = {key: value / len(results) for key, value in counts.items()}
                results_dict[level_name][coef_name][method] = proportions
                print(level_name, coef_name, method, proportions)

    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, 'w') as out:
        out.write(json.dumps(results_dict, indent=2))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--metrics-jsonls', nargs='+', required=True)
    argp.add_argument('--metrics', nargs=2, required=True)
    argp.add_argument('--num-processes', type=int, default=1)
    argp.add_argument('--output-json', required=True)
    args = argp.parse_args()
    main(args)