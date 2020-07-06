from distutils.core import setup

requires = [
    'flask',
    'flask-sqlalchemy',
    'blinker',
    'sqlalchemy-utils',
    'python-slugify',
    'jsonpatch',
    'flask-migrate',
    'webargs',
    'jsonpointer',
    'LinkHeader',
    'jsonpatch',
    'flask-principal'
]

tests_require = [
    'pytest',
    'pytest-flask-sqlalchemy',
    'md-toc',
    'isort',
    'check-manifest'
]

setup(
    name='flask-taxonomies',
    version='7.0.0dev',
    packages=['flask_taxonomies', ],
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
        'postgresql': ['psycopg2'],
        'sqlite': []
    },
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
