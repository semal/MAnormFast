from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from lib/__init__.py
version = {}
with open(os.path.join(this_directory, 'lib', '__init__.py')) as f:
    exec(f.read(), version)

def main():
    setup(
        name='MAnormFast',
        version=version['version'],
        packages=['MAnormFast'],
        package_dir={'MAnormFast': 'lib'},
        scripts=['bin/MAnormFast'],
        url='https://github.com/semal/MAnormFast',
        license='GNU General Public License v3 (GPLv3)',
        author='Semal',
        author_email='gzhsss2@gmail.com',
        description='MAnorm Fast - A robust model for quantitative comparison of ChIP-Seq data sets',
        long_description=long_description,
        long_description_content_type='text/markdown',
        python_requires='>=3.10',
        install_requires=[
            'numpy>=1.21.0',
            'matplotlib>=3.5.0',
            'pandas>=1.3.0',
            'scipy>=1.7.0',
            'statsmodels>=0.13.0',
        ],
        entry_points={
            'console_scripts': [
                'MAnormFast=MAnormFast.MAnormFast:command',
            ],
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Operating System :: OS Independent',
        ],
        keywords='bioinformatics, ChIP-Seq, genomics, peak analysis, normalization',
        project_urls={
            'Bug Reports': 'https://github.com/semal/MAnormFast/issues',
            'Source': 'https://github.com/semal/MAnormFast',
            'Documentation': 'https://github.com/semal/MAnormFast/blob/main/README.md',
        },
    )

if __name__ == '__main__':
    main()
