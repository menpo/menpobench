from setuptools import setup, find_packages
import versioneer


setup(name='menpobench',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Deformable Model benching suite',
      author='The Menpo Development Team',
      author_email='james.booth08@imperial.ac.uk',
      packages=find_packages(),
      tests_require=['nose'],
      install_requires=['menpofit>=0.2,<0.3'])
