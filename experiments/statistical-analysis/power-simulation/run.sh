DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

# We don't use a for loop because they require different rouge variants
python ${DIR}/run.py \
  --summaries-jsonl ${DIR}/../data/tac2008/summaries.jsonl \
  --metrics-jsonls ${DIR}/../data/tac2008/metrics.jsonl \
  --ground-truth Responsiveness \
  --rouge-variant recall \
  --num-processes 48 \
  --output-dir ${DIR}/output/tac2008/results

python ${DIR}/run.py \
  --summaries-jsonl ${DIR}/../data/fabbri2020/summaries.jsonl \
  --metrics-jsonls ${DIR}/../data/fabbri2020/metrics.jsonl \
  --ground-truth Responsiveness \
  --rouge-variant f1 \
  --num-processes 48 \
  --output-dir ${DIR}/output/fabbri2020/results

python ${DIR}/run.py \
  --summaries-jsonl ${DIR}/../data/bhandari2020/summaries.jsonl \
  --metrics-jsonls ${DIR}/../data/bhandari2020/metrics.jsonl \
  --ground-truth Responsiveness \
  --rouge-variant recall \
  --num-processes 48 \
  --output-dir ${DIR}/output/bhandari2020/results

python ${DIR}/plot.py \
  --input-dir ${DIR}/output/tac2008/results \
  --dataset "TAC'08" \
  --output-dir ${DIR}/output/tac2008/plots

python ${DIR}/plot.py \
  --input-dir ${DIR}/output/fabbri2020/results \
  --dataset "CNN/DM" \
  --output-dir ${DIR}/output/fabbri2020/plots

python ${DIR}/plot.py \
  --input-dir ${DIR}/output/bhandari2020/results \
  --dataset "CNN/DM" \
  --output-dir ${DIR}/output/bhandari2020/plots