from distutils.core import setup
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
        description='MAnorm version, Fast but more memory'
    )


if __name__ == '__main__':
    main()
