from distutils.core import setup


def main():

    setup(
        name='MAnormFast',
        version='0.1.0',
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
