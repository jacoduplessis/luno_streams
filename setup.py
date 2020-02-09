from setuptools import setup

setup(
    name='luno_streams',
    author='Jaco du Plessis',
    author_email='jaco@jacoduplessis.co.za',
    description='Luno client for the streaming API.',
    url='https://github.com/jacoduplessis/luno_streams',
    keywords='luno websockets',
    package_data={
      'luno_streams': ['app.html']
    },
    version='0.1.4',
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
