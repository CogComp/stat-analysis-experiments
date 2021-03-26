import argparse
import sys

sys.path.append('.')

from sacrerouge.commands.correlate import load_metrics, merge_metrics
from sacrerouge.data import MetricsDict
from sacrerouge.io import JsonlWriter


def main(args):
    metrics_list = load_metrics(args.metrics_jsonls)
    metrics_list = merge_metrics(metrics_list)
    for metrics in metrics_list:
        metrics.flatten_keys()

    with JsonlWriter(args.output_jsonl) as out:
        for metrics in metrics_list:
            if metrics.summarizer_type != 'peer':
                continue

            if args.dataset == 'tac':
                metrics.metrics = MetricsDict({
                    'Responsiveness': metrics.metrics['overall_responsiveness'],
                    'ROUGE-1': metrics.metrics['rouge-1_recall'],
                    'ROUGE-2': metrics.metrics['rouge-2_recall'],
                    'ROUGE-L': metrics.metrics['rouge-l_recall'],
                    'ROUGE-SU4': metrics.metrics['rouge-su4_recall'],
                    'BEwTE': metrics.metrics['BEwTE_recall'],
                    'QAEval': metrics.metrics['qa-eval_f1'],
                    'AutoSummENG': metrics.metrics['AutoSummENG'],
                    'MeMoG': metrics.metrics['MeMoG'],
                    'NPowER': metrics.metrics['NPowER'],
                    'BERTScore': metrics.metrics['bertscore_recall'],
                    'METEOR': metrics.metrics['METEOR'],
                    'MoverScore': metrics.metrics['MoverScore'],
                    'S3': metrics.metrics['s3_resp']
                })

            elif args.dataset == 'fabbri2020':
                metrics.metrics = MetricsDict({
                    'Responsiveness': metrics.metrics['expert_relevance'],
                    'ROUGE-1': metrics.metrics['rouge-1_f1'],
                    'ROUGE-2': metrics.metrics['rouge-2_f1'],
                    'ROUGE-L': metrics.metrics['rouge-l_f1'],
                    'ROUGE-SU4': metrics.metrics['rouge-su4_f1'],
                    'BEwTE': metrics.metrics['BEwTE_f1'],
                    'QAEval': metrics.metrics['qa-eval_f1'],
                    'AutoSummENG': metrics.metrics['AutoSummENG'],
                    'MeMoG': metrics.metrics['MeMoG'],
                    'NPowER': metrics.metrics['NPowER'],
                    'BERTScore': metrics.metrics['bertscore_recall'],
                    'METEOR': metrics.metrics['METEOR'],
                    'MoverScore': metrics.metrics['MoverScore'],
                    'S3': metrics.metrics['s3_resp']
                })

            elif args.dataset == 'bhandari2020':
                metrics.metrics = MetricsDict({
                    'Responsiveness': metrics.metrics['litepyramid_recall'],
                    'ROUGE-1': metrics.metrics['rouge-1_recall'],
                    'ROUGE-2': metrics.metrics['rouge-2_recall'],
                    'ROUGE-L': metrics.metrics['rouge-l_recall'],
                    'ROUGE-SU4': metrics.metrics['rouge-su4_recall'],
                    'BEwTE': metrics.metrics['BEwTE_recall'],
                    'QAEval': metrics.metrics['qa-eval_f1'],
                    'AutoSummENG': metrics.metrics['AutoSummENG'],
                    'MeMoG': metrics.metrics['MeMoG'],
                    'NPowER': metrics.metrics['NPowER'],
                    'BERTScore': metrics.metrics['bertscore_recall'],
                    'METEOR': metrics.metrics['METEOR'],
                    'MoverScore': metrics.metrics['MoverScore'],
                    'S3': metrics.metrics['s3_resp']
                })
            else:
                raise Exception(f'Unknown dataset {args.dataset}')

            out.write(metrics)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--dataset', required=True)
    argp.add_argument('--metrics-jsonls', nargs='+', required=True)
    argp.add_argument('--output-jsonl', required=True)
    args = argp.parse_args()
    main(args)