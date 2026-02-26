# AGENTS.md

## Cursor Cloud specific instructions

### Overview

MAnormFast is a Python CLI bioinformatics tool for quantitative comparison of ChIP-Seq data sets using the MAnorm algorithm. It is a standalone computational tool with no external services, databases, or web servers.

### Python Environment

- Conda env name: `manormfast3` (Python 3.10 with numpy, scipy, matplotlib, pandas, statsmodels, flake8, pytest)
- Activate: `conda activate manormfast3` or use `conda run -n manormfast3 <command>`
- `$HOME/miniconda3/bin` is in `PATH` via `~/.bashrc`

### Key Commands

| Action | Command |
|--------|---------|
| Run help | `conda run -n manormfast3 python bin/MAnormFast --help` |
| Build | `conda run -n manormfast3 python setup.py build` |
| Install (dev) | `conda run -n manormfast3 pip install -e .` |
| Lint | `conda run -n manormfast3 flake8 --max-line-length=120 --ignore=E402,W503,W504 lib/ bin/MAnormFast` |
| Tests | `conda run -n manormfast3 python -m pytest tests/ -v` |
| Run analysis | `conda run -n manormfast3 python bin/MAnormFast --p1 <peaks1> --r1 <reads1> --p2 <peaks2> --r2 <reads2> -o <output>` |

### Gotchas

- The `test/` directory contains legacy reference output files (not test scripts). Actual tests are in `tests/`.
- The `-o` output folder must not already exist (the tool creates a new directory).
- All output functions take an `output_dir` parameter; `os.chdir()` is no longer used.
- The `lib/cli.py` module contains the main `command()` function; `bin/MAnormFast` delegates to it.
