import numpy as np
import random
from collections import Counter
from typing import Dict, List, Tuple, Union

from sacrerouge.data import Metrics
from sacrerouge.metrics import PythonRouge


ArrayOrArrays = Union[np.ndarray, Tuple[np.ndarray, ...]]


def sample_submatrices(*matrices: np.ndarray) -> Tuple[ArrayOrArrays, ArrayOrArrays, ArrayOrArrays, ArrayOrArrays]:
    # Ensure they are all the same shape and 2-dimensions
    N, M = matrices[0].shape
    for matrix in matrices:
        assert matrix.shape == (N, M)

    # Randomly shuffle all of the rows
    rows = np.random.permutation(N)
    matrices = [matrix[rows] for matrix in matrices]

    # Randomly shuffle the columns by transposing the matrices and shuffling the "rows"
    cols = np.random.permutation(M)
    matrices = [matrix.T[cols].T for matrix in matrices]

    # Split the matrices into 4 submatrices of equal size (ignoring odd sizes)
    i = N // 2
    j = M // 2
    As = [matrix[:i, :j] for matrix in matrices]
    Bs = [matrix[:i, j:] for matrix in matrices]
    Cs = [matrix[i:, :j] for matrix in matrices]
    Ds = [matrix[i:, j:] for matrix in matrices]

    # Only return individual matrices if only 1 matrix was given as input
    if len(matrices) == 1:
        return As[0], Bs[0], Cs[0], Ds[0]
    else:
        return As, Bs, Cs, Ds


def _preprocess_summary(summary, rouge: PythonRouge, token_to_id: Dict[str, int]):
    if isinstance(summary, list):
        summary = ' '.join(summary)
    tokens = rouge.preprocess_summary(summary)[0]
    token_ids = []
    for token in tokens:
        if token not in token_to_id:
            token_to_id[token] = len(token_to_id)
        token_ids.append(token_to_id[token])
    counts = Counter(token_ids)
    return token_ids, counts


def _get_intersection(counts1, counts2):
    intersection = {}
    for token, count in counts1.items():
        if token in counts2:
            intersection[str(token)] = min(count, counts2[token])
    return intersection


def preprocess_instances_for_rouge_simulation(instances: List) -> List:
    rouge = PythonRouge()
    compressed_instances = []
    for instance in instances:
        compressed = {
            'instance_id': instance['instance_id'],
            'summarizer_id': instance['summarizer_id']
        }

        token_to_id = {}
        summary_tokens, summary_counts = _preprocess_summary(instance['summary']['text'], rouge, token_to_id)
        compressed['tokens'] = summary_tokens

        compressed['references'] = []
        for reference in instance['references']:
            reference_tokens, reference_counts = _preprocess_summary(reference['text'], rouge, token_to_id)
            intersection = _get_intersection(summary_counts, reference_counts)
            compressed['references'].append({
                'num_tokens': len(reference_tokens),
                'intersection': intersection
            })
        compressed_instances.append(compressed)
    return compressed_instances


def _calculate_pr_f1(reference_total: int, summary_total: int, intersection: int) -> Tuple[float, float, float]:
    precision = 0.0
    if summary_total != 0.0:
        precision = intersection / summary_total * 100
    recall = 0.0
    if reference_total != 0.0:
        recall = intersection / reference_total * 100
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)
    return precision, recall, f1


def _get_score(instance, rouge_variant: str, proportion: float) -> float:
    summary_tokens = instance['tokens']
    num_to_take = int(len(summary_tokens) * proportion)
    sample = Counter(random.sample(summary_tokens, num_to_take))

    score = 0
    for reference in instance['references']:
        num_reference_tokens = reference['num_tokens']
        intersection = reference['intersection']

        count = 0
        for token, summary_count in sample.items():
            if str(token) in intersection:
                count += min(summary_count, intersection[str(token)])

        p, r, f1 = _calculate_pr_f1(num_reference_tokens, num_to_take, count)
        if rouge_variant == 'recall':
            score += r
        elif rouge_variant == 'f1':
            score += f1
        else:
            score += p
    score = score / len(instance['references'])
    return score


def score_instances_with_ablated_rouge(instances: List, proportion: float, rouge_variant: str,
                                       metric_name: str = 'ablated_rouge') -> List:
    metrics_list = []
    for instance in instances:
        score = _get_score(instance, rouge_variant, proportion)
        metrics_list.append(Metrics(instance['instance_id'], instance['summarizer_id'], 'peer',
                                    {metric_name: score}))
    return metrics_list