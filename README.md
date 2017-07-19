Recruitr
========

Recruitr is a modern online judge tool.

You can add coding challenges via the admin interface, specify test cases
(expected input/output), and make it available for visitors to try to solve them
by submitting code.

Currently, recruitr supports C, C++, Haskell, Java, Javascript (Node), Perl,
PHP, Python, Racket, Ruby, Scala, and Shell (Bash). The user submitted code is
run in a docker container, therefore very secure.

Recruitr is built in [Django](https://www.djangoproject.com), and
uses [Celery](http://www.celeryproject.org) for dispatching the code running
tasks asynchronously.

#### OAuth setup

Get the api client id and secret key by registering your app on the platform whose oauth you want to use, like:
 * [Google](https://console.developers.google.com/start)
 * [Github](https://developer.github.com/apps/building-integrations/setting-up-and-registering-oauth-apps/)

After you have them just add to `local_settings.py` in `recruitr` app.

For example:

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'xxxx'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'xxxx'

    SOCIAL_AUTH_GITHUB_KEY = 'xxxx'
    SOCIAL_AUTH_GITHUB_SECRET = 'xxxx'

### Tests

To run the tests you can execute the following command.
```python
    python manage.py test
```
