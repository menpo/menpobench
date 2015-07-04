from setuptools import setup, find_packages
import sys
import versioneer

install_requires = ['menpofit>=0.2,<0.3']

if sys.version_info.major == 2:
      install_requires.append('pathlib==1.0')

setup(name='menpobench',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Deformable Model benching suite',
      author='The Menpo Development Team',
      author_email='james.booth08@imperial.ac.uk',
      packages=find_packages(),
      tests_require=['nose'],
      install_requires=install_requires)