from setuptools import setup, find_packages

with open('README.md') as readme:
    long_decription = readme.read()

setup(
    name='setuptools-demo', # package will be imported as: import setuptools-demo
    version='0.0.1',
    description='setuptools demo',
    long_description=long_decription,
    author='mateuszmidor',
    author_email='mateuszmidor@mateuszmidor.com',
    license='MIT',
    url='https://github.com/mateuszmidor/PythonStudy/setuptools-demo',
    packages=find_packages(exclude=('tests*', 'testing')), # or just packages=['src']
    install_requires=["requests>=2"], # package dependencies list
    python_requires="~=3.5", # python 3.5 and up, but not python 4. (See: >=3.5 that includes python 4)
    entry_points= { # this makes the installed package a shell command: setuptools-demo
        'console_scripts': ['setuptools-demo = src.main:main']
    }
)