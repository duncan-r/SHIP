from setuptools import setup, find_packages, Command
import os
import shutil

'''
Usage:
    Compile to .egg format:
    c:\python27\python.exe setup.py bdist_egg
    
    Compile to windows installer format:
    c:\python27\python.exe setup.py bdist_wininst
    
    Compile to zip format
    c:\python27\python.exe setup.py bdist --format=zip
    
    Create raw source distribution:
    c:\python27\python.exe setup.py sdist
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
        version='0.2.0',
        description='A Library of Python utilities for interacting with 1D and 2D hydraulic models',
        long_description=readme(),
        classifiers=[
          'Development Status :: 1 - Beta',
          'License :: OSI Approved :: GNU General Public License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities :: Model processing :: API',
        ],
        keywords='ISIS TUFLOW Utilities Files Tools API',
        url='https://github.com/duncan-r/SHIP',
        author='Duncan Runnacles',
        author_email='duncan.runnacles@thomasmackay.co.uk',
        license='GPL',
        
        # Include the test suite
        test_suite='tests',
        
        # Package exclusions
        packages=find_packages(exclude=['tests', 'docs']),
          
        # No package requirements at the moment
        #install_requires=[
        #    ,
        #],
         
        include_package_data=True,
        zip_safe=False,
        
        cmdclass={
                  'clean': CleanCommand,
                 }
    )
