from setuptools import setup, find_packages
import sys
import versioneer
import os

install_requires = ['menpofit>=0.2,<0.3', 'pyyaml>=3.11,<4.0',
                    'docopt>=0.6.0,<0.7.0', 'pyrx==0.3.0',
                    'tinys3>=0.1.11,<0.2']

if sys.version_info.major == 2:
      install_requires.append('pathlib==1.0')

setup(name='menpobench',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Deformable Model benching suite',
      author='The Menpo Development Team',
      author_email='james.booth08@imperial.ac.uk',
      packages=find_packages(),
      package_data={'menpobench': ['predefined/dataset/*.py',
                                   'predefined/method/*.py',
                                   'predefined/landmark_process/*.py',
                                   'predefined/experiment/*.yaml',
                                   'predefined/*schema.yaml']},
      tests_require=['nose'],
      scripts=[os.path.join('menpobench', 'bin', 'menpobench')],
      install_requires=install_requires)
