DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in tac2008 fabbri2020 bhandari2020; do
  python ${DIR}/run.py \
    --input-jsonls ${DIR}/../data/${dataset}/metrics.jsonl \
    --metrics 'Responsiveness' 'AutoSummENG' 'MeMoG' 'NPowER' 'BERTScore' 'BEwTE' 'METEOR' 'MoverScore' 'QAEval' 'ROUGE-1' 'ROUGE-2' 'ROUGE-L' 'ROUGE-SU4' 'S3' \
    --output-file ${DIR}/output/${dataset}.json
done

python ${DIR}/make_table.py \
  --tac2008 ${DIR}/output/tac2008.json \
  --fabbri2020 ${DIR}/output/fabbri2020.json \
  --bhandari2020 ${DIR}/output/bhandari2020.json \
  --metrics 'Responsiveness' 'AutoSummENG' 'MeMoG' 'NPowER' 'BERTScore' 'BEwTE' 'METEOR' 'MoverScore' 'QAEval' 'ROUGE-1' 'ROUGE-2' 'ROUGE-L' 'ROUGE-SU4' 'S3' \
  --output-file ${DIR}/output/table.tex

