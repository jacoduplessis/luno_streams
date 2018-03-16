from setuptools import setup

github = 'https://github.com/jacoduplessis/luno_streams'

setup(
    name='luno_streams',
    author='Jaco du Plessis',
    author_email='jaco@jacoduplessis.co.za',
    description='Luno client for the streaming API.',
    url=github,
    keywords='luno websockets',
    include_package_data=True,
    package_data={
      'luno_streams': ['app.html']
    },
    version='0.1.1',
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
