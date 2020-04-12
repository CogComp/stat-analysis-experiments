Here is the comparison of the performance of our MoverScore wrapper compared to the [original implementation](https://github.com/AIPHES/emnlp19-moverscore) (after editing the code to implement jackknifing) at the summary-level using all of the summaries (references and peers).

Correlation to responsiveness
| Implementation | Pearson | Spearman | Kendall |
|----------------|---------|----------|---------|
| Original       | 0.5768  | 0.5578   | 0.4449  |
| Ours           | 0.6031  | 0.5645   | 0.4595  |

Correlation to pyramid score
| Implementation | Pearson | Spearman | Kendall |
|----------------|---------|----------|---------|
| Original       | 0.7266  | 0.6892   | 0.5353  |
| Ours           | 0.6649  | 0.6385   | 0.4783  |
I believe the difference in pyramid score correlations is explained by which pyramid score was used.
The original implementation uses the un-jackknifed pyramid score for the peers and the (jackknifed) pyramid score for the references.
