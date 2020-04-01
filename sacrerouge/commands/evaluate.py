import argparse
import jsons
import os
from overrides import overrides
from typing import Any, Dict, List

from sacrerouge.commands import Subcommand
from sacrerouge.data import EvalInstance, Metrics, MetricsDict
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric


def load_metrics(config: Dict[str, Any]) -> List[Metric]:
    metrics = []
    for params in config['metrics']:
        metric = Metric.from_params(params)
        metrics.append(metric)
    return metrics


def get_initial_micro_list(instances: List[EvalInstance]) -> List[Metrics]:
    micro_list = []
    for instance in instances:
        micro_list.append(Metrics(instance.instance_id, instance.summarizer_id, instance.summarizer_type))
    return micro_list


class EvaluateSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('evaluate')
        self.parser.add_argument('config')
        self.parser.add_argument('macro_output_json')
        self.parser.add_argument('micro_output_jsonl')
        self.parser.add_argument('--silent', action='store_true')
        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        config = jsons.loads(open(args.config, 'r').read())
        dataset_reader = DatasetReader.from_params(config['dataset_reader'])
        metrics = load_metrics(config)

        instances = dataset_reader.read()
        summaries = [instance.summary for instance in instances]

        macro = MetricsDict()
        micro_list = get_initial_micro_list(instances)

        for metric in metrics:
            # Prepare the extra input arguments
            eval_args = []
            for field in metric.required_fields:
                eval_args.append([instance.fields[field] for instance in instances])

            # Score all the summaries
            this_macro, this_micro_list = metric.evaluate(summaries, *eval_args)

            # Update the global metrics dictionaries
            macro.update(this_macro)
            for micro, this_micro in zip(micro_list, this_micro_list):
                micro.metrics.update(this_micro)

        dirname = os.path.dirname(args.macro_output_json)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        serialized_macro = jsons.dumps({'metrics': macro}, jdkwargs={'indent': 2})
        with open(args.macro_output_json, 'w') as out:
            out.write(serialized_macro)
        if not args.silent:
            print(serialized_macro)

        with JsonlWriter(args.micro_output_jsonl) as out:
            for metrics_dict in micro_list:
                out.write(metrics_dict)
