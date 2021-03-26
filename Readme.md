# "Resampling Methods" Experiments
This paper contains the experiments related to the paper "Resampling Methods for Evaluating Summarization Evaluation Metrics."
The experiments use a fork of the [SacreROUGE library](https://github.com/danieldeutsch/sacrerouge).
If you want to use the statistical analyses proposed in the paper, they have been integrated into SacreROUGE, and we recommend you use the implementation there instead of here.

All of the experiment code is contained in the `experiments/statistical-analysis` directory.
All of the scripts should be run from the root of the repository, not that directory.

## Environment
The Python environment is the same as for SacreROUGE.
It is based on Python3.
`pip install -r requirements.txt` should install the required dependencies.

## Preparing the data
In the `experiments/statistical-analysis/data` directory, we have provided the scores of all of the automatic metrics and human judgments for the summaries across all 3 datasets.

For Bhandari et al., (2020) and Fabbri et al., (2020), we have also included the summaries.
The summaries are only necessary for running the power simulation experiment, not calculating/running the confidence intervals and hypothesis tests.
We cannot do the same for TAC 2008 because the data is licensed.
If you have access to the original data, see [here](doc/datasets/duc-tac/tac2008.md) for instructions for how to set up the dataset.
After you have finished those steps, copy `task1.A.summaries.jsonl` to `experiments/statistical-analysis/data/tac2008/summaries.jsonl`.

The Bhandari data is from the mixed version (both extractive and abstractive summaries).

All of the metrics scores came from running the metrics on the respective datasets.
See that metric's experiment directory (e.g., `experiments/qaeval/`) for the scripts to generate the scores.
The files that we included in `experiments/statistical-analysis/data` are the `scores.jsonl` files.
The ground-truth human judgments are also included (`tac2008/responsiveness.jsonl`, `fabbri2020/relevance.jsonl`, `bhandari2020/pyramid.jsonl`).

The only required step is to run
```
experiments/statistical-analysis/setup.sh
```
which will combine all of the metrics files into a single file.
Several of the metrics have different versions (e.g., precision, recall, f1), and we select one for each dataset.
The human judgments are also merged into a single `Responsiveness` metric, regardless of what the annotation was.
See `experiments/statistical-analysis/setup.py` for details.

## Reproducing Experiments
### Confidence Interval Simulation
To run the confidence interval simulation (Section 5.1; Table 1), run
```
sh experiments/statistical-analysis/confidence-interval-simulation/run.sh
```
By default, this will use the `joblib` library to run 48 processes in parallel.
This is configurable in the script.
The output will be written to `experiments/statistical-analysis/confidence-interval-simulation/output`.

### Power Simulation
To run the power simulation (Section 5.2; Figure 3), run
```
sh experiments/statistical-analysis/power-simulation/run.sh
```
By default, this will use the `joblib` library to run 48 processes in parallel.
This is configurable in the script.
The output will be written to `experiments/statistical-analysis/power-simulation/output`.

### Confidence Intervals
To calculate and plot the confidence intervals (Section 6.1; Figure 4), run
```
sh experiments/statistical-analysis/confidence-intervals/run.sh
```
The confidence intervals will be calculated for all of the metrics and plots will be saved to `experiments/statistical-analysis/confidence-intervals/output/plots`.

### Hypothesis Tests
To run all of the pairwise hypothesis tests (Section 6.2; Figure 5), run
```
sh experiments/statistical-analysis/hypothesis-tests/run.sh
```
The results from all of the tests will be saved to `experiments/statistical-analysis/hypothesis-tests/output` and the heatmap figure will be generated in `experiments/statistical-analysis/hypothesis-tests/output/heatmaps`.

### WMT Results
To calculate the number of statistical results found on WMT19 (Section 5.2), see [here](experiments/statistical-analysis/wmt/Readme.md). 

### Normality Tests
To reproduce the results of our normality tests (Appendix A; Table 2), run
```
sh experiments/statistical-analysis/normality-tests/run.sh
```
The Shapiro-Wilk test will be run on all of the data which would be input to the Pearson, Spearman, or Kendall correlation functions.
The data for the table in the paper will be saved to `experiments/statistical-analysis/normality-tests/output/table.tex`.
