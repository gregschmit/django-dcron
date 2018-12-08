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
    description='A re-useable Django app for scheduling jobs dynamically.',
    long_description='`dcron` (dynamic cron) is a re-useable Django app that allows you to schedule jobs dynamically. You can assign a schedule for a Model class, or you can schedule jobs for each Model instance. Read the documentation at https://django-dcron.readthedocs.io/.',
    url='https://github.com/gregschmit/django-dcron',
    author='Gregory N. Schmit',
    author_email='gschmi4@uic.edu',
    license='MIT',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
