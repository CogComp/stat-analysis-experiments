This directory contains an analysis of the metrics submitted to the WMT19 metrics shared task.
The data included here is from the released WMT data ([this file](http://ufallab.ms.mff.cuni.cz/~bojar/wmt19-metrics-task-package.tgz) from the [WMT19 results page](http://www.statmt.org/wmt19/results.html)):

- `wmt19-metrics-task-package/manual-evaluation/DA-syslevel.csv`: `data/DA-syslevel.csv`
- `wmt19-metrics-task-package/baselines`: `data/baselines`
- `wmt19-metrics-task-package/final-metric-scores/submissions-corrected`: `data/submissions-corrected`

These contain the metrics scores for each system and language pair as well as the system-level human judgments.

To reproduce the WMT results which calculate how many pairwise statistical differences are found, run the following code.

First, parse the WMT data into the SacreROUGE format
```
sh experiments/statistical-analysis/wmt/setup.sh
```
The metrics' scores are saved to `data/metrics`.
We only have system level values, so any summary-level correlation that might be calculated is meaningless.

Then, calculate the correlations of all of the metrics and run the pairwise hypothesis tests
```
sh experiments/statistical-analysis/wmt/run.sh
```
The correlations are written to `output/<language-pair>/correlations`.
These are only written to verify that we reproduce the correlations reported by WMT19 (http://www.statmt.org/wmt19/pdf/53/WMT02.pdf, page 9)

The `output/<language-pair>/stats.json` file will have the top metrics which are not statistically worse than any other (the bold metrics in the WMT19 results) and the number of significant differences found out of all possible pairwise comparisons.
In the paper, we report the number of significant results found when the correlations have an average value of 0.6 (3 out of 231) instead of 0.9 (81 out of 231).
To do that, we manually edited the `williams_diff_test` in `sacrerouge/stats.py` to shift the correlations `r12` and `r13` down by 0.3:
```python
r12 = abs(corr_func(X, Z)) - 0.3
r13 = abs(corr_func(Y, Z)) - 0.3
```
Then we reran the `run.sh` script.
It's hacky, but it's the easiest and quickest solution to calculate the number without adding a special argument to the `williams_diff_test` function.