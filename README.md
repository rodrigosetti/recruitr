recruitr
========

Recruitr is a modern online judge tool.

You can add coding challenges via the admin interface, specify test cases
(expected input/output), and make it available for visitors to try to solve them
by submitting code.

Currently, recruitr supports C, C++, Haskell, Java, Javascript (Node), Perl,
PHP, Python, Ruby, Scala, and Shell (Bash). The user submitted code is run in a
docker container, therefore very secure.

Recruitr is built in [Django](https://www.djangoproject.com), and
uses [Celery](http://www.celeryproject.org) for dispatching the code running
tasks asynchronously.
