from setuptools import setup, find_packages, Command
import os
import shutil

'''
Usage:
    Compile to .egg format:
    $Python setup.py bdist_egg
    
    Compile to windows installer format:
    $Python setup.py bdist_wininst
    
    Compile to zip format
    $Python setup.py bdist --format=zip
    
    Create raw source distribution:
    $Python setup.py sdist
'''


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        self.cwd = None
        
    def finalize_options(self):
        self.cwd = os.getcwd()
        
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        curd = os.getcwd()
        shutil.rmtree(os.path.join(curd, 'SHIP.egg-info'))
        shutil.rmtree(os.path.join(curd, 'dist'))
        shutil.rmtree(os.path.join(curd, 'build'))


def readme():
    with open('README.rst') as f:
        return f.read()
    

setup(  name='ship',
        version='0.3.0',
        description='A Library of Python utilities for interacting with 1D and 2D hydraulic models',
        long_description=readme(),
        classifiers=[
          'Development Status :: 1 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Utilities :: Model processing :: API',
        ],
        keywords='FMP TUFLOW Utilities Files Tools API',
        url='https://github.com/duncan-r/SHIP',
        author='Duncan Runnacles',
        author_email='duncan.runnacles@thomasmackay.co.uk',
        license='MIT',
        
        # Include the test suite
        test_suite='tests',
        
        # Package exclusions
        packages=find_packages(exclude=['tests', 'integration_tests', 'docs']),
          
        # No package requirements at the moment
        install_requires=[
            'future',
        ],
         
        include_package_data=True,
        zip_safe=False,
        
        cmdclass={
                  'clean': CleanCommand,
                 }
    )
