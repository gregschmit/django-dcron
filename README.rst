=============
:code:`dcron`
=============

.. inclusion-marker-do-not-remove

.. image:: https://readthedocs.org/projects/django-dcron/badge/?version=latest
    :target: https://django-dcron.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Documentation: https://django-dcron.readthedocs.io
Source: https://github.com/gregschmit/django-dcron
PyPI: https://pypi.org/project/django-dcron/

:code:`dcron` is a Django app for dynamically building scheduled jobs based on
models or their instances.

**The Problem**: Existing Django cron-related apps are not dynamic. To make a
cronjob, the programmer has to create an entry in :code:`settings.py`, or has to
write a function or class. This means that changes in the schedule require
intervention by a developer. There may be cases where you want non-developers to
affect when jobs are scheduled (e.g., by modifying the database via the web
application).

**The Solution**: This app allows for the creation of dynamically scheduled
jobs, based on model objects saved in the database. This allows you to have
users affect scheduled jobs by interacting with the web interface and creating
or modifying objects in the database.

How to Use
----------

To install:

.. code-block:: shell

    $ pip install django-dcron

Load :code:`dcron` into your :code:`INSTALLED_APPS`

There are two use cases:

1. A job needs to run regularly for a model class.
2. Each instance (object) in a model class may need it's own job schedule.

For case #1, on the model class, include the **classmethod**
:code:`dcron_class_pattern`. The scheduler will automatically register a cronjob
based on the pattern(s) (semicolon-delimited) in :code:`dcron_class_pattern`. An
empty string is equivalent to the cronjob being disabled.

For case #2 (the more common case), include a property or method
:code:`dcron_pattern`. For each object/instance, the scheduler will
automatically register a cronjob based on the pattern(s) (semicolon-delimited)
in :code:`dcron_pattern`.

The scheduled models should have a :code:`dcron_run`/:code:`dcron_class_run`
method; if none exists then :code:`dcron` will fall-back and attempt to execute
the :code:`run` method.

Patterns should be a semicolon-delimited list of cronjob patterns, such as:

.. code-block:: shell

    * * * * *; 8 11 * * *

    -- or --

    */2 * * * *

You do need to call the management command :code:`dcron_run` often enough for
the jobs to be run. An entry similar to this in the system :code:`/etc/crontab`
is appropriate:

.. code-block:: shell

    * * * * *   root   /path/to/python3 /path/to/manage.py dcron_run

This app comes with two models that provide generic scheduling for running shell
commands and management commands using the :code:`dcron` API. Check out the
:code:`ScheduledShellCommand` and the :code:`ScheduledManagementCommand` models
to test out this functionality.

Examples
--------

Example 1
~~~~~~~~~

Suppose you want to perform some operation on all of your users every night at
9pm. Add this to your :code:`User` model:

.. code-block:: python

    dcron_class_pattern = '* 21 * * *'

    @classmethod
    def dcron_class_run(cls):
        do_my_awesome_operation_here()

Example 2
~~~~~~~~~

Suppose you want your users to be able to schedule when their computers are
rebooted, since some of them use them mostly in the evening, and some use them
mostly during the day. Note that this is different from our first case since
each user must be able to configure their own schedule (so one job per each
entry in the database). You could add this to your :code:`User` model:

.. code-block:: python

    enable_daily_reboot = models.BooleanField(default=True)
    hour_choices = [(x, str(x)) for x in range(24)]
    reboot_hour = models.IntegerField(default=0, choices=hour_choices)
    
    def dcron_pattern(self):
        if not self.enable_daily_reboot: return ''
        return '* {0} * * *'.format(self.reboot_hour)

    def dcron_run(self):
        self.reboot_the_computer()

Contributing
------------

Email gschmi4@uic.edu if you want to contribute. You must only contribute code
that you have authored or otherwise hold the copyright to, and you must
make any contributions to this project available under the MIT license.

To collaborators: don't push using the :code:`--force` option.

Dev Quickstart
--------------

First clone, the repository into a location of your choosing:

.. code-block:: shell

    $ git clone https://github.com/gregschmit/django-dcron

Then you can go into the :code:`django-dcron` directory and do the initial
migrations and run the server (you may need to type :code:`python3` rather than
:code:`python`):

.. code-block:: shell

    $ cd django-dcron
    $ python manage.py makemigrations dcron
    $ python manage.py migrate
    $ python manage.py runserver

Then you can see the models at 127.0.0.1:8000/admin.
