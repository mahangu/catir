from setuptools import setup

setup(
    name='catir',
    version='0.5',
    py_modules=['catir'],
    install_requires=[
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'catir=catir:main',
        ],
    },
    author='Mahangu Weerasinghe',
    author_email='mahangu@gmail.com',
    description='Camera Trap Image Renamer (CATIR)',
    url='https://github.com/mahangu/catir',
)