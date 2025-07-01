from setuptools import setup
from lib import version


def main():

    setup(
        name='MAnormFast',
        version=version,
        packages=['MAnormFast'],
        package_dir={'MAnormFast': 'lib'},
        scripts=['bin/MAnormFast'],
        url='www.github.com/semal',
        license='GNU General Public License',
        author='Semal',
        author_email='gzhsss2@gmail.com',
        description='MAnorm version, Fast but more memory',
        python_requires='>=3.10',
        classifiers=[
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
        ],
    )


if __name__ == '__main__':
    main()
