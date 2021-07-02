import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict
from glob import glob

LEVELS = ['summary_level', 'system_level', 'global']
COEFS = ['pearson', 'spearman', 'kendall']


def load_samples(input_dir):
    samples_dict = defaultdict(lambda: defaultdict(dict))
    metrics = set()
    for metric_dir in glob(f'{input_dir}/*'):
        path = metric_dir.split('/')
        metric = path[-1]
        if metric == 'QAEval':
            metric = 'QAEval-F$_1$'
        metrics.add(metric)

        for level in LEVELS:
            for coef in COEFS:
                samples = list(map(float, open(f'{metric_dir}/{level}/{coef}.txt', 'r').read().splitlines()))
                lower = np.percentile(samples, 2.5)
                upper = np.percentile(samples, 97.5)
                samples = np.array(list(filter(lambda x: lower <= x <= upper, samples)))
                samples_dict[level][coef][metric] = samples
    return samples_dict, metrics


def set_colors(parts):
    # Color hacks
    blue = '#1f77b4'
    orange = '#ff7f0e'
    for i, pc in enumerate(parts['bodies']):
        if i % 2 == 1:
            pc.set_color(orange)
    parts['cbars'].set_color([blue, orange])
    parts['cmaxes'].set_color([blue, orange])
    parts['cmins'].set_color([blue, orange])


def main(args):
    tac08, tac_metrics = load_samples(args.tac08_input)
    fabbri, fabbri_metrics = load_samples(args.fabbri2020_input)
    bhandari, bhandari_metrics = load_samples(args.bhandari2020_input)

    assert tac_metrics == fabbri_metrics
    metrics = sorted(tac_metrics)

    os.makedirs(args.output_dir, exist_ok=True)
    for coef in COEFS:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True, figsize=(10, 4))

        data1, data2, data3 = [], [], []
        positions = []
        ticks = []
        for i, metric in enumerate(metrics):
            data1.append(tac08['summary_level'][coef][metric])
            data1.append(tac08['system_level'][coef][metric])
            data2.append(fabbri['summary_level'][coef][metric])
            data2.append(fabbri['system_level'][coef][metric])
            data3.append(bhandari['summary_level'][coef][metric])
            data3.append(bhandari['system_level'][coef][metric])
            positions.append(len(metrics) - (i + 1))
            positions.append(len(metrics) - (i + 1))
            ticks.append(len(metrics) - (i + 1))

        parts1 = ax1.violinplot(data1, positions=positions, vert=False)
        parts2 = ax2.violinplot(data2, positions=positions, vert=False)
        parts3 = ax3.violinplot(data3, positions=positions, vert=False)
        set_colors(parts1)
        set_colors(parts2)
        set_colors(parts3)

        ax1.set_title('TAC 2008')
        ax2.set_title('CNN/DM - Fabbri et al. (2021)')
        ax3.set_title('CNN/DM - Bhandari et al. (2020)')

        ax1.set_yticks(ticks)
        ax1.set_yticklabels(metrics)

        fig.add_subplot(111, frame_on=False)
        plt.tick_params(labelcolor="none", bottom=False, left=False)

        coef_name = coef[0].upper() + coef[1:]
        plt.xlabel(f'{coef_name} Correlation Coefficient')

        plt.tight_layout()
        fig.savefig(f'{args.output_dir}/{coef}.pdf', bbox_inches='tight', pad_inches=0)
        plt.close()


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--tac08-input', required=True)
    argp.add_argument('--fabbri2020-input', required=True)
    argp.add_argument('--bhandari2020-input', required=True)
    argp.add_argument('--output-dir', required=True)
    args = argp.parse_args()
    main(args)