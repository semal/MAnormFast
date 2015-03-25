# coding=utf-8
from bisect import bisect_left, bisect_right
from math import log, exp
from scipy.misc import comb
import random
import numpy as np
from statsmodels import api as sm


class Peak(object):
    """
    Peak是蛋白质结合在基因组上的信号
    """
    def __init__(self, c, s, e, smt=None):
        self.chrm = c
        self.start = s
        self.end = e
        if smt is None:
            self.summit = (s + e) / 2 + 1
        else:
            self.summit = smt + s
        # MAnorm因为输入是两个read文件，对一个peak用这两个read文件计算两次read count
        self.read_count1, self.read_density1 = 0, 0.
        self.normed_read_density1 = 0, 0.
        self.read_count2, self.read_density2 = 0, 0.
        self.mvalue, self.avalue = 0., 0.
        self.normed_mvalue, self.normed_avalue, self.pvalue = 0., 0., 0.

    def set_summit(self, smt):
        self.summit = smt

    def __cal_read_count(self, reads_pos, ext):
        """
        根据给定的reads的位点信息计算落在此peak的read数
        :param reads_pos: 不同染色体reads的位点升序list组成的字典
        :return: 落在此peak的read数
        """
        if self.chrm not in reads_pos.keys():
            return 0
        re_start, re_end = self.summit - ext - 1, self.summit + ext
        si = bisect_left(reads_pos[self.chrm], re_start)
        ei = bisect_right(reads_pos[self.chrm], re_end)
        # print '%d(%d)--%d(%d)' % (si, re_start, ei, re_end)
        try:
            if re_end == reads_pos[self.chrm][ei]:
                return ei - si + 1
            else:
                return ei - si
        except IndexError:
            return ei - si

    def __cal_read_density(self, reads_pos, ext):
        read_count = self.__cal_read_count(reads_pos, ext) + 1  # 加1是为了保证每个peak的read count初始为1
        read_density = read_count * 1000. / (2. * ext)
        return read_count, read_density

    def cal_read_density(self, reads_pos1, reads_pos2, ext):
        self.read_count1, self.read_density1 = self.__cal_read_density(reads_pos1, ext)
        self.read_count2, self.read_density2 = self.__cal_read_density(reads_pos2, ext)
        self.mvalue = log(self.read_density1, 2) - log(self.read_density2, 2)
        self.avalue = (log(self.read_density1, 2) + log(self.read_density2, 2)) / 2

    def normalize_mavalue(self, ma_fit):
        """
        ma_fit: R2 = ma_fit[0] * R1 + ma_fit[1]
        """
        # key method for normalizing read density
        normed_log2_density1 = \
            (2. - ma_fit[1]) * log(self.read_density1, 2) / (2. + ma_fit[1]) - 2. * ma_fit[0] / (2. + ma_fit[1])
        self.normed_read_density1 = 2 ** normed_log2_density1

        self.normed_mvalue = normed_log2_density1 - log(self.read_density2, 2)
        self.normed_avalue = (normed_log2_density1 + log(self.read_density2, 2)) / 2.
        self.pvalue = _digit_exprs_p_norm(2. ** normed_log2_density1, self.read_density2)

    def isoverlap(self, other_pk):
        if self.start <= other_pk.start < self.end or self.start < other_pk.end <= self.end:
            return True
        else:
            return False


def _digit_exprs_p_norm(x, y):
    """
    利用read count相对于随机情况下计算p值
    """
    xx = round(x)
    if xx == 0:
        xx = 1
    yy = int(round(y))
    if xx + yy < 20.0:  # if x + y small
        p1 = round(comb(xx + yy, xx)) * 2 ** - (xx + yy + 1.0)
        p2 = round(comb(xx + yy, yy)) * 2 ** - (xx + yy + 1.0)
        return max(p1, p2)
    else:  # if x + y large, use the approximate equations
        log_p = (xx + yy) * log(xx + yy) - xx * log(xx) - yy * log(yy) - (xx + yy + 1.0) * log(2.0)
        if log_p < -500:
            log_p = -500
        p = exp(log_p)
        return p


def get_peaks_size(pks):
    """
    获取peaks字典的数据长度
    """
    i = 0
    for key in pks.keys():
        for _ in pks[key]:
            i += 1
    return i


def cal_peaks_read_density(pks, reads_pos1, reads_pos2, ext):
    """
    计算pks字典中所有peak的read density
    :param pks: pks字典
    """
    for key in pks.keys():
        [pk.cal_read_density(reads_pos1, reads_pos2, ext) for pk in pks[key]]


def normalize_peaks(pks, ma_fit):
    """
    :param pks: peaks字典
    :param ma_fit: 用来标准化peaks的M值和A值的模型参数
    """
    for key in pks.keys():
        [pk.normalize_mavalue(ma_fit) for pk in pks[key]]


def get_common_peaks(pks1, pks2):
    """
    通过看两组peaks之间是否有重复区域找出pks1与pks2共有的peak
    :param pks1: pks1字典
    :param pks2: pks2字典
    :return: common and unique peaks
    """
    pks1_unique, pks1_common, pks2_unique, pks2_common = {}, {}, {}, {}
    common_chrm = set(pks1.keys()).intersection(pks2.keys())
    pks1_unique_chrm, pks2_unique_chrm = \
        set(pks1.keys()).difference(common_chrm), set(pks2.keys()).difference(common_chrm)
    for chrm in pks1_unique_chrm:
        pks1_unique[chrm] = pks1[chrm]
    for chrm in pks2_unique_chrm:
        pks2_unique[chrm] = pks2[chrm]
    for chrm in common_chrm:
        pks1_unique[chrm], pks1_common[chrm], pks2_unique[chrm], pks2_common[chrm] = \
            __get_common_peaks(pks1[chrm], pks2[chrm])
    return pks1_unique, pks1_common, pks2_unique, pks2_common


def __get_common_peaks(pks1_chrm, pks2_chrm):
    """
    两组peaks同一条染色体中peaks内找common peaks
    :param pks1_chrm: pks1的chri染色体上的peaks
    :param pks2_chrm: pks2的chri染色体上的peaks
    :return: common and unique peaks
    """
    flag1, flag2 = np.zeros(len(pks1_chrm)), np.zeros(len(pks2_chrm))
    pks2_chrm_start = np.array([pk.start for pk in pks2_chrm])
    pks2_chrm_end = np.array([pk.end for pk in pks2_chrm])
    for i, pk in enumerate(pks1_chrm):
        claus = 1.0 * (pk.end - pks2_chrm_start) * (pks2_chrm_end - pk.start)
        overlap_locs = np.where(claus > 0)[0]
        if overlap_locs.size > 0:
            flag1[i] = 1
            flag2[overlap_locs] = 1

    pks1_chrm_unique, pks1_chrm_common = [], []
    for i, v in enumerate(flag1):
        pks1_chrm_unique.append(pks1_chrm[i]) if v == 0 else pks1_chrm_common.append(pks1_chrm[i])

    pks2_chrm_unique, pks2_chrm_common = [], []
    for i, v in enumerate(flag2):
        pks2_chrm_unique.append(pks2_chrm[i]) if v == 0 else pks2_chrm_common.append(pks2_chrm[i])

    return pks1_chrm_unique, pks1_chrm_common, pks2_chrm_unique, pks2_chrm_common


def randomize_peaks(pks):
    """
    通过随机模拟出和pks类似的random_pks
    :param pks: 被模拟的peaks
    :return: 模拟后的peaks
    """
    randomized_pks = {}
    for key in pks.keys():
        randomized_pks[key] = []
        pks_chrm = pks[key]
        starts, ends = [pk.start for pk in pks_chrm], [pk.end for pk in pks_chrm]
        lengths = [e - s for e, s in zip(ends, starts)]
        min_start, max_end = min(starts), max(ends)
        for length in lengths:
            randomized_start = random.randint(min_start, max_end)
            randomized_pks[key].append(Peak(key, randomized_start, randomized_start + length))
    return randomized_pks


def merge_common_peaks(pks1_common, pks2_common):
    """
    合并common peaks
    """
    merged_pks = {}
    summit_dist = {}
    for key in pks1_common.keys():
        mix_pks_chrm = pks1_common[key] + pks2_common[key]
        merged_pks[key], summit_dist[key] = __merge_sorted_peaks_list(_sort_peaks_list(mix_pks_chrm))
    return merged_pks, summit_dist


def _sort_peaks_list(pks_list, start_or_summit='start'):
    """
    将peaks列表进行排序
    """
    if start_or_summit == 'start':
        return [pks_list[loc] for loc in np.argsort([pk.start for pk in pks_list])]
    elif start_or_summit == 'summit':
        return [pks_list[loc] for loc in np.argsort([pk.summit for pk in pks_list])]


def _add_peaks(pks1, pks2):
    """
    将peaks中对应的key的值扩展
    :param pks1: peaks1字典
    :param pks2: peaks2字典
    :return: 新的peaks字典
    """
    peaks = {}
    keys = set(pks1.keys() + pks2.keys())
    for key in keys:
        value = []
        if key in pks1.keys():
            value += pks1[key]
        if key in pks2.keys():
            value += pks2[key]
        peaks[key] = value
    return peaks


def __merge_sorted_peaks_list(sorted_pks_list):
    # print 'sorted peaks length: %d' % len(sorted_pks_list)
    merged_pks, smt_dists = [], []

    def get_a_merged_peak(head_loc):
        # print head_loc
        merged_pk_num = 0
        merged_pk = sorted_pks_list[head_loc]
        summits = [merged_pk.summit]
        for pk in sorted_pks_list[head_loc + 1:]:
            if merged_pk.isoverlap(pk):
                merged_pk = Peak(pk.chrm, min(merged_pk.start, pk.start), max(merged_pk.end, pk.end))
                summits.append(pk.summit)
                merged_pk_num += 1
            else:
                # print summits
                sorted_summits = sorted(summits)
                smt_a, smt_b = get_summit(sorted_summits)
                smt_dist = smt_b - smt_a
                merged_pk.set_summit((smt_a + smt_b) / 2 + 1)
                new_head_loc = head_loc + merged_pk_num + 1
                return new_head_loc, merged_pk, smt_dist
        sorted_summits = sorted(summits)
        smt_a, smt_b = get_summit(sorted_summits)
        smt_dist = smt_b - smt_a
        merged_pk.set_summit((smt_a + smt_b) / 2 + 1)
        new_head_loc = head_loc + merged_pk_num + 1
        return new_head_loc, merged_pk, smt_dist

    h_loc = 0
    while h_loc < len(sorted_pks_list):
        h_loc, m_pk, smt_d = get_a_merged_peak(h_loc)
        merged_pks.append(m_pk)
        smt_dists.append(smt_d)
    return merged_pks, smt_dists


def get_summit(sorted_summits):
    smt_starts, smt_ends = sorted_summits[:-1], sorted_summits[1:]
    smt_a, smt_b = smt_starts[0], smt_ends[0]
    for s, e in zip(smt_starts, smt_ends):
        if s - e < smt_a - smt_b:
            smt_a, smt_b = s, e
    return smt_a, smt_b


def use_merged_peaks_fit_model(merged_pks, summit_dist, min_summit_dist):
    """
    利用合并后的peaks来拟合模型
    """
    selected_pks = {}
    for key in merged_pks.keys():
        selected_pks[key] = []
        for pk, smt_d in zip(merged_pks[key], summit_dist[key]):
            if smt_d <= min_summit_dist:
                selected_pks[key].append(pk)
    mvalues, avalues = get_peaks_mavalues(selected_pks)
    fit_x = np.array(avalues)
    fit_y = np.array(mvalues)
    idx_sel = np.where((fit_y >= -10) & (fit_y <= 10))[0]

    # fit the model
    x = sm.add_constant(fit_x[idx_sel])
    y = fit_y[idx_sel]
    ma_fit = sm.RLM(y, x).fit().params
    return ma_fit


def get_peaks_mavalues(pks):
    """
    返回peaks所有的m, a值对
    :param pks: peaks字典
    :return: mvalues, avalues
    """
    mvalues, avalues = [], []
    for key in pks.keys():
        for pk in pks[key]:
            mvalues.append(pk.mvalue), avalues.append(pk.avalue)

    return mvalues, avalues


def get_peaks_normed_mavalues(pks):
    """
    返回peaks normalization之后所有的m, a值对
    :param pks: peaks字典
    :return: normed_mvalues, normed_avalues
    """
    normed_mvalues, normed_avalues = [], []
    for key in pks.keys():
        for pk in pks[key]:
            normed_mvalues.append(pk.normed_mvalue), normed_avalues.append(pk.normed_avalue)

    return normed_mvalues, normed_avalues


def get_peaks_pvalues(pks):
    """
    返回peaks normalization之后所有的p值
    :param pks: peaks字典
    :return: pvalues
    """
    pvalues = []
    for key in pks.keys():
        for pk in pks[key]:
            pvalues.append(pk.pvalue)

    return pvalues