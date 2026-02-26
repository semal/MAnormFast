# coding=utf-8
"""Command-line interface for MAnormFast."""
from __future__ import print_function, division

import argparse
import logging
import os
import sys
import time

import numpy as np

from .MAnorm_io import (read_peaks, read_reads,
                        output_normalized_peaks, output_3set_normalized_peaks,
                        draw_figs_to_show_data, output_peaks_mvalue_2wig_file,
                        output_unbiased_peaks, output_biased_peaks)
from .peaks import (get_common_peaks, get_peaks_size, merge_common_peaks,
                    cal_peaks_read_density, use_merged_peaks_fit_model,
                    normalize_peaks, randomize_peaks)
from . import version

logger = logging.getLogger('MAnormFast')


def _parse_args():
    parser = argparse.ArgumentParser(
        description='MAnormFast: quantitative comparison of ChIP-Seq data sets'
    )
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument(
        '--p1', dest='pkf1', required=True,
        help='numerator peaks file path. It should contain at least three '
             'columns: chromosome name, start and end position of each peak. '
             'If the fourth column exists, it should be summit position '
             '(relative to peak start).'
    )
    parser.add_argument(
        '--p2', dest='pkf2', required=True,
        help='denominator peaks file path'
    )
    parser.add_argument(
        '--r1', dest='rdf1', required=True,
        help='numerator reads file path (BED format). The first, second, third '
             'and sixth columns are the chromosome, start, end and strand.'
    )
    parser.add_argument(
        '--r2', dest='rdf2', required=True,
        help='denominator reads file path'
    )
    parser.add_argument(
        '--s1', dest='sft1', type=int, default=100,
        help='read shift size of sample 1 (default: 100)'
    )
    parser.add_argument(
        '--s2', dest='sft2', type=int, default=100,
        help='read shift size of sample 2 (default: 100)'
    )
    parser.add_argument(
        '-n', dest='random_time', type=int, default=5,
        help='number of random permutations (default: 5)'
    )
    parser.add_argument(
        '-o', dest='output', required=True,
        help='output folder name'
    )
    parser.add_argument(
        '-e', dest='extension', type=int, default=1000,
        help='extension size of peak window (default: 1000). '
             'Recommend 1000 for histone marks, 500 for TF or DNase-seq.'
    )
    parser.add_argument(
        '-d', dest='smt_dist', type=int, default=None,
        help='summit-to-summit distance cutoff (default: extension/2)'
    )
    parser.add_argument(
        '-s', dest='output_no_merge', action='store_true', default=False,
        help='skip merging common peaks'
    )
    parser.add_argument(
        '-v', dest='overlap_dependent', action='store_true', default=False,
        help='use overlap-dependent filtering for biased/unbiased peaks'
    )
    parser.add_argument(
        '-p', dest='biased_p', type=float, default=0.01,
        help='P-value cutoff for biased peaks (default: 0.01)'
    )
    parser.add_argument(
        '-m', dest='biased_m', type=float, default=1.,
        help='M-value cutoff for biased peaks (default: 1.0)'
    )
    parser.add_argument(
        '-u', dest='unbiased_m', type=float, default=1.,
        help='M-value cutoff for unbiased peaks (default: 1.0)'
    )
    return parser.parse_args()


def _validate_files(*filepaths):
    """验证输入文件是否存在"""
    for fp in filepaths:
        if not os.path.isfile(fp):
            sys.exit('Error: File not found: %s' % fp)


def command():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    values = _parse_args()
    numerator_peaks_fp = values.pkf1
    denominator_peaks_fp = values.pkf2
    numerator_reads_fp = values.rdf1
    denominator_reads_fp = values.rdf2
    shift1, shift2 = values.sft1, values.sft2
    random_time = values.random_time
    output_folder = values.output
    ext = values.extension
    min_smt_dist = values.smt_dist if values.smt_dist is not None else ext // 2
    output_no_merge = values.output_no_merge
    overlap_dependent = values.overlap_dependent
    biased_pvalue = values.biased_p
    biased_mvalue = values.biased_m
    unbiased_mvalue = values.unbiased_m

    _validate_files(numerator_peaks_fp, denominator_peaks_fp,
                    numerator_reads_fp, denominator_reads_fp)

    try:
        os.mkdir(output_folder)
    except OSError:
        sys.exit('Error: folder name "%s" already exists, please change the '
                 'output folder name!' % output_folder)

    start = time.perf_counter()

    pks1_fn = os.path.basename(numerator_peaks_fp)
    pks2_fn = os.path.basename(denominator_peaks_fp)
    rds1_fn = os.path.basename(numerator_reads_fp)
    rds2_fn = os.path.basename(denominator_reads_fp)

    logger.info('\n'
                '# ARGUMENT LIST:\n'
                '# numerator peaks file=%s\n'
                '# denominator peaks file=%s\n'
                '# numerator reads file=%s\n'
                '# denominator reads file=%s\n'
                '# shift size of numerator reads=%d\n'
                '# shift size of denominator reads=%d\n'
                '# extension size of peak=%d\n'
                '# min summit to summit distance=%d\n'
                '# output folder name=%s',
                pks1_fn, pks2_fn, rds1_fn, rds2_fn,
                shift1, shift2, ext, min_smt_dist, output_folder)

    pks1_fn = pks1_fn.split('.')[0].replace(' ', '_')
    pks2_fn = pks2_fn.split('.')[0].replace(' ', '_')
    rds1_fn = rds1_fn.split('.')[0].replace(' ', '_')
    rds2_fn = rds2_fn.split('.')[0].replace(' ', '_')

    logger.info('Reading Data, please wait for a while...')
    pks1 = read_peaks(numerator_peaks_fp)
    pks2 = read_peaks(denominator_peaks_fp)
    reads_pos1 = read_reads(numerator_reads_fp, shift1)
    reads_pos2 = read_reads(denominator_reads_fp, shift2)

    logger.info('Step1: Classify the 2 peaks by overlap')
    pks1_uniq, pks1_com, pks2_uniq, pks2_com = get_common_peaks(pks1, pks2)
    logger.info('%s: %d(unique) %d(common)', pks1_fn, get_peaks_size(pks1_uniq), get_peaks_size(pks1_com))
    logger.info('%s: %d(unique) %d(common)', pks2_fn, get_peaks_size(pks2_uniq), get_peaks_size(pks2_com))

    logger.info('Step2: Random overlap testing, test time is %d', random_time)
    fcs = []
    for _ in range(random_time):
        pks2_random = randomize_peaks(pks2)
        pks1_com_new = get_common_peaks(pks1, pks2_random)[1]
        fcs.append(
            1. * get_peaks_size(pks1_com) / (get_peaks_size(pks1_com_new) + 0.1)
        )
    logger.info('fold change: mean=%f, std=%f', np.array(fcs).mean(), np.array(fcs).std())

    logger.info('Step3: Merging common peaks')
    merged_pks, summit2summit_dist = merge_common_peaks(pks1_com, pks2_com)
    logger.info('merged peaks: %d', get_peaks_size(merged_pks))
    if get_peaks_size(merged_pks) == 0:
        sys.exit('Error: No common peaks!')

    logger.info('Step4: Calculating peaks read density')
    cal_peaks_read_density(pks1, reads_pos1, reads_pos2, ext)
    cal_peaks_read_density(pks2, reads_pos1, reads_pos2, ext)
    cal_peaks_read_density(merged_pks, reads_pos1, reads_pos2, ext)

    logger.info('Step5: Using merged common peaks to fitting all peaks')
    ma_fit = use_merged_peaks_fit_model(
        merged_pks, summit2summit_dist, min_smt_dist
    )
    if ma_fit[0] >= 0:
        logger.info('Model for normalization: M = %f * A + %f', ma_fit[1], ma_fit[0])
    else:
        logger.info('Model for normalization: M = %f * A - %f', ma_fit[1], abs(ma_fit[0]))

    logger.info('Step6: Normalizing all peaks')
    normalize_peaks(pks1, ma_fit)
    normalize_peaks(pks2, ma_fit)
    normalize_peaks(merged_pks, ma_fit)

    logger.info('Step7: Output result')

    if output_no_merge:
        output_normalized_peaks(
            pks1_uniq, pks1_com,
            os.path.join(output_folder, pks1_fn + '_MAvalues.xls'),
            rds1_fn, rds2_fn
        )
        output_normalized_peaks(
            pks2_uniq, pks2_com,
            os.path.join(output_folder, pks2_fn + '_MAvalues.xls'),
            rds1_fn, rds2_fn
        )
    output_3set_normalized_peaks(
        pks1_uniq, merged_pks, pks2_uniq,
        os.path.join(output_folder, output_folder + '_all_peak_MAvalues.xls'),
        pks1_fn, pks2_fn, rds1_fn, rds2_fn
    )

    fig_dir = os.path.join(output_folder, 'output_figures')
    filter_dir = os.path.join(output_folder, 'output_filters')
    wig_dir = os.path.join(output_folder, 'output_wig_files')
    os.mkdir(fig_dir)
    os.mkdir(filter_dir)
    os.mkdir(wig_dir)

    draw_figs_to_show_data(
        pks1_uniq, pks2_uniq, merged_pks,
        pks1_fn, pks2_fn, ma_fit,
        rds1_fn, rds2_fn, output_dir=fig_dir
    )
    output_peaks_mvalue_2wig_file(
        pks1_uniq, pks2_uniq, merged_pks, output_folder, output_dir=wig_dir
    )
    output_unbiased_peaks(
        pks1_uniq, pks2_uniq, merged_pks, unbiased_mvalue, overlap_dependent, output_dir=filter_dir
    )
    output_biased_peaks(
        pks1_uniq, pks2_uniq, merged_pks,
        biased_mvalue, biased_pvalue, overlap_dependent, output_dir=filter_dir
    )
    logger.info('time consumption: %.2f s\nDone!', time.perf_counter() - start)


if __name__ == '__main__':
    command()
