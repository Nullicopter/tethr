Vanillons
=========

Vanillons is a pylons app that can be used as the basis of other web
applications. It will provide as a scaffold for rapidly building apps. I am
tired of repeating myself! It is effectively glue code between pylons,
benogle/quaid, and benogle/pylons_common. The goal is to make a runnable
project here, then generate the templates for benogle/vanillons_templates.

### virtualenv

Above this dir is a bin dir. It has an activate binary. You need to run it with
virtual env. Check out the [virtualenv primer](http://iamzed.com/2009/05/07/a-primer-on-virtualenv/)

    source bin/activate

### pylons-common

I wrote benogle/pylons_common which houses much code that should not be generated by
a template. This needs to be installed.


Installation and Setup
----------------------

Download + extract/clone. Then run

    sudo python setup.py develop

Make a vanillons DB and a vanillons_test DB, pick a db user and run in psql:

    GRANT ALL PRIVILEGES ON DATABASE vanillons_test TO myuser;

Change the development.ini and test.ini to reflect your db settings users:
    
    sqlalchemy.default.url = postgresql://user:password@localhost/dbname

Generate the proper tables in your fresh new db by running

    paster setup-app development.ini

Tests are run via:

    sudo nosetests -s --tests=vanillons.tests

And the webserver is run via

    paster serve --reload development.ini

Head over to http://localhost:5000/ and register a user. The first one
registered will be donned the admin cap.

Making Templates
----------------

The entire point of this project it to generate templates for other pylons
projects. To do so, (assuming you have benogle/vanillons_templates a dir up)
go up a dir and run the findandreplace script

    rm -Rf templates/vanillons
    python vanillons/gen_templates/findandreplace.py templates/vanillons

Read the readme at benogle/vanillons_templates to install them if you havent
already.

Try out the new templates

    paster create -t vanillons MyProj

Extending
---------

Write junk here...