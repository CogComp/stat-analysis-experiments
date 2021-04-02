DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

datasets=( 'tac2008' 'fabbri2020' 'bhandari2020' )
metrics=( 'QAEval' )

for dataset in "${datasets[@]}"; do
  for metric in "${metrics[@]}"; do
    python ${DIR}/run.py \
      --metrics-jsonls ${DIR}/../data/${dataset}/metrics.jsonl \
      --metrics Responsiveness QAEval \
      --num-processes 48 \
      --output-json ${DIR}/output/${dataset}/${metric}.json
  done
done

for metric in "${metrics[@]}"; do
  python ${DIR}/make_table.py \
    --tac-results ${DIR}/output/tac2008/${metric}.json \
    --fabbri-results ${DIR}/output/fabbri2020/${metric}.json \
    --bhandari-results ${DIR}/output/bhandari2020/${metric}.json \
    --output-dir ${DIR}/output/tables/${metric}
done