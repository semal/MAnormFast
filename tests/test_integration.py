# coding=utf-8
"""Integration tests: run the full MAnormFast pipeline."""
import sys
import os
import tempfile
import shutil
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.MAnorm_io import (read_peaks, read_reads,
                           output_normalized_peaks, output_3set_normalized_peaks,
                           draw_figs_to_show_data, output_peaks_mvalue_2wig_file,
                           output_unbiased_peaks, output_biased_peaks)
from lib.peaks import (get_common_peaks, get_peaks_size, merge_common_peaks,
                       cal_peaks_read_density, use_merged_peaks_fit_model,
                       normalize_peaks)


class TestFullPipeline:
    """Run the complete MAnormFast analysis pipeline with sample data."""

    @pytest.fixture
    def output_dir(self):
        d = tempfile.mkdtemp(prefix='manormfast_test_')
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_full_pipeline(self, sample_peaks1, sample_peaks2,
                           sample_reads1, sample_reads2, output_dir):
        ext = 1000
        min_smt_dist = ext // 2

        # Step 1: Read input
        pks1 = read_peaks(sample_peaks1)
        pks2 = read_peaks(sample_peaks2)
        reads_pos1 = read_reads(sample_reads1, 100)
        reads_pos2 = read_reads(sample_reads2, 100)

        assert get_peaks_size(pks1) == 30
        assert get_peaks_size(pks2) == 30

        # Step 2: Classify peaks
        pks1_uniq, pks1_com, pks2_uniq, pks2_com = get_common_peaks(pks1, pks2)
        total = (get_peaks_size(pks1_uniq) + get_peaks_size(pks1_com) +
                 get_peaks_size(pks2_uniq) + get_peaks_size(pks2_com))
        assert total > 0

        # Step 3: Merge common peaks
        merged_pks, summit2summit_dist = merge_common_peaks(pks1_com, pks2_com)
        assert get_peaks_size(merged_pks) > 0

        # Step 4: Calculate read density
        cal_peaks_read_density(pks1, reads_pos1, reads_pos2, ext)
        cal_peaks_read_density(pks2, reads_pos1, reads_pos2, ext)
        cal_peaks_read_density(merged_pks, reads_pos1, reads_pos2, ext)

        # Step 5: Fit model
        ma_fit = use_merged_peaks_fit_model(merged_pks, summit2summit_dist, min_smt_dist)
        assert len(ma_fit) == 2

        # Step 6: Normalize
        normalize_peaks(pks1, ma_fit)
        normalize_peaks(pks2, ma_fit)
        normalize_peaks(merged_pks, ma_fit)

        # Step 7: Output
        xls_path = os.path.join(output_dir, 'test_all_peak_MAvalues.xls')
        output_3set_normalized_peaks(
            pks1_uniq, merged_pks, pks2_uniq,
            xls_path, 'peaks1', 'peaks2', 'reads1', 'reads2'
        )
        assert os.path.isfile(xls_path)
        with open(xls_path) as f:
            lines = f.readlines()
        assert len(lines) > 1  # header + data
        assert 'M_value' in lines[0]

        # Figures
        fig_dir = os.path.join(output_dir, 'figures')
        os.mkdir(fig_dir)
        draw_figs_to_show_data(
            pks1_uniq, pks2_uniq, merged_pks,
            'peaks1', 'peaks2', ma_fit, 'reads1', 'reads2',
            output_dir=fig_dir
        )
        assert os.path.isfile(os.path.join(fig_dir, 'before_rescale.png'))
        assert os.path.isfile(os.path.join(fig_dir, 'after_rescale.png'))

        # WIG files
        wig_dir = os.path.join(output_dir, 'wig')
        os.mkdir(wig_dir)
        output_peaks_mvalue_2wig_file(
            pks1_uniq, pks2_uniq, merged_pks, 'test', output_dir=wig_dir
        )
        assert os.path.isfile(os.path.join(wig_dir, 'test_peaks_Mvalues.wig'))

        # Filter files
        filter_dir = os.path.join(output_dir, 'filters')
        os.mkdir(filter_dir)
        output_unbiased_peaks(
            pks1_uniq, pks2_uniq, merged_pks, 1.0, False, output_dir=filter_dir
        )
        output_biased_peaks(
            pks1_uniq, pks2_uniq, merged_pks, 1.0, 0.01, False, output_dir=filter_dir
        )
        assert os.path.isfile(os.path.join(filter_dir, 'unbiased_peaks_of_all_peaks.bed'))

    def test_no_merge_mode(self, sample_peaks1, sample_peaks2,
                            sample_reads1, sample_reads2, output_dir):
        """Test the -s (no merge) output mode."""
        ext = 1000
        pks1 = read_peaks(sample_peaks1)
        pks2 = read_peaks(sample_peaks2)
        reads_pos1 = read_reads(sample_reads1, 100)
        reads_pos2 = read_reads(sample_reads2, 100)

        pks1_uniq, pks1_com, pks2_uniq, pks2_com = get_common_peaks(pks1, pks2)
        merged_pks, smt_dist = merge_common_peaks(pks1_com, pks2_com)

        cal_peaks_read_density(pks1, reads_pos1, reads_pos2, ext)
        cal_peaks_read_density(pks2, reads_pos1, reads_pos2, ext)
        cal_peaks_read_density(merged_pks, reads_pos1, reads_pos2, ext)

        ma_fit = use_merged_peaks_fit_model(merged_pks, smt_dist, ext // 2)
        normalize_peaks(pks1, ma_fit)
        normalize_peaks(pks2, ma_fit)
        normalize_peaks(merged_pks, ma_fit)

        # No-merge outputs individual peak files
        f1 = os.path.join(output_dir, 'peaks1_MAvalues.xls')
        f2 = os.path.join(output_dir, 'peaks2_MAvalues.xls')
        output_normalized_peaks(pks1_uniq, pks1_com, f1, 'reads1', 'reads2')
        output_normalized_peaks(pks2_uniq, pks2_com, f2, 'reads1', 'reads2')
        assert os.path.isfile(f1)
        assert os.path.isfile(f2)
