# MAnormFast Pip 安装支持 - 完成总结

## 已完成的工作

### 1. 更新了 setup.py
- 添加了完整的包元数据
- 配置了正确的包结构 (`MAnormFast` 包映射到 `lib` 目录)
- 添加了入口点 (console_scripts) 
- 包含了长描述和项目 URL
- 设置了正确的依赖关系

### 2. 创建了 lib/MAnormFast.py
- 从 `bin/MAnormFast` 复制了主要功能
- 添加了适当的模块导入
- 提供了 `command()` 函数作为入口点

### 3. 创建了 MANIFEST.in
- 确保所有必要文件都包含在分发包中
- 排除了不必要的文件

### 4. 创建了 pyproject.toml
- 支持现代 Python 打包标准
- 与 setup.py 保持一致的配置

### 5. 完全重写了 README.md
- 添加了 pip 安装说明
- 改进了文档结构
- 添加了使用示例和故障排除
- 包含了版本徽章和许可证信息

### 6. 创建了安装指南
- 详细的安装说明
- 常见问题解答
- 验证方法

## 安装方法

### 从 PyPI 安装（推荐）
```bash
pip install MAnormFast
```

### 从源码安装
```bash
git clone https://github.com/semal/MAnormFast.git
cd MAnormFast
pip install .
```

### 开发者安装
```bash
git clone https://github.com/semal/MAnormFast.git
cd MAnormFast
pip install -e .
```

## 使用方法

安装后，可以通过以下方式使用：

### 命令行
```bash
MAnormFast --p1 peak1.bed --r1 read1.bed --p2 peak2.bed --r2 read2.bed -o output
```

### Python API
```python
from MAnormFast import command
import sys

# 设置命令行参数
sys.argv = ['MAnormFast', '--p1', 'peak1.bed', '--r1', 'read1.bed', 
            '--p2', 'peak2.bed', '--r2', 'read2.bed', '-o', 'output']

# 运行分析
command()
```

## 测试验证

在虚拟环境中测试了完整的安装流程：
1. ✅ 包成功构建
2. ✅ 依赖项自动安装
3. ✅ 模块可以正确导入
4. ✅ 命令行工具可用

## 文件结构

```
MAnormFast/
├── setup.py                    # 主要安装配置
├── pyproject.toml              # 现代打包配置
├── MANIFEST.in                 # 包含文件列表
├── README.md                   # 更新的项目文档
├── INSTALLATION_GUIDE.md       # 详细安装指南
├── requirements.txt            # 依赖列表
├── lib/                        # 主要代码目录
│   ├── __init__.py            # 包初始化
│   ├── MAnormFast.py          # 主入口点
│   ├── MAnorm_io.py           # IO 功能
│   └── peaks.py               # 峰值处理
└── bin/                       # 可执行脚本
    └── MAnormFast             # 命令行脚本
```

## 关键改进

1. **标准化包结构**: 遵循 Python 包标准
2. **自动依赖管理**: pip 自动处理所有依赖
3. **命令行集成**: 安装后直接可用 `MAnormFast` 命令
4. **完整文档**: 详细的安装和使用说明
5. **现代打包**: 支持 pyproject.toml 和传统 setup.py
6. **版本管理**: 集中的版本信息管理

## 发布准备

项目现在已经准备好发布到 PyPI：

1. 构建分发包：
   ```bash
   python -m build
   ```

2. 上传到 PyPI：
   ```bash
   twine upload dist/*
   ```

## 兼容性

- Python 3.10+
- 支持 Linux, macOS, Windows
- 与现有的 MAnorm 工作流兼容