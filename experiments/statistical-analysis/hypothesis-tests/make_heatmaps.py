import argparse
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
import sys
from collections import defaultdict
from glob import glob
from matplotlib.patches import Rectangle

sys.path.append('.')

from sacrerouge.commands.partial_conjunction_test import run_all_partial_conjunction_pvalue_test


LEVELS = ['summary_level', 'system_level', 'global']
COEFS = ['pearson', 'spearman', 'kendall']


def load_data(input_dir):
    pvalues = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    metrics = set()
    metric_to_pairs = defaultdict(list)
    for input_path in glob(f'{input_dir}/*/*.json'):
        path = input_path.split('/')
        metric1 = path[-2]
        metric2 = path[-1][:-len('.json')]
        if metric1 == 'QAEval':
            metric1 = 'QAEval-F$_1$'
        if metric2 == 'QAEval':
            metric2 = 'QAEval-F$_1$'

        metrics.add(metric1)
        metrics.add(metric2)
        metric_to_pairs[metric1].append((metric2, input_path))
        correlations = json.load(open(input_path, 'r'))

        for level in LEVELS:
            for coef in COEFS:
                pvalues[level][coef][metric1][metric2] = correlations[level][coef]['pvalue']

    partial_results = {}
    for metric, pairs in metric_to_pairs.items():
        names = [name for name, _ in pairs]
        files = [file_path for _, file_path in pairs]
        partial_results[metric] = run_all_partial_conjunction_pvalue_test('bonferroni', files, names)

    metrics = sorted(metrics)
    return pvalues, partial_results, metrics


def get_matrix_and_highlights(pvalues, partial_results, metrics, level, coef):
    data = np.ones((len(metrics), len(metrics)))
    highlights = []
    for i, metric1 in enumerate(metrics):
        for j, metric2 in enumerate(metrics):
            if metric1 == metric2:
                continue
            value = pvalues[level][coef][metric1][metric2]
            data[i, j] = value

            if metric2 in partial_results[metric1][level][coef]['significant']:
                highlights.append((i, j))

    # Sanity check the highlights
    for i, j in highlights:
        if (j, i) in highlights:
            print('Both metrics have invalid significant results', metrics[i], metrics[j])

    return data, highlights


def plot_heatmap(data, highlights, metrics, ax, cbar, cbar_ax):
    colors = ['#2061A9', '#5C9FCD', '#C7DBF0', '#FFFFFF']
    boundaries = [0, 0.05, 1.0]
    norm = matplotlib.colors.BoundaryNorm(boundaries=boundaries, ncolors=256)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
    sns.heatmap(data, ax=ax, cbar=False, xticklabels=metrics, yticklabels=metrics,
                linewidths=0.5, linecolor='lightgray',
                cmap=cmap, norm=norm, cbar_ax=None)

    # Draw the diagonal lines
    ax.axline((1, 1), (2, 2), color='lightgray', linewidth=0.75)

    # Add the Bonferroni squares
    for i, j in highlights:
        ax.add_patch(Rectangle((j, i), 1, 1, fill=False, edgecolor='#ff7f0e', lw=2))



def main(args):
    tac_pvalues, tac_partial_results, tac_metrics = load_data(args.tac08_input)
    fab_pvalues, fab_partial_results, fab_metrics = load_data(args.fabbri2020_input)
    bha_pvalues, bha_partial_results, bha_metrics = load_data(args.bhandari2020_input)

    assert tac_metrics == fab_metrics == bha_metrics
    metrics = tac_metrics

    os.makedirs(args.output_dir, exist_ok=True)
    for coef in COEFS:
        fig, axes = plt.subplots(2, 3, sharex=True, sharey=True, figsize=(11, 6.5))
        cbar_ax = None

        data, highlights = get_matrix_and_highlights(tac_pvalues, tac_partial_results, metrics, 'summary_level', coef)
        plot_heatmap(data, highlights, metrics, axes[0, 0], True, cbar_ax)

        data, highlights = get_matrix_and_highlights(fab_pvalues, fab_partial_results, metrics, 'summary_level', coef)
        plot_heatmap(data, highlights, metrics, axes[0, 1], False, None)

        data, highlights = get_matrix_and_highlights(bha_pvalues, bha_partial_results, metrics, 'summary_level', coef)
        plot_heatmap(data, highlights, metrics, axes[0, 2], False, None)

        data, highlights = get_matrix_and_highlights(tac_pvalues, tac_partial_results, metrics, 'system_level', coef)
        plot_heatmap(data, highlights, metrics, axes[1, 0], False, None)

        data, highlights = get_matrix_and_highlights(fab_pvalues, fab_partial_results, metrics, 'system_level', coef)
        plot_heatmap(data, highlights, metrics, axes[1, 1], False, None)

        data, highlights = get_matrix_and_highlights(bha_pvalues, bha_partial_results, metrics, 'system_level', coef)
        plot_heatmap(data, highlights, metrics, axes[1, 2], False, None)

        axes[0, 0].tick_params(axis='both', which='major', labelsize=9, labelbottom=False, bottom=False, top=False, labeltop=True, left=False)
        axes[0, 0].set_xticklabels(metrics, rotation=45, ha='left', rotation_mode="anchor")

        axes[0, 1].tick_params(axis='both', which='major', labelsize=9, labelbottom=False, bottom=False, top=False, labeltop=True, left=False)
        axes[0, 1].set_xticklabels(metrics, rotation=45, ha='left', rotation_mode="anchor")

        axes[0, 2].tick_params(axis='both', which='major', labelsize=9, labelbottom=False, bottom=False, top=False, labeltop=True, left=False)
        axes[0, 2].set_xticklabels(metrics, rotation=45, ha='left', rotation_mode="anchor")

        axes[1, 0].tick_params(axis='both', which='major', labelsize=10, labelbottom=False, bottom=False, top=False, labeltop=False, left=False)
        axes[1, 1].tick_params(axis='both', which='major', labelsize=10, labelbottom=False, bottom=False, top=False, labeltop=False, left=False)
        axes[1, 2].tick_params(axis='both', which='major', labelsize=10, labelbottom=False, bottom=False, top=False, labeltop=False, left=False)

        fontsize = 12
        axes[1, 0].set_xlabel('TAC 2008', fontsize=fontsize, labelpad=10)
        axes[1, 1].set_xlabel('CNN/DM - Fabbri et al. (2021)', fontsize=fontsize, labelpad=10)
        axes[1, 2].set_xlabel('CNN/DM - Bhandari et al. (2020)', fontsize=fontsize, labelpad=10)

        axes[0, 2].set_ylabel('Summary-\nLevel', rotation=0, labelpad=35, fontsize=fontsize)
        axes[0, 2].yaxis.set_label_position("right")
        axes[1, 2].set_ylabel('System-\nLevel', rotation=0, labelpad=35, fontsize=fontsize)
        axes[1, 2].yaxis.set_label_position("right")

        axes[0, 0].text(-5.0, -1.5, '$\\mathcal{X}$$\\downarrow$  $\\mathcal{Y}$$\\rightarrow$', fontsize=14)

        plt.tight_layout()
        fig.savefig(f'{args.output_dir}/{coef}.pdf', pad_inches=0)
        plt.close()


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--tac08-input', required=True)
    argp.add_argument('--fabbri2020-input', required=True)
    argp.add_argument('--bhandari2020-input', required=True)
    argp.add_argument('--output-dir', required=True)
    args = argp.parse_args()
    main(args)