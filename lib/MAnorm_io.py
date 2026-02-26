# coding=utf-8
from __future__ import print_function, division

import logging
import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from numpy.ma import log2, log10

from .peaks import (Peak, get_peaks_mavalues, get_peaks_normed_mavalues,
                    get_peaks_pvalues, _add_peaks, _sort_peaks_list)

logger = logging.getLogger(__name__)


def _get_reads_position(reads_fp, shift):
    """
    从read文件中获取所有read的点位置信息，我们将read的位置当成点来处理。
    read文件要求前三列是chr, start, end,第六列是strand(bed格式), 列之间以\\t分隔
    :param shift: <int>平移量
    :param reads_fp: read文件路径
    :return: 所有read记录的位点
    """
    position = {}
    with open(reads_fp) as fi:
        for li in fi:
            sli = li.split('\t')
            chrm, start, end, strand = \
                sli[0].strip(), int(sli[1]), int(sli[2]), sli[5].strip()
            pos = start + shift if strand == '+' else end - shift
            if chrm not in position:
                position[chrm] = []
            position[chrm].append(pos)
    return {key: sorted(position[key]) for key in position}


def _get_read_length(reads_fp):
    """
    通过读取第一行的read信息获取此read文件中read的长度。
    :param reads_fp: read文件
    :return: read长度
    """
    with open(reads_fp) as fi:
        for li in fi:
            sli = li.split('\t')
            return int(sli[2]) - int(sli[1])


def read_reads(reads_fp, shift):
    return _get_reads_position(reads_fp, shift)


def _read_peaks(peak_fp):
    """
    peak文件要求前三列分别是chrm, start, end. 可以有第四列summit,
    summit要求是相对于start的位置（和macs的结果一样）
    以#开头的行会跳过，列之间用制表符分隔开
    :param peak_fp: peak文件路径
    :return: Peak的字典
    """
    pks = {}
    with open(peak_fp) as fi:
        for li in fi:
            if li.startswith('#'):
                continue
            sli = li.split('\t')
            chrm = sli[0].strip()
            try:
                pk = Peak(chrm, int(sli[1]), int(sli[2]), int(sli[3].strip()))
            except (IndexError, ValueError):
                pk = Peak(chrm, int(sli[1]), int(sli[2]))
            if chrm not in pks:
                pks[chrm] = []
            pks[chrm].append(pk)
    return pks


def _read_macs_xls_peaks(peak_fp):
    """
    读取MACS xls格式的peak文件
    :param peak_fp: macs xls peaks file path
    :return: peaks字典
    """
    pks = {}
    with open(peak_fp) as fi:
        for li in fi:
            if li.startswith('#'):
                continue
            sli = li.split('\t')
            chrm = sli[0].strip()
            try:
                pk = Peak(chrm, int(sli[1]), int(sli[2]), int(sli[4]))
            except (IndexError, ValueError):
                continue
            if chrm not in pks:
                pks[chrm] = []
            pks[chrm].append(pk)
    return pks


def read_peaks(peak_fp):
    if peak_fp.endswith('.xls'):
        return _read_macs_xls_peaks(peak_fp)
    else:
        return _read_peaks(peak_fp)


def _write_peaks_block(fo, pks, group_name, rds1_name, rds2_name):
    """通用的 peak 写入函数，减少代码重复"""
    fmt = '\t'.join(['%s', '%d', '%d', '%d', '%f', '%f', '%s', '%s', '%f', '%f'])
    for chrm in pks:
        for pk in pks[chrm]:
            cnt = (pk.chrm, pk.start, pk.end, pk.summit - pk.start,
                   pk.normed_mvalue, pk.normed_avalue, str(pk.pvalue), group_name,
                   pk.normed_read_density1, pk.read_density2)
            fo.write(fmt % cnt + '\n')


def _write_header(fo, rds1_name, rds2_name):
    """写入输出文件的表头"""
    header = '\t'.join(['chr', 'start', 'end', 'summit', 'M_value', 'A_value', 'P_value', 'Peak_Group',
                        'normalized_read_density_in_%s' % rds1_name,
                        'normalized_read_density_in_%s' % rds2_name])
    fo.write(header + '\n')


def output_normalized_peaks(pks_unique, pks_common, file_name, rds1_name, rds2_name):
    """输出MAnorm标准化后的结果"""
    with open(file_name, 'w') as fo:
        _write_header(fo, rds1_name, rds2_name)
        _write_peaks_block(fo, pks_unique, 'unique', rds1_name, rds2_name)
        _write_peaks_block(fo, pks_common, 'common', rds1_name, rds2_name)


def output_3set_normalized_peaks(pks1_unique, merged_pks, pks2_unique,
                                 file_name, pks1_name, pks2_name,
                                 rds1_name, rds2_name):
    """输出pks1_unique, pks2_unique, merged_pks所有的peaks"""
    with open(file_name, 'w') as fo:
        _write_header(fo, rds1_name, rds2_name)
        _write_peaks_block(fo, pks1_unique, '%s_unique' % pks1_name, rds1_name, rds2_name)
        _write_peaks_block(fo, merged_pks, 'merged_common_peak', rds1_name, rds2_name)
        _write_peaks_block(fo, pks2_unique, '%s_unique' % pks2_name, rds1_name, rds2_name)


def draw_figs_to_show_data(pks1_uni, pks2_uni, merged_pks, pks1_name,
                           pks2_name, ma_fit, reads1_name, reads2_name,
                           output_dir='.'):
    """draw four figures to show data before and after rescaled"""
    pks_3set = [pks1_uni, pks2_uni, merged_pks]
    pks1_name = ' '.join([pks1_name, 'unique'])
    pks2_name = ' '.join([pks2_name, 'unique'])
    merged_pks_name = 'merged common peaks'
    pks_names = [pks1_name, pks2_name, merged_pks_name]
    colors = 'bgr'
    a_max = 0
    a_min = 10000
    plt.figure(1).set_size_inches(16, 12)
    for (idx, pks) in enumerate(pks_3set):
        mvalues, avalues = get_peaks_mavalues(pks)
        if len(avalues) != 0:
            a_max = max(max(avalues), a_max)
            a_min = min(min(avalues), a_min)
        plt.scatter(avalues, mvalues, s=10, c=colors[idx])
    plt.xlabel('A value')
    plt.ylabel('M value')
    plt.grid(axis='y')
    plt.legend(pks_names, loc='best')
    plt.title('before rescale')

    x = np.arange(a_min, a_max, 0.01)
    y = ma_fit[1] * x + ma_fit[0]
    plt.plot(x, y, '-', color='k')
    plt.savefig(os.path.join(output_dir, 'before_rescale.png'))

    plt.figure(2).set_size_inches(16, 12)
    rd_min = 1000
    rd_max = 0
    rds_density1, rds_density2 = [], []
    for key in merged_pks:
        for pk in merged_pks[key]:
            rds_density1.append(pk.read_density1)
            rds_density2.append(pk.read_density2)
    rd_max = max(max(log2(rds_density1)), rd_max)
    rd_min = min(min(log2(rds_density1)), rd_min)
    plt.scatter(log2(rds_density1), log2(rds_density2), s=10, c='r', label=merged_pks_name, alpha=0.5)
    plt.xlabel(' log2 read density' + ' by ' + '"' + reads1_name + '" reads')
    plt.ylabel(' log2 read density' + ' by ' + '"' + reads2_name + '" reads')
    plt.grid(axis='y')
    plt.legend(loc='upper left')
    plt.title('Fitting Model via common peaks')
    rx = np.arange(rd_min, rd_max, 0.01)
    ry = (2 - ma_fit[1]) * rx / (2 + ma_fit[1]) - 2 * ma_fit[0] / (2 + ma_fit[1])
    plt.plot(rx, ry, '-', color='k')
    plt.savefig(os.path.join(output_dir, 'log2_read_density.png'))

    plt.figure(3).set_size_inches(16, 12)
    for (idx, pks) in enumerate(pks_3set):
        normed_mvalues, normed_avalues = get_peaks_normed_mavalues(pks)
        plt.scatter(normed_avalues, normed_mvalues, s=10, c=colors[idx])
    plt.xlabel('A value')
    plt.ylabel('M value')
    plt.grid(axis='y')
    plt.legend(pks_names, loc='best')
    plt.title('after rescale')
    plt.savefig(os.path.join(output_dir, 'after_rescale.png'))

    plt.figure(4).set_size_inches(16, 12)
    for (idx, pks) in enumerate(pks_3set):
        normed_mvalues, normed_avalues = get_peaks_normed_mavalues(pks)
        pval_colors = -log10(get_peaks_pvalues(pks))
        for i, c in enumerate(pval_colors):
            if c > 50:
                pval_colors[i] = 50
        plt.scatter(normed_avalues, normed_mvalues, s=10, c=pval_colors, cmap='jet')
    plt.colorbar()
    plt.grid(axis='y')
    plt.xlabel('A value')
    plt.ylabel('M value')
    plt.title('-log10(P-value)')
    plt.savefig(os.path.join(output_dir, '-log10_P-value.png'))
    plt.close()


def output_peaks_mvalue_2wig_file(pks1_uni, pks2_uni, merged_pks, comparison_name, output_dir='.'):
    """output of peaks with normed m value and p values"""
    logger.info('output wig files ...')

    peaks = _add_peaks(_add_peaks(pks1_uni, merged_pks), pks2_uni)

    mvalues_path = os.path.join(output_dir, '_'.join([comparison_name, 'peaks_Mvalues.wig']))
    with open(mvalues_path, 'w') as f_2write:
        f_2write.write('browser position chr11:5220000-5330000\n')
        f_2write.write('track type=wiggle_0 name=%s' % comparison_name +
                       ' visibility=full autoScale=on color=255,0,0 ' +
                       ' yLineMark=0 yLineOnOff=on priority=10\n')
        for chr_id in peaks:
            f_2write.write('variableStep chrom=' + chr_id + ' span=100\n')
            pks_chr = peaks[chr_id]
            sorted_pks_chr = _sort_peaks_list(pks_chr, 'summit')
            for pk in sorted_pks_chr:
                f_2write.write('\t'.join(['%d' % pk.summit, '%s\n' % str(pk.normed_mvalue)]))

    pvalues_path = os.path.join(output_dir, '_'.join([comparison_name, 'peaks_Pvalues.wig']))
    with open(pvalues_path, 'w') as f_2write:
        f_2write.write('browser position chr11:5220000-5330000\n')
        f_2write.write('track type=wiggle_0 name=%s(-log10(p-value))' % comparison_name +
                       ' visibility=full autoScale=on color=255,0,0 ' +
                       ' yLineMark=0 yLineOnOff=on priority=10\n')
        for chr_id in peaks:
            f_2write.write('variableStep chrom=' + chr_id + ' span=100\n')
            pks_chr = peaks[chr_id]
            sorted_pks_chr = _sort_peaks_list(pks_chr, 'summit')
            for pk in sorted_pks_chr:
                f_2write.write('\t'.join(['%d' % pk.summit, '%s\n' % str(-log10(pk.pvalue))]))


def output_unbiased_peaks(pks1_uni, pks2_uni, merged_pks, unbiased_mvalue, overlap_dependent, output_dir='.'):
    """输出没有显著差异的peak"""
    logger.info('define unbiased peaks')

    if not overlap_dependent:
        pks = _add_peaks(_add_peaks(pks1_uni, merged_pks), pks2_uni)
        name = 'all_peaks'
    else:
        pks = merged_pks
        name = 'merged_common_peaks'

    filepath = os.path.join(output_dir, 'unbiased_peaks_of_%s.bed' % name)
    i = 0
    with open(filepath, 'w') as file_bed:
        for key in pks:
            for pk in pks[key]:
                if abs(pk.normed_mvalue) < unbiased_mvalue:
                    i += 1
                    line = '\t'.join([pk.chrm, '%d' % pk.start, '%d' % pk.end, 'from_%s_%d' % (name, i),
                                      '%s\n' % str(pk.normed_mvalue)])
                    file_bed.write(line)
    logger.info('filter %d unbiased peaks', i)


def output_biased_peaks(pks1_uni, pks2_uni, merged_pks, biased_mvalue,
                        biased_pvalue, overlap_dependent, output_dir='.'):
    """输出有显著差异的peaks"""
    logger.info('define biased peaks')

    if not overlap_dependent:
        pks = _add_peaks(_add_peaks(pks1_uni, merged_pks), pks2_uni)
        name = 'all_peaks'
    else:
        pks = _add_peaks(pks1_uni, pks2_uni)
        name = 'unique_peaks'

    over_path = os.path.join(output_dir, 'M_over_%.2f_biased_peaks_of_%s.bed' % (biased_mvalue, name))
    less_path = os.path.join(output_dir, 'M_less_-%.2f_biased_peaks_of_%s.bed' % (biased_mvalue, name))
    i, j = 0, 0
    with open(over_path, 'w') as file_bed_over, open(less_path, 'w') as file_bed_less:
        for key in pks:
            for pk in pks[key]:
                if pk.pvalue < biased_pvalue:
                    if pk.normed_mvalue > biased_mvalue:
                        i += 1
                        line = '\t'.join([pk.chrm, '%d' % pk.start, '%d' % pk.end, 'from_%s_%d' % (name, i),
                                          '%s\n' % str(pk.normed_mvalue)])
                        file_bed_over.write(line)
                    if pk.normed_mvalue < -biased_mvalue:
                        j += 1
                        line = '\t'.join([pk.chrm, '%d' % pk.start, '%d' % pk.end, 'from_%s_%d' % (name, j),
                                          '%s\n' % str(pk.normed_mvalue)])
                        file_bed_less.write(line)
    logger.info('filter %d biased peaks', i + j)
