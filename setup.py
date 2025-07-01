from setuptools import setup, find_packages
from lib import version


def main():

    setup(
        name='MAnormFast',
        version=version,
        packages=find_packages(),
        package_dir={'MAnormFast': 'lib'},
        scripts=['bin/MAnormFast'],
        url='www.github.com/semal',
        license='GNU General Public License',
        author='Semal',
        author_email='gzhsss2@gmail.com',
        description='MAnorm version, Fast but more memory',
        python_requires='>=3.10',
        install_requires=[
            'numpy>=1.21.0',
            'matplotlib>=3.5.0',
            'pandas>=1.3.0',
            'scipy>=1.7.0',
            'statsmodels>=0.13.0',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
    )


if __name__ == '__main__':
    main()
