# AGENTS.md

## Cursor Cloud specific instructions

### Overview

MAnormFast is a **Python 2.7** CLI bioinformatics tool for quantitative comparison of ChIP-Seq data sets using the MAnorm algorithm. It is a standalone computational tool with no external services, databases, or web servers.

### Python 2.7 Environment

This codebase requires **Python 2.7** (uses `print` statements, `time.clock()`, Python 2-style relative imports). Ubuntu 24.04 does not ship Python 2, so a **Miniconda** environment is used:

- Miniconda installed at: `$HOME/miniconda3`
- Conda env name: `manormfast` (Python 2.7 with numpy, scipy, matplotlib, pandas, statsmodels, flake8)
- Activate: `conda activate manormfast` or use `conda run -n manormfast <command>`
- The `$HOME/miniconda3/bin` is added to `PATH` in `~/.bashrc`

### Key Commands

| Action | Command |
|--------|---------|
| Run help | `conda run -n manormfast python bin/MAnormFast --help` |
| Build/Install | `conda run -n manormfast python setup.py install` |
| Lint | `conda run -n manormfast flake8 --max-line-length=120 lib/ bin/MAnormFast setup.py` |
| Run analysis | `conda run -n manormfast python bin/MAnormFast --p1 <peaks1> --r1 <reads1> --p2 <peaks2> --r2 <reads2> -o <output>` |

### Gotchas

- There are no automated unit tests in this repo. Validation is done by running the tool against test data and comparing outputs.
- The `test/` directory contains reference output files (XLS tables, PNG figures, WIG tracks, BED filters) for comparison.
- The `bin/MAnormFast` script uses `time.clock()` which is Python 2 specific (removed in Python 3.8).
- All lint warnings (star imports, `is` vs `==` for string comparison) are pre-existing code patterns and not regressions.
- The tool uses `os.chdir()` during output, so always run from a clean working directory or use absolute paths.
- When running the tool, the `-o` output folder must not already exist (it creates a new directory).
