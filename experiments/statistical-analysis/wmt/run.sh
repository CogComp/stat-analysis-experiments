DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

datasets=( 'de-en' )
metrics=( 'BEER' 'BERTr' 'BLEU' 'CDER' 'CharacTER' 'chrF' 'chrF+' 'EED' 'ESIM' 'Meteor++_2.0(syntax)' 'Meteor++_2.0(syntax+copy)' 'NIST' 'PER' 'PReP' 'sacreBLEU-BLEU' 'sacreBLEU-chrF' 'TER' 'WER' 'WMDO' 'YiSi-0' 'YiSi-1' 'YiSi-1_srl' )

for dataset in "${datasets[@]}"; do
  for metric in "${metrics[@]}"; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files ${DIR}/data/metrics/${dataset}.jsonl \
      --metrics human ${metric} \
      --summarizer-type peer \
      --confidence-interval-method "none" \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}.json \
    &
  done
  wait

  for metric1 in "${metrics[@]}"; do
    for metric2 in "${metrics[@]}"; do
      if [ ${metric1} != ${metric2} ]; then
        python -m sacrerouge stat-sig-test \
          --metrics-jsonl-files ${DIR}/data/metrics/${dataset}.jsonl \
          --dependent-metric human \
          --metric-A ${metric1} \
          --metric-B ${metric2} \
          --summarizer-type peer \
          --hypothesis-test williams \
          --confidence 95 \
          --num-tails 1 \
          --output-file ${DIR}/output/${dataset}/hypothesis-tests/${metric1}/${metric2}.json \
          &
      fi
    done
    wait
  done

  python ${DIR}/analyze.py \
    --results-dir ${DIR}/output/${dataset}/hypothesis-tests \
    --output-file ${DIR}/output/${dataset}/stats.json
done