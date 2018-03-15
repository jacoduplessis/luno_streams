from setuptools import setup

github = 'https://github.com/jacoduplessis/luno_streams'

setup(
    name='luno_streams',
    author='Jaco du Plessis',
    author_email='jaco@jacoduplessis.co.za',
    description='Luno client for the streaming API.',
    url=github,
    keywords='luno websockets',
    project_urls={
        'Source': github,
        'Tracker': f'{github}/issues',
    },
    version='0.1.0',
    packages=['luno_streams'],
    install_requires=[
        'websockets'
    ],
    entry_points={'console_scripts': [
        'luno_streams=luno_streams.cli:main',
    ]},

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
