DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

datasets=( 'tac2008' 'fabbri2020' 'bhandari2020' )
metrics=( 'AutoSummENG' 'MeMoG' 'NPowER' 'BERTScore' 'BEwTE' 'METEOR' 'MoverScore' 'QAEval' 'ROUGE-1' 'ROUGE-2' 'ROUGE-L' 'ROUGE-SU4' 'S3' )
methods=( 'bootstrap-both' )

for dataset in "${datasets[@]}"; do
  for method in "${methods[@]}"; do
    for metric in "${metrics[@]}"; do
      kwargs='
        {
          "summary_level": {
            "pearson": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/summary_level/pearson.txt"
            },
            "spearman": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/summary_level/spearman.txt"
            },
            "kendall": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/summary_level/kendall.txt"
            }
          },
          "system_level": {
            "pearson": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/system_level/pearson.txt"
            },
            "spearman": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/system_level/spearman.txt"
            },
            "kendall": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/system_level/kendall.txt"
            }
          },
          "global": {
            "pearson": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/global/pearson.txt"
            },
            "spearman": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/global/spearman.txt"
            },
            "kendall": {
              "samples_output_file": "'${DIR}'/output/'${dataset}'/'${method}'/correlations/'${metric}'/global/kendall.txt"
            }
          }
        }
      '
      python -m sacrerouge correlate \
        --metrics-jsonl-files ${DIR}/../data/${dataset}/metrics.jsonl \
        --metrics Responsiveness ${metric} \
        --summarizer-type peer \
        --confidence-interval-method ${method} \
        --confidence 95 \
        --num-tails 2 \
        --confidence-interval-kwargs "${kwargs}" \
        --output-file ${DIR}/output/${dataset}/${method}/correlations/${metric}/correlations.json \
      &
    done
    wait
  done
done

for method in "${methods[@]}"; do
  python ${DIR}/plot.py \
    --tac08-input ${DIR}/output/tac2008/${method}/correlations \
    --fabbri2020-input ${DIR}/output/fabbri2020/${method}/correlations \
    --bhandari2020-input ${DIR}/output/bhandari2020/${method}/correlations \
    --output-dir ${DIR}/output/plots/${method}
done