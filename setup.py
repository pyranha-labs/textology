"""Setup configuration and dependencies for the textology library."""

import os

from pathlib import Path

from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


def read_requirements_file(extra_type: str | None) -> list[str]:
    """Read local requirement file basic on the type."""
    extra_type = f'-{extra_type}' if extra_type else ''
    with open(f'requirements{extra_type}.txt', encoding='utf-8') as fp:
        lines = (line.strip() for line in fp)
        return [req for req in lines if req and not req.startswith("#")]


def _find_version(module_path: str, file: str = '__init__.py') -> str:
    """Locate semantic version from a text file in a compatible format with setuptools."""
    # Do not import the module within the library, as this can cause an infinite import. Read manually.
    init_file = os.path.join(ROOT_DIR, module_path, file)
    with open(init_file, 'rt') as file_in:
        for line in file_in.readlines():
            if '__version__' in line:
                # Example:
                # __version__ = '1.2.3' -> 1.2.3
                version = line.split()[2].replace("'", '')
    return version


setup(
    name='textology',
    description='Extensions for creating Terminal User Interfaces',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    version=_find_version('textology'),
    maintainer='David Fritz',
    author='David Fritz',
    url='https://github.com/dfrtz/textology',
    project_urls={
        'Issue Tracker': 'https://github.com/dfrtz/textology/issues',
        'Source Code': 'https://github.com/dfrtz/textology',
    },
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Widget Sets',
        'Typing :: Typed',
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: POSIX :: Linux",
    ],
    platforms=[
        'MacOS',
        'Linux',
        'Windows',
    ],
    test_suite='pytest',
    packages=find_packages(
        ROOT_DIR,
        include=['textology*'],
        exclude=['*test', 'tests*']
    ),
    python_requires='>=3.10',
    install_requires=read_requirements_file(None),
    extras_require={
        'dev': read_requirements_file('dev'),
    },
)
