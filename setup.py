from setuptools import setup, find_packages

setup(
    name='carthooks',
    version='0.1.1',
    packages=find_packages(),
    description='Carthooks Python SDK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Carthooks',
    author_email='developer@carthooks.com',
    license='MIT',
    install_requires=[
        'requests>=2.23.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)