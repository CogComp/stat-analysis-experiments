DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -e

python ${DIR}/setup.py \
  --dataset tac \
  --metrics-jsonls \
      ${DIR}/data/tac2008/autosummeng.jsonl \
      ${DIR}/data/tac2008/bertscore.jsonl \
      ${DIR}/data/tac2008/bewte.jsonl \
      ${DIR}/data/tac2008/meteor.jsonl \
      ${DIR}/data/tac2008/moverscore.jsonl \
      ${DIR}/data/tac2008/qaeval.jsonl \
      ${DIR}/data/tac2008/responsiveness.jsonl \
      ${DIR}/data/tac2008/s3.jsonl \
  --output-jsonl ${DIR}/data/tac2008/metrics.jsonl

python ${DIR}/setup.py \
  --dataset fabbri2020 \
  --metrics-jsonls \
      ${DIR}/data/fabbri2020/autosummeng.jsonl \
      ${DIR}/data/fabbri2020/bertscore.jsonl \
      ${DIR}/data/fabbri2020/bewte.jsonl \
      ${DIR}/data/fabbri2020/meteor.jsonl \
      ${DIR}/data/fabbri2020/moverscore.jsonl \
      ${DIR}/data/fabbri2020/qaeval.jsonl \
      ${DIR}/data/fabbri2020/relevance.jsonl \
      ${DIR}/data/fabbri2020/rouge.jsonl \
      ${DIR}/data/fabbri2020/s3.jsonl \
  --output-jsonl ${DIR}/data/fabbri2020/metrics.jsonl

python ${DIR}/setup.py \
  --dataset bhandari2020 \
  --metrics-jsonls \
      ${DIR}/data/bhandari2020/autosummeng.jsonl \
      ${DIR}/data/bhandari2020/bewte.jsonl \
      ${DIR}/data/bhandari2020/meteor.jsonl \
      ${DIR}/data/bhandari2020/pyramid.jsonl \
      ${DIR}/data/bhandari2020/qaeval.jsonl \
      ${DIR}/data/bhandari2020/rouge.jsonl \
      ${DIR}/data/bhandari2020/s3.jsonl \
  --output-jsonl ${DIR}/data/bhandari2020/metrics.jsonl