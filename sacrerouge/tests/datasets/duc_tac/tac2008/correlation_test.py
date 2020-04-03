import os
import pytest
import unittest

from sacrerouge.commands.correlate import compute_correlation

_metrics_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A-B.metrics.jsonl'


class TestTAC2008Correlation(unittest.TestCase):
    # Computes the correlations of the TAC 2008 metrics and compares them
    # to the results published in Dang (2008):
    # (https://tac.nist.gov//publications/2008/additional.papers/update_summ_overview08.proceedings.pdf)
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2008 metrics file does not exist')
    def test_dang_2008_table_6(self):
        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'linguistic_quality', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.910, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.778, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'linguistic_quality', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.750, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.763, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'modified_pyramid_score_jk', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.455, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.637, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'modified_pyramid_score', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.941, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.950, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58

    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2008 metrics file does not exist')
    def test_dang_2008_table_9(self):
        correlations = compute_correlation(_metrics_file_path, 'modified_pyramid_score_jk', 'rouge-2_jk_recall', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.429, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.276, 1e-1)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'modified_pyramid_score_jk', 'rouge-su4_jk_recall', 'reference')
        # assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.595, 1e-2)
        # assert correlations['system_level']['pearson']['r'] == pytest.approx(0.457, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'modified_pyramid_score_jk', 'rouge-be-hm_jk_recall', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.309, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.425, 1e-1)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'modified_pyramid_score', 'rouge-2_recall', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.967, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.946, 1e-1)
        assert correlations['system_level']['num_summarizers'] == 58

        correlations = compute_correlation(_metrics_file_path, 'modified_pyramid_score', 'rouge-su4_recall', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.951, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.928, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58

        correlations = compute_correlation(_metrics_file_path, 'modified_pyramid_score', 'rouge-be-hm_recall', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.950, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.949, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58

    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2008 metrics file does not exist')
    def test_dang_2008_table_10(self):
        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'rouge-2_jk_recall', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.874, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.725, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'rouge-su4_jk_recall', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.898, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.866, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'rouge-be-hm_jk_recall', 'reference')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.683, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.656, 1e-1)
        assert correlations['system_level']['num_summarizers'] == 8

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'rouge-2_recall', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.920, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.894, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'rouge-su4_recall', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.909, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.874, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58

        correlations = compute_correlation(_metrics_file_path, 'overall_responsiveness', 'rouge-be-hm_recall', 'peer')
        assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.910, 1e-2)
        assert correlations['system_level']['pearson']['r'] == pytest.approx(0.911, 1e-2)
        assert correlations['system_level']['num_summarizers'] == 58
