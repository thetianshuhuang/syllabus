
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Syllabus',
    version='1.1',
    packages=[
        'syllabus',
        'syllabus.format',
        'syllabus.app_utils',
        'syllabus.parallel',
        'syllabus.reporting'
    ],
    install_requires=['pyfiglet', 'ansiwrap'],
    license='MIT',
    author='Tianshu Huang',
    author_email='thetianshuhuang@gmail.com',
    description=(
        'Time and memory tracking task manager for Machine Learning '
        'applications'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/thetianshuhuang/syllabus',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
