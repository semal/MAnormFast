# MAnormFast 安装指南

本指南详细说明了如何安装和使用 MAnormFast。

## 系统要求

- Python >= 3.10
- 操作系统：Linux, macOS, Windows
- 内存：建议 4GB 以上

## 安装方法

### 方法 1：通过 pip 安装（推荐）

```bash
pip install MAnormFast
```

### 方法 2：从源码安装

```bash
git clone https://github.com/semal/MAnormFast.git
cd MAnormFast
pip install .
```

### 方法 3：开发者安装

```bash
git clone https://github.com/semal/MAnormFast.git
cd MAnormFast
pip install -e .
```

## 依赖包

MAnormFast 会自动安装以下依赖包：

- numpy >= 1.21.0
- matplotlib >= 3.5.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- statsmodels >= 0.13.0

## 验证安装

安装完成后，可以通过以下方式验证：

### 1. 验证模块导入

```python
import MAnormFast
print("MAnormFast 安装成功！")
```

### 2. 验证命令行工具

```bash
MAnormFast --help
```

应该显示帮助信息。

## 使用示例

### 基本用法

```bash
MAnormFast --p1 sample1_peaks.bed --r1 sample1_reads.bed \
           --p2 sample2_peaks.bed --r2 sample2_reads.bed \
           -o comparison_results
```

### 带参数的用法

```bash
MAnormFast --p1 sample1_peaks.bed --r1 sample1_reads.bed \
           --p2 sample2_peaks.bed --r2 sample2_reads.bed \
           -o comparison_results -e 500 -n 10 -p 0.05
```

## 常见问题

### Q: 导入错误 "No module named 'MAnormFast'"

A: 请确保：
1. 使用正确的 Python 环境
2. 已正确安装包：`pip install MAnormFast`
3. 如果使用虚拟环境，确保已激活

### Q: 命令行工具不可用

A: 请检查：
1. 包是否正确安装
2. PATH 环境变量是否包含 Python 脚本目录
3. 尝试重新安装：`pip uninstall MAnormFast && pip install MAnormFast`

### Q: 依赖包安装失败

A: 建议：
1. 升级 pip：`pip install --upgrade pip`
2. 使用虚拟环境
3. 在某些系统上可能需要安装编译工具

## 卸载

```bash
pip uninstall MAnormFast
```

## 获取帮助

- GitHub Issues: https://github.com/semal/MAnormFast/issues
- 文档: https://github.com/semal/MAnormFast/blob/main/README.md

## 版本信息

当前版本：0.1.0

查看版本：
```bash
python -c "import MAnormFast; print(MAnormFast.__version__)"
```