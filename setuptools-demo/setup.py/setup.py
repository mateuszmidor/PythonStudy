from setuptools import setup, find_packages

setup(
    name='setuptools-demo',
    version='0.0.1',
    description='setuptools demo',
    author='mateuszmidor',
    author_email='mateuszmidor@mateuszmidor.com',
    url='https://github.com/mateuszmidor/PythonStudy/setuptools-demo',
    packages=find_packages(exclude=('tests*', 'testing')), # or just packages=['src']
    entry_points= { # this makes the installed package a shell command: setuptools-demo
        'console_scripts': ['setuptools-demo = src.main:main']
    }
)