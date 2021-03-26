DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python ${DIR}/setup.py \
  --input-csv ${DIR}/data/DA-syslevel.csv \
  --baselines-dir ${DIR}/data/baselines \
  --metrics-dir ${DIR}/data/submissions-corrected \
  --output-dir ${DIR}/data/metrics