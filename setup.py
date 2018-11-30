import os
from setuptools import find_packages, setup
from dcron import version


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# stamp the package prior to installation
version.stamp_directory(os.path.join(os.getcwd(), 'dcron'))

setup(
    name='django-dcron',
    version=version.get_version(),
    packages=find_packages(),
    include_package_data=True,
    package_data={'dcron': ['VERSION_STAMP']},
    install_requires=['Django>=2', 'croniter'],
    description='An app for building cron jobs dynamically from model classes and model instances',
    url='https://github.com/gregschmit/django-dcron',
    author='Gregory N. Schmit',
    author_email='gschmi4@uic.edu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
