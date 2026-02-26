# coding=utf-8
"""Unit tests for lib/peaks.py"""
import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.peaks import (
    Peak, get_peaks_size, get_common_peaks, merge_common_peaks,
    randomize_peaks, _add_peaks, _sort_peaks_list, get_summit,
    _digit_exprs_p_norm, normalize_peaks, cal_peaks_read_density,
    use_merged_peaks_fit_model, get_peaks_mavalues,
    get_peaks_normed_mavalues, get_peaks_pvalues,
)


class TestPeakInit:
    def test_basic_creation(self):
        pk = Peak('chr1', 100, 200)
        assert pk.chrm == 'chr1'
        assert pk.start == 100
        assert pk.end == 200
        assert pk.summit == 151  # (100+200)//2 + 1

    def test_creation_with_summit(self):
        pk = Peak('chr1', 100, 200, 50)
        assert pk.summit == 150  # smt + s = 50 + 100

    def test_default_values(self):
        pk = Peak('chr1', 0, 100)
        assert pk.read_count1 == 0
        assert pk.read_density1 == 0.
        assert pk.normed_read_density1 == 0.  # fixed: was tuple (0, 0.)
        assert pk.read_count2 == 0
        assert pk.mvalue == 0.
        assert pk.pvalue == 0.

    def test_integer_division_summit(self):
        pk = Peak('chr1', 1, 4)
        assert pk.summit == 3  # (1+4)//2 + 1 = 3
        assert isinstance(pk.summit, int)


class TestIsOverlap:
    def test_overlap_partial(self):
        pk1 = Peak('chr1', 100, 200)
        pk2 = Peak('chr1', 150, 250)
        assert pk1.isoverlap(pk2) is True

    def test_no_overlap(self):
        pk1 = Peak('chr1', 100, 200)
        pk2 = Peak('chr1', 300, 400)
        assert pk1.isoverlap(pk2) is False

    def test_adjacent_no_overlap(self):
        pk1 = Peak('chr1', 100, 200)
        pk2 = Peak('chr1', 200, 300)
        assert pk1.isoverlap(pk2) is False

    def test_containment_other_contains_self(self):
        """Fixed bug: other_pk fully contains self should return True"""
        pk1 = Peak('chr1', 150, 180)
        pk2 = Peak('chr1', 100, 300)
        assert pk1.isoverlap(pk2) is True

    def test_containment_self_contains_other(self):
        pk1 = Peak('chr1', 100, 300)
        pk2 = Peak('chr1', 150, 180)
        assert pk1.isoverlap(pk2) is True

    def test_identical_peaks(self):
        pk1 = Peak('chr1', 100, 200)
        pk2 = Peak('chr1', 100, 200)
        assert pk1.isoverlap(pk2) is True


class TestGetPeaksSize:
    def test_empty(self):
        assert get_peaks_size({}) == 0

    def test_single_chrm(self):
        pks = {'chr1': [Peak('chr1', 0, 100), Peak('chr1', 200, 300)]}
        assert get_peaks_size(pks) == 2

    def test_multi_chrm(self):
        pks = {
            'chr1': [Peak('chr1', 0, 100)],
            'chr2': [Peak('chr2', 0, 100), Peak('chr2', 200, 300)],
        }
        assert get_peaks_size(pks) == 3


class TestGetCommonPeaks:
    def test_all_common(self):
        pks1 = {'chr1': [Peak('chr1', 100, 200)]}
        pks2 = {'chr1': [Peak('chr1', 150, 250)]}
        u1, c1, u2, c2 = get_common_peaks(pks1, pks2)
        assert get_peaks_size(c1) == 1
        assert get_peaks_size(c2) == 1
        assert get_peaks_size(u1) == 0
        assert get_peaks_size(u2) == 0

    def test_all_unique(self):
        pks1 = {'chr1': [Peak('chr1', 100, 200)]}
        pks2 = {'chr1': [Peak('chr1', 300, 400)]}
        u1, c1, u2, c2 = get_common_peaks(pks1, pks2)
        assert get_peaks_size(c1) == 0
        assert get_peaks_size(u1) == 1
        assert get_peaks_size(u2) == 1

    def test_different_chromosomes(self):
        pks1 = {'chr1': [Peak('chr1', 100, 200)]}
        pks2 = {'chr2': [Peak('chr2', 100, 200)]}
        u1, c1, u2, c2 = get_common_peaks(pks1, pks2)
        assert get_peaks_size(u1) == 1
        assert get_peaks_size(u2) == 1
        assert get_peaks_size(c1) == 0
        assert get_peaks_size(c2) == 0


class TestAddPeaks:
    def test_merge_same_chrm(self):
        pks1 = {'chr1': [Peak('chr1', 0, 100)]}
        pks2 = {'chr1': [Peak('chr1', 200, 300)]}
        merged = _add_peaks(pks1, pks2)
        assert len(merged['chr1']) == 2

    def test_merge_different_chrm(self):
        pks1 = {'chr1': [Peak('chr1', 0, 100)]}
        pks2 = {'chr2': [Peak('chr2', 0, 100)]}
        merged = _add_peaks(pks1, pks2)
        assert 'chr1' in merged
        assert 'chr2' in merged


class TestSortPeaksList:
    def test_sort_by_start(self):
        pks = [Peak('chr1', 300, 400), Peak('chr1', 100, 200), Peak('chr1', 200, 300)]
        sorted_pks = _sort_peaks_list(pks, 'start')
        assert sorted_pks[0].start == 100
        assert sorted_pks[1].start == 200
        assert sorted_pks[2].start == 300


class TestDigitExprsPNorm:
    def test_small_values(self):
        p = _digit_exprs_p_norm(5, 5)
        assert 0 < p <= 1

    def test_large_values(self):
        p = _digit_exprs_p_norm(100, 50)
        assert 0 < p <= 1

    def test_zero_x(self):
        p = _digit_exprs_p_norm(0, 5)
        assert 0 < p <= 1

    def test_equal_values(self):
        p = _digit_exprs_p_norm(10, 10)
        assert 0 < p <= 1


class TestGetSummit:
    def test_two_summits(self):
        a, b = get_summit([100, 200])
        assert a == 100
        assert b == 200

    def test_farthest_pair(self):
        """get_summit finds the pair with the largest gap (for summit distance measurement)."""
        a, b = get_summit([100, 500, 510, 900])
        assert a == 100
        assert b == 500


class TestRandomizePeaks:
    def test_preserves_structure(self):
        pks = {'chr1': [Peak('chr1', 100, 200), Peak('chr1', 300, 500)]}
        rand_pks = randomize_peaks(pks)
        assert 'chr1' in rand_pks
        assert len(rand_pks['chr1']) == 2

    def test_preserves_lengths(self):
        pks = {'chr1': [Peak('chr1', 100, 300)]}
        rand_pks = randomize_peaks(pks)
        pk = rand_pks['chr1'][0]
        assert pk.end - pk.start == 200
