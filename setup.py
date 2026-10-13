from setuptools import setup, find_packages

try:
    from lib import version
except ImportError:
    version = '0.2.0'


def main():
    setup(
        name='MAnormFast',
        version=version,
        packages=['MAnormFast'],
        package_dir={'MAnormFast': 'lib'},
        scripts=['bin/MAnormFast'],
        url='https://github.com/semal/MAnormFast',
        license='GNU General Public License v3',
        author='Semal',
        author_email='gzhsss2@gmail.com',
        description='MAnorm: a robust model for quantitative comparison of ChIP-Seq data sets',
        python_requires='>=3.7',
        install_requires=[
            'numpy>=1.20',
            'scipy>=1.7',
            'matplotlib>=3.5',
            'pandas>=1.3',
            'statsmodels>=0.13',
        ],
        entry_points={
            'console_scripts': [
                'manormfast=MAnormFast.cli:command',
            ],
        },
    )


if __name__ == '__main__':
    main()
