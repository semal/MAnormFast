# MAnormFast 优化建议

> 本文档基于对整个代码库的深入分析，从 8 个维度提出具体的优化建议。每条建议附带代码位置和优先级标注。

---

## 目录

1. [Python 3 迁移（最高优先级）](#1-python-3-迁移最高优先级)
2. [代码缺陷与正确性修复](#2-代码缺陷与正确性修复)
3. [性能优化](#3-性能优化)
4. [架构与代码设计改进](#4-架构与代码设计改进)
5. [测试体系建设](#5-测试体系建设)
6. [打包与发布改进](#6-打包与发布改进)
7. [文档完善](#7-文档完善)
8. [健壮性与错误处理](#8-健壮性与错误处理)

---

## 1. Python 3 迁移（最高优先级）

Python 2.7 已于 2020 年 1 月 1 日正式停止维护，存在安全风险，且在现代操作系统（如 Ubuntu 22.04+）中不再预装。**迁移到 Python 3 是本项目最紧迫的优化**。

### 1.1 需要修改的 Python 2 语法

| 问题 | 位置 | 修改方法 |
|------|------|----------|
| `print` 语句 | `bin/MAnormFast` 全文（约 15 处），`lib/MAnorm_io.py:278,312,331,339,366,372,377,378,391` | 改为 `print()` 函数 |
| `time.clock()` | `bin/MAnormFast:152,285`，`lib/MAnorm_io.py:384,390` | 改为 `time.perf_counter()` 或 `time.process_time()` |
| `optparse` 模块 | `bin/MAnormFast:5,19` | 迁移到 `argparse`（更现代、功能更强） |
| 隐式相对导入 | `lib/MAnorm_io.py:6-7`（`from peaks import ...`） | 改为 `from .peaks import ...` 或 `from MAnormFast.peaks import ...` |
| 字典 `.keys()` 拼接 | `lib/peaks.py:230`（`set(pks1.keys() + pks2.keys())`） | 改为 `set(list(pks1.keys()) + list(pks2.keys()))` 或 `set(pks1) | set(pks2)` |
| 整除行为 | `lib/peaks.py:19`（`(s + e) / 2`）, `bin/MAnormFast:136,260` | Python 3 中 `/` 返回浮点数，基因组坐标应使用 `//` 整除 |
| `scipy.misc.comb` | `lib/peaks.py:4` | 已迁移到 `scipy.special.comb`（`scipy.misc.comb` 在新版中已移除） |

### 1.2 迁移步骤建议

```
1. 在文件顶部添加 `from __future__ import print_function, division`（过渡阶段）
2. 使用 `2to3` 工具自动转换大部分语法
3. 手动修复整除、相对导入、已废弃 API
4. 更新 requirements.txt 中的依赖版本到支持 Python 3 的版本
5. 添加 CI 测试确保兼容性
```

---

## 2. 代码缺陷与正确性修复

### 2.1 严重 Bug：字符串比较使用 `is` 而非 `==`

**位置**: `lib/MAnorm_io.py:28`

```python
pos = start + shift if strand is '+' else end - shift
```

**问题**: `is` 比较的是对象标识（identity），不是值相等（equality）。由于 Python 的字符串驻留机制（string interning），短字符串 `'+'` 可能碰巧可以通过 `is` 比较，但这是**未定义行为**，在不同 Python 实现或版本中可能导致所有 read 位置计算全部走 `end - shift` 分支，产生错误结果。

**修复**: 改为 `strand == '+'`。

### 2.2 Bug：`normed_read_density1` 初始化为元组

**位置**: `lib/peaks.py:24`

```python
self.normed_read_density1 = 0, 0.
```

**问题**: 这行赋值的结果是一个元组 `(0, 0.0)` 而不是数值。虽然后续 `normalize_mavalue` 方法会覆盖这个值为正确的标量，但如果某个 peak 未经归一化就被输出，会导致类型错误。

**修复**: 改为 `self.normed_read_density1 = 0.`

### 2.3 `isoverlap` 方法有遗漏

**位置**: `lib/peaks.py:76-80`

```python
def isoverlap(self, other_pk):
    if self.start <= other_pk.start < self.end or self.start < other_pk.end <= self.end:
        return True
    else:
        return False
```

**问题**: 当 `other_pk` 完全包含 `self`（即 `other_pk.start < self.start` 且 `other_pk.end > self.end`）时，此方法返回 `False`，但实际上两个区间是重叠的。

**修复**:
```python
def isoverlap(self, other_pk):
    return self.start < other_pk.end and other_pk.start < self.end
```

### 2.4 错误退出码

**位置**: `bin/MAnormFast:148`

```python
exit(0)  # 文件夹已存在时退出码为 0
```

**问题**: 错误情况应返回非零退出码（如 `exit(1)`），否则在脚本/pipeline 中无法正确检测错误。

---

## 3. 性能优化

### 3.1 去掉硬编码的 `time.sleep()` 调用

**位置**: `bin/MAnormFast:196,210,218,224,236,242`

```python
time.sleep(2)  # 步骤之间的固定 2 秒等待
```

**问题**: 每个步骤之间无意义地等待 2 秒，7 个步骤共浪费约 12 秒。对于批量处理多组数据集时影响显著。

**修复**: 直接删除所有 `time.sleep()` 调用。如果是为了让用户看到输出，可以改用 `logging` 模块或 `sys.stdout.flush()`。

### 3.2 `get_peaks_size` 效率低下

**位置**: `lib/peaks.py:103-111`

```python
def get_peaks_size(pks):
    i = 0
    for key in pks.keys():
        for _ in pks[key]:
            i += 1
    return i
```

**问题**: 逐个遍历计数，时间复杂度 O(N)，且该函数在代码中被频繁调用（如 `bin/MAnormFast` 中多次调用用于打印统计信息）。

**修复**:
```python
def get_peaks_size(pks):
    return sum(len(v) for v in pks.values())
```

### 3.3 使用列表推导式产生副作用

**位置**: `lib/peaks.py:120,129`，`lib/MAnorm_io.py:291,304`

```python
[pk.cal_read_density(reads_pos1, reads_pos2, ext) for pk in pks[key]]
```

**问题**: 列表推导式用于副作用（修改对象状态），会创建一个无用的返回值列表，浪费内存。

**修复**: 改为普通 `for` 循环：
```python
for pk in pks[key]:
    pk.cal_read_density(reads_pos1, reads_pos2, ext)
```

### 3.4 重复的 `dict.keys()` 调用

多处代码使用 `for key in pks.keys()` 和 `if chrm not in reads_pos.keys()`。

**修复**: 直接使用 `for key in pks` 和 `if chrm not in reads_pos`，避免创建中间列表（Python 2 中 `.keys()` 返回列表）。

### 3.5 `__get_common_peaks` 可以使用排序+扫描优化

**位置**: `lib/peaks.py:153-178`

当前的 overlap 检测对每个 pks1 中的 peak 都与 pks2 的所有 peak 做 numpy 向量运算，时间复杂度 O(N*M)。

**优化方案**: 如果两组 peaks 都按起始位置排序，可以使用双指针/区间树（Interval Tree）将复杂度降至 O((N+M)*logN)。对于全基因组规模的数据集（数万到数十万 peaks），这会带来显著加速。

### 3.6 reads 文件解析可用 numpy/pandas 加速

**位置**: `lib/MAnorm_io.py:14-35`

当前逐行解析 BED 文件。对于大规模 reads 文件（几千万行），可以使用 `pandas.read_csv` 或 numpy 的批量加载来显著提速。

---

## 4. 架构与代码设计改进

### 4.1 使用 `os.path.join` 替代 `os.chdir`

**位置**: `bin/MAnormFast:245-274`

```python
os.chdir(output_folder)
# ... 输出文件 ...
os.chdir('output_figures')
# ... 输出图片 ...
os.chdir('..')
os.chdir('output_wig_files')
```

**问题**: 使用 `os.chdir()` 改变全局工作目录是不安全的做法：
- 在多线程环境中会导致竞争条件
- 如果中间任一步骤抛出异常，工作目录不会恢复，后续操作将在错误目录执行
- 使得代码路径难以追踪

**修复**: 使用 `os.path.join()` 构造完整路径，不改变工作目录：
```python
fig_dir = os.path.join(output_folder, 'output_figures')
os.makedirs(fig_dir)
draw_figs_to_show_data(..., output_dir=fig_dir)
```

### 4.2 文件操作未使用 `with` 语句

**位置**: `lib/MAnorm_io.py:140,165,281,294,321,348,350`

```python
fo = open(file_name, 'w')
# ... 写入操作 ...
fo.close()
```

**问题**: 如果写入过程中发生异常，文件句柄不会被正确关闭，可能导致数据丢失。

**修复**: 统一使用上下文管理器：
```python
with open(file_name, 'w') as fo:
    # ... 写入操作 ...
```

### 4.3 引入 `logging` 模块替代 `print`

当前所有状态输出都使用 `print` 语句，无法控制日志级别。

**建议**: 引入 `logging` 模块，区分 `INFO`（进度信息）、`WARNING`（异常情况）和 `ERROR`（错误），支持日志写入文件，便于批量处理时的问题排查。

### 4.4 输出函数大量重复代码

**位置**: `lib/MAnorm_io.py:136-189`

`output_normalized_peaks` 和 `output_3set_normalized_peaks` 两个函数的核心写入逻辑几乎完全相同（构造 header、格式化每行输出），只是输入的 peaks 分组不同。

**修复**: 抽取通用的 peak 写入函数，减少代码重复：
```python
def _write_peaks_to_file(fo, pks, group_name, rds1_name, rds2_name):
    for chrm in pks:
        for pk in pks[chrm]:
            # 通用写入逻辑
```

### 4.5 使用 `defaultdict` 简化字典初始化

多处代码使用 try/except KeyError 模式初始化字典：

```python
try:
    pks[chrm].append(pk)
except KeyError:
    pks[chrm] = []
    pks[chrm].append(pk)
```

**修复**: 使用 `collections.defaultdict(list)`：
```python
from collections import defaultdict
pks = defaultdict(list)
pks[chrm].append(pk)
```

### 4.6 `Peak` 类可使用 `__slots__` 优化内存

**位置**: `lib/peaks.py:10-27`

每个 `Peak` 对象有固定属性集，使用 `__slots__` 可以减少约 40-50% 的每对象内存开销。对于全基因组规模（数十万 peaks）效果显著。

```python
class Peak(object):
    __slots__ = ['chrm', 'start', 'end', 'summit', 'read_count1', 'read_density1',
                 'normed_read_density1', 'read_count2', 'read_density2',
                 'mvalue', 'avalue', 'normed_mvalue', 'normed_avalue', 'pvalue']
```

---

## 5. 测试体系建设

### 5.1 当前状态

项目**完全没有自动化测试**。`test/` 目录仅包含参考输出文件，没有任何测试脚本。`lib/MAnorm_io.py` 底部有两个简单的测试函数（`test_read_reads`、`test_read_peaks`），但它们引用不存在的文件路径，且未集成到任何测试框架。

### 5.2 建议添加的测试

| 测试类型 | 覆盖范围 | 工具 |
|----------|----------|------|
| 单元测试 | `Peak` 类方法、P-value 计算、overlap 判断、peaks 合并 | `pytest` |
| 集成测试 | 使用小型测试数据运行完整 pipeline，与 `test/` 参考输出比对 | `pytest` |
| 回归测试 | 验证输出 XLS 文件的数值精度在代码变更后保持稳定 | `pytest` + `pandas` |
| 边界测试 | 空输入、单 peak、无 common peaks、单染色体 | `pytest` |

### 5.3 建议的测试目录结构

```
tests/
├── conftest.py          # 共用的 fixtures（测试数据路径等）
├── test_peaks.py        # Peak 类和相关函数的单元测试
├── test_io.py           # 文件读写函数的测试
├── test_integration.py  # 端到端 pipeline 测试
└── data/                # 小型测试数据集
    ├── sample_peaks1.bed
    ├── sample_peaks2.bed
    ├── sample_reads1.bed
    └── sample_reads2.bed
```

---

## 6. 打包与发布改进

### 6.1 从 `distutils` 迁移到 `setuptools` / `pyproject.toml`

**位置**: `setup.py:1`

```python
from distutils.core import setup
```

**问题**: `distutils` 在 Python 3.10 中已被标记为废弃，Python 3.12 中已移除。

**修复**: 迁移到现代打包标准：

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "MAnormFast"
version = "0.1.0"
requires-python = ">=3.7"
dependencies = [
    "numpy>=1.20",
    "scipy>=1.7",
    "matplotlib>=3.5",
    "pandas>=1.3",
    "statsmodels>=0.13",
]

[project.scripts]
MAnormFast = "MAnormFast.cli:command"
```

### 6.2 依赖版本过旧且锁死

**位置**: `requirements.txt`

所有依赖锁定在 2016 年的版本（如 `numpy==1.11.2`、`scipy==0.18.1`），这些版本：
- 不支持 Python 3.7+
- 包含已知安全漏洞
- 无法在现代系统上编译安装

**修复**: 使用最低版本约束而非精确版本锁定：
```
numpy>=1.20
scipy>=1.7
matplotlib>=3.5
pandas>=1.3
statsmodels>=0.13
```

### 6.3 添加 `entry_points` 替代 `scripts`

当前使用 `scripts=['bin/MAnormFast']` 直接复制脚本文件。建议使用 `entry_points` 的 `console_scripts` 方式，这是更标准的做法，支持跨平台。

### 6.4 支持 pip install

目前只能通过 `python setup.py install` 安装。应支持 `pip install .` 和 `pip install -e .`（开发模式）。

---

## 7. 文档完善

### 7.1 README 中的命令示例有误

**位置**: `README.md:12`

```
python MAnorm.py --p1 peak1 --r1 read1 --p2 peak2 --r2 read1 -o ouput_folder_name
```

**问题**:
- 文件名是 `MAnormFast` 而不是 `MAnorm.py`
- `--r2 read1` 应为 `--r2 read2`（复制粘贴错误）
- `ouput` 应为 `output`（拼写错误）

### 7.2 README 安装说明有误

**位置**: `README.md:24`

```
chmod -x MAnormFast
```

**问题**: `-x` 是**移除**执行权限，应为 `chmod +x MAnormFast`。

### 7.3 缺少以下文档内容

- 输出文件格式说明（各列含义）
- 完整的使用示例（从数据准备到结果解读）
- 算法原理简要说明（不仅仅是论文链接）
- 环境要求（Python 版本、操作系统）
- CHANGELOG（版本变更日志）
- LICENSE 文件（声明了 GPL 许可证但缺少 LICENSE 文件）

---

## 8. 健壮性与错误处理

### 8.1 裸 `except` 语句

**位置**: `lib/MAnorm_io.py:72,119`

```python
except:
    pk = Peak(chrm, int(sli[1]), int(sli[2]))
```

**问题**: 捕获所有异常（包括 `KeyboardInterrupt`、`SystemExit`），会静默隐藏真正的错误（如文件格式损坏、内存不足）。

**修复**: 明确捕获特定异常：
```python
except (IndexError, ValueError):
    pk = Peak(chrm, int(sli[1]), int(sli[2]))
```

### 8.2 缺少输入验证

`bin/MAnormFast` 的 `command()` 函数中，必需参数（`--p1`、`--p2`、`--r1`、`--r2`、`-o`）全部可以为 `None`，但代码没有做任何检查。如果用户遗漏参数，会得到不友好的 `AttributeError` 或 `TypeError`。

**修复**: 添加参数完整性验证：
```python
required = ['pkf1', 'pkf2', 'rdf1', 'rdf2', 'output']
for attr in required:
    if getattr(values, attr) is None:
        opt_parser.error('Missing required argument: --%s' % attr)
```

### 8.3 文件存在性检查缺失

用户提供的 peak 文件和 reads 文件路径没有做存在性验证。如果路径错误，会在处理过程中才报出 `FileNotFoundError`，且错误信息不够明确。

**修复**: 在 `command()` 函数开头添加检查：
```python
for fp in [numerator_peaks_fp, denominator_peaks_fp, numerator_reads_fp, denominator_reads_fp]:
    if not os.path.isfile(fp):
        sys.exit('Error: File not found: %s' % fp)
```

### 8.4 输出图片格式建议

**位置**: `lib/MAnorm_io.py:221,242,254,270`

当前所有图片保存为 PNG 格式。建议：
- 添加命令行选项支持指定输出格式（PNG/PDF/SVG）
- 对于论文级别的图片，PDF/SVG 矢量格式更适合

### 8.5 数值稳定性

**位置**: `lib/peaks.py:83-100`

P-value 计算中使用 `round(comb(...))` 可能导致大数溢出。当 `xx + yy` 较大时，组合数可能超过浮点数精度范围。建议在对数域中完成全部计算，避免中间结果溢出。

---

## 优先级总结

| 优先级 | 优化项 | 影响 |
|--------|--------|------|
| **P0 - 紧急** | Python 3 迁移 | 安全性、可用性、长期维护 |
| **P0 - 紧急** | 修复 `strand is '+'` Bug (#2.1) | 计算结果正确性 |
| **P0 - 紧急** | 修复 `isoverlap` 遗漏 (#2.3) | 计算结果正确性 |
| **P1 - 重要** | 删除 `time.sleep()` (#3.1) | 运行效率 |
| **P1 - 重要** | `os.chdir` → `os.path.join` (#4.1) | 代码健壮性 |
| **P1 - 重要** | 添加输入验证 (#8.2, #8.3) | 用户体验 |
| **P1 - 重要** | 添加自动化测试 (#5) | 代码质量保障 |
| **P2 - 建议** | 打包迁移到 setuptools/pyproject.toml (#6.1) | 现代化分发 |
| **P2 - 建议** | `with` 语句替换手动 close (#4.2) | 代码安全 |
| **P2 - 建议** | README 修正 (#7.1, #7.2) | 文档准确性 |
| **P3 - 长期** | 使用 Interval Tree 优化 overlap 检测 (#3.5) | 大规模数据性能 |
| **P3 - 长期** | `Peak.__slots__` 内存优化 (#4.6) | 大规模数据内存 |
| **P3 - 长期** | reads 解析向量化 (#3.6) | 大文件读取性能 |
