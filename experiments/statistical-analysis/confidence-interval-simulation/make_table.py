import argparse
import json
import os


def main(args):
    tac = json.load(open(args.tac_results, 'r'))
    fabbri = json.load(open(args.fabbri_results, 'r'))
    bhandari = json.load(open(args.bhandari_results, 'r'))

    for coef in ['pearson', 'spearman', 'kendall']:
        tac_sys_fisher = tac['system_level'][coef]['fisher']['contains']
        tac_sys_input = tac['system_level'][coef]['bootstrap-input']['contains']
        tac_sys_system = tac['system_level'][coef]['bootstrap-system']['contains']
        tac_sys_joint = tac['system_level'][coef]['bootstrap-both']['contains']

        fabbri_sys_fisher = fabbri['system_level'][coef]['fisher']['contains']
        fabbri_sys_input = fabbri['system_level'][coef]['bootstrap-input']['contains']
        fabbri_sys_system = fabbri['system_level'][coef]['bootstrap-system']['contains']
        fabbri_sys_joint = fabbri['system_level'][coef]['bootstrap-both']['contains']

        bhandari_sys_fisher = bhandari['system_level'][coef]['fisher']['contains']
        bhandari_sys_input = bhandari['system_level'][coef]['bootstrap-input']['contains']
        bhandari_sys_system = bhandari['system_level'][coef]['bootstrap-system']['contains']
        bhandari_sys_joint = bhandari['system_level'][coef]['bootstrap-both']['contains']

        tac_sum_fisher = tac['summary_level'][coef]['fisher']['contains']
        tac_sum_input = tac['summary_level'][coef]['bootstrap-input']['contains']
        tac_sum_system = tac['summary_level'][coef]['bootstrap-system']['contains']
        tac_sum_joint = tac['summary_level'][coef]['bootstrap-both']['contains']

        fabbri_sum_fisher = fabbri['summary_level'][coef]['fisher']['contains']
        fabbri_sum_input = fabbri['summary_level'][coef]['bootstrap-input']['contains']
        fabbri_sum_system = fabbri['summary_level'][coef]['bootstrap-system']['contains']
        fabbri_sum_joint = fabbri['summary_level'][coef]['bootstrap-both']['contains']

        bhandari_sum_fisher = bhandari['summary_level'][coef]['fisher']['contains']
        bhandari_sum_input = bhandari['summary_level'][coef]['bootstrap-input']['contains']
        bhandari_sum_system = bhandari['summary_level'][coef]['bootstrap-system']['contains']
        bhandari_sum_joint = bhandari['summary_level'][coef]['bootstrap-both']['contains']

        os.makedirs(args.output_dir, exist_ok=True)
        with open(f'{args.output_dir}/{coef}.tex', 'w') as out:
            out.write(f'Fisher & {tac_sys_fisher:.2f} & {tac_sum_fisher:.2f} & & {fabbri_sys_fisher:.2f} & {fabbri_sum_fisher:.2f} & & {bhandari_sys_fisher:.2f} & {bhandari_sum_fisher:.2f} \\\\\n')
            out.write(f'\\midrule \\\\\n')
            out.write(f'\\textsc{{Boot-System}} & {tac_sys_system:.2f} & {tac_sum_system:.2f} & & {fabbri_sys_system:.2f} & {fabbri_sum_system:.2f} & & {bhandari_sys_system:.2f} & {bhandari_sum_system:.2f} \\\\\n')
            out.write(f'\\textsc{{Boot-Inputs}} & {tac_sys_input:.2f} & {tac_sum_input:.2f} & & {fabbri_sys_input:.2f} & {fabbri_sum_input:.2f} & & {bhandari_sys_input:.2f} & {bhandari_sum_input:.2f} \\\\\n')
            out.write(f'\\textsc{{Boot-Both}} & {tac_sys_joint:.2f} & {tac_sum_joint:.2f} & & {fabbri_sys_joint:.2f} & {fabbri_sum_joint:.2f} & & {bhandari_sys_joint:.2f} & {bhandari_sum_joint:.2f} \\\\\n')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--tac-results', required=True)
    argp.add_argument('--fabbri-results', required=True)
    argp.add_argument('--bhandari-results', required=True)
    argp.add_argument('--output-dir', required=True)
    args = argp.parse_args()
    main(args)