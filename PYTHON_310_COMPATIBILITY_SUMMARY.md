# Python 3.10+ Compatibility Optimizations for MAnormFast

## Overview
This document summarizes the optimizations made to make MAnormFast compatible with Python 3.10 and above versions.

## Issues Fixed

### 1. Setup and Dependencies
- **setup.py**: Replaced deprecated `distutils` with `setuptools`
- **requirements.txt**: Updated all package versions to modern ones compatible with Python 3.10+
- Added `python_requires='>=3.10'` to enforce minimum Python version
- Added proper package classifiers for Python 3.10, 3.11, and 3.12

### 2. Print Statements → Print Functions
**Files affected**: `lib/MAnorm_io.py`, `bin/MAnormFast`

**Changes made**:
- `print 'message'` → `print('message')`
- `print 'message' % value` → `print('message' % value)`

**Examples**:
```python
# Before
print 'output wig files ... '
print 'filter %d unbiased peaks' % i

# After  
print('output wig files ... ')
print('filter %d unbiased peaks' % i)
```

### 3. Time Module Updates
**Files affected**: `lib/MAnorm_io.py`, `bin/MAnormFast`

**Changes made**:
- `time.clock()` → `time.perf_counter()`
- Added `import time` where needed

**Reason**: `time.clock()` was deprecated in Python 3.3 and removed in Python 3.8. `time.perf_counter()` provides monotonic timing with the highest available resolution.

### 4. SciPy Import Updates
**File affected**: `lib/peaks.py`

**Changes made**:
- `from scipy.misc import comb` → `from scipy.special import comb`

**Reason**: `scipy.misc.comb` was deprecated and moved to `scipy.special.comb` in newer SciPy versions.

### 5. Dictionary Operations
**File affected**: `lib/peaks.py`

**Changes made**:
- `set(pks1.keys() + pks2.keys())` → `set(list(pks1.keys()) + list(pks2.keys()))`

**Reason**: In Python 3, `dict.keys()` returns a view object that doesn't support concatenation with `+`. Converting to lists first enables concatenation.

### 6. Integer Division
**Files affected**: `lib/peaks.py`, `bin/MAnormFast`

**Changes made**:
- `(s + e) / 2 + 1` → `(s + e) // 2 + 1` (for integer division)
- `ext / 2` → `ext // 2` (for integer division)

**Reason**: Ensures consistent integer division behavior across Python versions.

### 7. Shebang Line Update
**File affected**: `bin/MAnormFast`

**Changes made**:
- `#!/usr/bin/python` → `#!/usr/bin/python3`

**Reason**: Explicitly use Python 3 interpreter.

## Package Version Updates

### Old Dependencies (Python 2.7 era):
```
matplotlib==1.5.3
numpy==1.11.2
pandas==0.19.1
scipy==0.18.1
statsmodels==0.6.1
```

### New Dependencies (Python 3.10+ compatible):
```
numpy>=1.21.0
matplotlib>=3.5.0
pandas>=1.3.0
scipy>=1.7.0
statsmodels>=0.13.0
```

## Key Benefits

1. **Future-proof**: Compatible with Python 3.10, 3.11, and 3.12
2. **Performance**: Modern package versions with performance improvements
3. **Security**: Updated dependencies with security patches
4. **Maintenance**: Follows current Python best practices
5. **Reliability**: Uses stable, well-maintained package versions

## Testing Recommendations

1. **Environment Setup**:
   ```bash
   python3 -m venv venv_310
   source venv_310/bin/activate
   pip install -r requirements.txt
   ```

2. **Installation**:
   ```bash
   python setup.py install
   ```

3. **Basic functionality test**:
   ```bash
   python -c "from lib.peaks import Peak; from lib.MAnorm_io import read_peaks; print('Import successful')"
   ```

## Notes

- All changes maintain backward compatibility with the existing API
- The core algorithm and functionality remain unchanged
- Only infrastructure and compatibility issues were addressed
- Modern Python features could be leveraged in future updates (e.g., type hints, f-strings, pathlib)

## Potential Future Improvements

1. **Type Hints**: Add type annotations for better code documentation
2. **F-strings**: Replace % formatting with f-string literals
3. **Pathlib**: Use `pathlib.Path` instead of `os.path` operations
4. **Context Managers**: Ensure all file operations use `with` statements
5. **Logging**: Replace print statements with proper logging
6. **Async Support**: Consider async/await for I/O operations if needed