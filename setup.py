
from distutils.core import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='syllabus',
    version='2.0',
    packages=[
        'syllabus',
        'syllabus.app_utils',
        'syllabus.format',
        'syllabus.parallel',
        'syllabus.reporting',
    ],
    license='MIT',
    install_requires=['printtools', 'ansiwrap'],
    author='Tianshu Huang',
    author_email='thetianshuhuang@gmail.com',
    description=(
        'Time and memory tracking task manager for Machine Learning '
        'applications'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/thetianshuhuang/syllabus',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
