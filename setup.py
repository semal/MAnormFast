from distutils.core import setup
import sys


def main():
    if not float(sys.version[:3]) >= 2.5:
        sys.stderr.write(
            "CRITICAL: Python version must be greater than or equal to 2.5! python 2.6.1 is recommended!\n")
        sys.exit(1)

    setup(
        name='MAnormFast',
        version='0.0.1',
        packages=['MAnormFast'],
        package_dir={'MAnormFast': 'lib'},
        scripts=['bin/MAnormFast'],
        url='www.github.com/semal',
        license='GNU General Public License',
        author='Semal',
        author_email='gzhsss2@gmail.com',
        description='MAnorm version, Fast but more memory'
    )


if __name__ == '__main__':
    main()