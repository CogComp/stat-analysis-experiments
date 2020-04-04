import argparse
import tarfile
from collections import defaultdict

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def parse_filename(filename: str):
    parts = filename.split('.')
    assert len(parts) == 5
    instance_id = parts[0].split('-')[0].lower()
    group = parts[0].split('-')[1]
    summarizer_id = parts[4]
    return instance_id, group, summarizer_id


def load_summaries(eval_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and (member.name.startswith('UpdateSumm08_eval/ROUGE/models/') or member.name.startswith('UpdateSumm08_eval/ROUGE/peers/')):
                path = member.name.split('/')
                filename = path[-1]
                instance_id, group, summarizer_id = parse_filename(filename)

                if summarizer_id.isalpha():
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'

                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                sentences = list(filter(None, map(lambda sentence: sentence.strip(), sentences)))
                summary = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': sentences
                }
                summaries[instance_id][summarizer_id][group] = summary
    return summaries


def load_manual_judgments(eval_tar: str, metrics):
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile('UpdateSumm08_eval/manual/manual.model').read().decode().splitlines()
        for line in lines:
            columns = line.split()
            instance_id = columns[0].split('-')[0].lower()
            group = columns[0].split('-')[1]
            summarizer_id = columns[1]
            metrics[instance_id][group][summarizer_id] = {
                'num_scus_jk': int(columns[2]),
                'modified_pyramid_score_jk': float(columns[4]),
                'linguistic_quality': int(columns[5]),
                'overall_responsiveness': int(columns[6])
            }

        lines = tar.extractfile('UpdateSumm08_eval/manual/manual.peer').read().decode().splitlines()
        for line in lines:
            columns = line.split()
            instance_id = columns[0].split('-')[0].lower()
            group = columns[0].split('-')[1]
            summarizer_id = columns[1]
            metrics[instance_id][group][summarizer_id] = {
                'modified_pyramid_score': float(columns[2]),
                'num_scus': int(columns[3]),
                'num_repetitions': int(columns[4]),
                'modified_pyramid_score_jk': float(columns[6]),
                'linguistic_quality': int(columns[7]),
                'overall_responsiveness': int(columns[8])
            }


def load_rouge_output(eval_tar: str, file_path: str, metrics):
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 7 and columns[2] == 'Eval':
                summarizer_id = columns[0]
                rouge_metric = columns[1].lower()
                instance_id, group, summarizer_id = parse_filename(columns[3])
                recall = float(columns[4][2:]) * 100
                precision = float(columns[5][2:]) * 100
                f1 = float(columns[6][2:]) * 100
                metrics[instance_id][group][summarizer_id][rouge_metric] = {
                    'recall': recall,
                    'precision': precision,
                    'f1': f1
                }


def load_rouge_jk_output(eval_tar: str, file_path: str, metrics):
    jk_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 7 and columns[2] == 'Eval':
                summarizer_id = columns[0]
                rouge_metric = columns[1].lower() + '_jk'
                instance_id, group, summarizer_id = parse_filename(columns[3])

                recall = float(columns[4][2:]) * 100
                precision = float(columns[5][2:]) * 100
                f1 = float(columns[6][2:]) * 100
                jk_metrics[instance_id][group][summarizer_id][rouge_metric]['recall'].append(recall)
                jk_metrics[instance_id][group][summarizer_id][rouge_metric]['precision'].append(precision)
                jk_metrics[instance_id][group][summarizer_id][rouge_metric]['f1'].append(f1)

        for instance_id in jk_metrics.keys():
            for group in ['A', 'B']:
                for summarizer_id in jk_metrics[instance_id][group].keys():
                    for rouge_metric in jk_metrics[instance_id][group][summarizer_id].keys():
                        recalls = jk_metrics[instance_id][group][summarizer_id][rouge_metric]['recall']
                        precisions = jk_metrics[instance_id][group][summarizer_id][rouge_metric]['precision']
                        f1s = jk_metrics[instance_id][group][summarizer_id][rouge_metric]['f1']
                        metrics[instance_id][group][summarizer_id][rouge_metric] = {
                            'recall': sum(recalls) / len(recalls),
                            'precision': sum(precisions) / len(precisions),
                            'f1': sum(f1s) / len(f1s)
                        }


def get_references(summaries, instance_id, summarizer_id, group):
    summarizer_ids = list(summaries[instance_id].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summarizer_ids))

    references = []
    for reference_id in reference_ids:
        if summarizer_id == reference_id:
            continue
        references.append(summaries[instance_id][reference_id][group])
    return references


def save_summaries_and_metrics(summaries, metrics, output_dir: str):
    with JsonlWriter(f'{output_dir}/task1.A-B.summaries.jsonl') as out_summaries_A_B:
        with JsonlWriter(f'{output_dir}/task1.A.summaries.jsonl') as out_summaries_A:
            with JsonlWriter(f'{output_dir}/task1.B.summaries.jsonl') as out_summaries_B:
                with JsonlWriter(f'{output_dir}/task1.A-B.metrics.jsonl') as out_metrics_A_B:
                    with JsonlWriter(f'{output_dir}/task1.A.metrics.jsonl') as out_metrics_A:
                        with JsonlWriter(f'{output_dir}/task1.B.metrics.jsonl') as out_metrics_B:
                            for instance_id in sorted(summaries.keys()):
                                for summarizer_id in sorted(summaries[instance_id].keys()):
                                    summary_A = summaries[instance_id][summarizer_id]['A']
                                    summary_B = summaries[instance_id][summarizer_id]['B']

                                    references_A = get_references(summaries, instance_id, summarizer_id, 'A')
                                    references_B = get_references(summaries, instance_id, summarizer_id, 'B')

                                    metrics_A = metrics[instance_id]['A'][summarizer_id]
                                    metrics_B = metrics[instance_id]['B'][summarizer_id]

                                    summary_instance_A = {
                                        'instance_id': f'{instance_id}-A',
                                        'summarizer_id': summarizer_id,
                                        'summarizer_type': summary_A['summarizer_type'],
                                        'summary': summary_A,
                                        'references': references_A,
                                    }
                                    summary_instance_B = {
                                        'instance_id': f'{instance_id}-B',
                                        'summarizer_id': summarizer_id,
                                        'summarizer_type': summary_B['summarizer_type'],
                                        'summary': summary_B,
                                        'references': references_B,
                                        'metrics': metrics_B
                                    }
                                    metric_instance_A = Metrics(f'{instance_id}-A', summarizer_id, summary_A['summarizer_type'], metrics_A)
                                    metric_instance_B = Metrics(f'{instance_id}-B', summarizer_id, summary_B['summarizer_type'], metrics_B)

                                    out_summaries_A_B.write(summary_instance_A)
                                    out_summaries_A_B.write(summary_instance_B)
                                    out_summaries_A.write(summary_instance_A)
                                    out_summaries_B.write(summary_instance_B)

                                    out_metrics_A_B.write(metric_instance_A)
                                    out_metrics_A_B.write(metric_instance_B)
                                    out_metrics_A.write(metric_instance_A)
                                    out_metrics_B.write(metric_instance_B)


def setup(data_dir: str, output_dir: str):
    eval_tar = f'{data_dir}/scrapes/tac.nist.gov/protected/past-aquaint2/2008/UpdateSumm08_eval.tar.gz'
    main(eval_tar, output_dir)


def main(eval_tar, output_dir):
    summaries = load_summaries(eval_tar)

    metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(MetricsDict)))
    load_manual_judgments(eval_tar, metrics)
    load_rouge_output(eval_tar, 'UpdateSumm08_eval/ROUGE/rouge.m.out', metrics)
    load_rouge_jk_output(eval_tar, 'UpdateSumm08_eval/ROUGE/rougejk.m.out', metrics)
    load_rouge_output(eval_tar, 'UpdateSumm08_eval/BE/simple.m.hm.out', metrics)
    load_rouge_jk_output(eval_tar, 'UpdateSumm08_eval/BE/simplejk.m.hm.out', metrics)

    save_summaries_and_metrics(summaries, metrics, output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('eval_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.eval_tar, args.output_dir)
