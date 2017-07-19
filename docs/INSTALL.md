## Installation

### Pre-requisites

Before installation of the project, you need to have the following softwares installed on your system:

- [Git](https://git-scm.com/downloads)
    - Ubuntu/Debian: `sudo apt-get install git`
    - Windows: 
- Python (3.x +)
- [Virtualenv](https://virtualenv.pypa.io/) 
    - `[sudo] pip install virtualenv`
- [Celery](www.celeryproject.org)
    - `pip install celery`
- [Redis](https://redis.io/)
    - Ubuntu/Debian: `sudo apt-get install redis-server`
    - Windows: Follow the instructions [here](https://github.com/ServiceStack/redis-windows#current-version-30503-june-28-2016) to setup redis.
- [Docker](https://www.docker.com/)
    - Complete install instruction for: 
        - [Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce)
        - [Windows](https://docs.docker.com/docker-for-windows/install/)

### Setting up environment

For setting up the project and running the server:

- Get the source code of the project.
    - `git clone https://github.com/hackions/recruitr`

- Create an isolated python environment and install python dependencies.
    ###### Linux
    ```
    cd recruitr
    virtualenv venv
    source venv/bin/activate  # run this command everytime before working on project
    pip install -r requirements.txt
    ```
    ###### Windows
    ```
    cd recruitr
    virtualenv venv
    venv\Scripts\activate.bat  # run this command everytime before working on project
    pip install -r requirements.txt

    ```

- Set up SECRET_KEY

    ```
    chmod 700 utils/gen_key.sh
    ./utils/gen_key.sh
    ```
    This will create a local_settings.py file.

- Run Database migrations
    ```
    python manage.py makemigrations candidates
    python manage.py makemigrations coding_problems
    ```
    then run
    `python manage.py migrate` 

- Running the runserver
    - `python manage.py runserver`

### Setting up Celery

Celery is used here for running tasks asyncronusly. We are using redis as messaging broker for celery.

- `celery -A recruitr worker -l info `
    - This will start a worker process that handles tasks. Keep this up when you are dealing with submission of code.

### Setting up docker container

Docker containers are used to run the submitted code by users so that it doesn't affect the host system.

- `docker build -t runner .`
    - This will create a docker image with configuration specified in `DOCKERFILE`. It might take some time for creating the image, but it's a one time process.

### OAuth setup

Logins are maintained via OAuth providers (currently Google and Github). For development purposes you can get OAuth keys from respective sites.
- [Google](https://console.developers.google.com/start)
- [Github](https://developer.github.com/apps/building-integrations/setting-up-and-registering-oauth-apps/)


After you have them just add to `local_settings.py` in `recruitr` app.

For example:

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'xxxx'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'xxxx'

    SOCIAL_AUTH_GITHUB_KEY = 'xxxx'
    SOCIAL_AUTH_GITHUB_SECRET = 'xxxx'
