import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import os

METHODS = [
    'bootstrap-both',
    'permutation-both',
    'williams',
]

NAMES = {
    'williams': 'Williams',
    'bootstrap-both': 'Boot-Both',
    'permutation-both': 'Perm-Both',
}

STYLES = ['-', '--', ':']


def main(args):
    plt.rcParams.update({'font.size': 15})

    system_results = json.load(open(f'{args.input_dir}/system_level.json', 'r'))
    summary_results = json.load(open(f'{args.input_dir}/summary_level.json', 'r'))

    for coef in ['pearson']:
        fig, axes = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(8, 4))

        proportions = sorted(map(float, system_results[coef][METHODS[0]].keys()))

        lines = []
        names = []
        for method, style in zip(METHODS, STYLES):
            system_powers = [system_results[coef][method][str(prop)] for prop in proportions]
            summary_powers = [summary_results[coef][method][str(prop)] for prop in proportions]
            system_errs = [1.96 * np.sqrt(power * (1 - power) / 1000) for power in system_powers]  # n = 1000
            summary_errs = [1.96 * np.sqrt(power * (1 - power) / 1000) for power in summary_powers]  # n = 1000
            xs = [p * 100 for p in proportions]
            axes[0].errorbar(xs, system_powers, yerr=system_errs, linewidth=3, linestyle=style)
            lines.append(axes[1].errorbar(xs, summary_powers, yerr=summary_errs, linewidth=3, linestyle=style)[0])
            names.append(NAMES[method])

        # plt.title(args.dataset)
        axes[0].set_title('System-Level')
        axes[1].set_title('Summary-Level')
        axes[0].set_ylabel('Power')
        fig.legend(lines, labels=names, loc="lower center", bbox_to_anchor=(0.525,0), ncol=3)
        plt.subplots_adjust(right=0.85)
        axes[0].grid()
        axes[1].grid()
        axes[0].set_xticks([0, 20, 40, 60, 80, 100])
        axes[1].set_xticks([0, 20, 40, 60, 80, 100])

        fig.add_subplot(111, frameon=False)
        plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
        plt.xlabel('$k$, Percent of Summary Tokens used for ROUGE')

        plt.tight_layout()
        os.makedirs(f'{args.output_dir}/power/', exist_ok=True)
        fig.savefig(f'{args.output_dir}/power/{coef}.pdf', bbox_inches='tight', pad_inches=0)
        plt.close()


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--input-dir', required=True)
    argp.add_argument('--dataset', required=True)
    argp.add_argument('--output-dir', required=True)
    args = argp.parse_args()
    main(args)