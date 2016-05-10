from setuptools import setup


def get_version():
    return open('biscuit/_version.py').readline().strip().strip('"')


setup(
    name='biscuit-py',
    version=get_version(),
    description='biscuit-py decrypts secrets managed by Biscuit.',
    long_description=open('README.rst').read(),
    author='Doug Coker',
    author_email='dcoker@gmail.com',
    url='https://github.com/dcoker/biscuit-py/',
    include_package_data=False,
    license='https://www.apache.org/licenses/LICENSE-2.0',
    packages=[
        'biscuit'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7'
    ],
    zip_safe=False,
    install_requires=[
        'boto3>=1.3.0,<2',
        'libnacl>=1.4.4,<2',
        'pycryptodomex>=3.4.2,<4',
        'pyyaml>=3.11,<4'
    ],
    test_suite='tests.biscuit_test',
    entry_points={
        'console_scripts': [
            'biscuitpy=biscuit.__main__:main'
        ]
    },
)
