from setuptools import setup

__version__ = '0.1.0b1'

long_description = ''' '''

setup(
    name=parsetcx,
    version=__version__,
    description='A comprehensive parser for .tcx files',
    long_description=long_description,
    url='https://github.com/bradenleith/tcxparser/',
    author='Braden Mitchell',
    author_email='braden.mitchell@mymail.unisa.edu.au',
    py_modules=['tcxparser']
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Researchers',
        'License :: OSI Approved :: GNU GPLv3 License',
        'Operating System :: OS Independent'
        'Programming Language :: Python :: 3'
    ],
    install_requirements=[
        'lxml'
    ],
    keywords='heartrate garmin polar .tcx'
)
