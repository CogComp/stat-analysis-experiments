DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

datasets=( 'tac2008' 'fabbri2020' 'bhandari2020' )
metrics=( 'AutoSummENG' 'MeMoG' 'NPowER' 'BERTScore' 'BEwTE' 'METEOR' 'MoverScore' 'QAEval' 'ROUGE-1' 'ROUGE-2' 'ROUGE-L' 'ROUGE-SU4' 'S3' )
methods=( 'permutation-both' )

for dataset in "${datasets[@]}"; do
  for metric1 in "${metrics[@]}"; do
    for metric2 in "${metrics[@]}"; do
      if [ ${metric1} != ${metric2} ]; then
        for method in "${methods[@]}"; do
          python -m sacrerouge stat-sig-test \
            --metrics-jsonl-files ${DIR}/../data/${dataset}/metrics.jsonl \
            --dependent-metric Responsiveness \
            --metric-A ${metric1} \
            --metric-B ${metric2} \
            --summarizer-type peer \
            --hypothesis-test ${method} \
            --confidence 95 \
            --num-tails 1 \
            --output-file ${DIR}/output/${dataset}/${method}/${metric1}/${metric2}.json \
            &
        done
      fi
    done
    wait
  done
done

for method in "${methods[@]}"; do
  python ${DIR}/make_heatmaps.py \
    --tac08-input ${DIR}/output/tac2008/${method}/ \
    --fabbri2020-input ${DIR}/output/fabbri2020/${method}/ \
    --bhandari2020-input ${DIR}/output/bhandari2020/${method}/ \
    --output-dir ${DIR}/output/heatmaps/${method}
done