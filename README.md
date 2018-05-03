# Book-A-Meal-V2
Book-A-Meal-V2 is an improvement to the previous Book-A-Meal  application on my repository the improvement being that the API are secured with JWT and fetches real data from database. It is an application that allows customers to make food orders and helps the food vendor know what the customers want to eat.


## Technologies used
* **[Python3](https://www.python.org/downloads/)** - A programming language.
* **[Flask](flask.pocoo.org/)** - A microframework for Python based on Werkzeug, Jinja 2.
* **[Virtualenv](https://virtualenv.pypa.io/en/stable/)** - A tool used to create isolated virtual environments to work on 
* **[PostgreSQL](https://www.postgresql.org/download/)** – Postgres database which offers a lot of advantages over others as you can find them [here](https://www.postgresql.org/about/advantages/).
* other dependencies can be found in the requirements.txt file.



## Installing and Using this app locally
* If you wish to run this application on your machine, ensure that you have python3 installed in your computer. You can get python3 their [official website](https://www.python.org).
* You should also have virtualenv installed in your computer. If you do not have it, you can install it by running the this command:
    ```
        $ pip install virtualenv
    ```
* Then you should have git installed then clone this repository to your computer
    ```
        $ git clone https://github.com/petermwash/Book-A-Meal-V2.git
    ```


* #### Dependencies
    1. Cd int the main folder of the cloned repository as:
        ```
        $ cd Book-A-Meal-V2
        ```

    2. Create and activate a virtual environment in python3 an install dependencies:
        ```
        $ virtualenv -p python3 venv
        $ source venv/bin/activate
        (venv)$ pip install -r requirements.txt
        ```


* #### Environment Variables
	Now export the environment variables by running the following commands on the terminal
    ```
    export SECRET="just-write-you-own-long-sring-here"
    export APP_SETTINGS="development"
    export DATABASE_URL="postgresql://<usernamr><password>@localhost/book_a_meal"
    ```


* #### Migrations
    Now on your psql console, create your database and apply migration  as shown bellow:
    ```
    > CREATE DATABASE book_a_meal;

    (venv)$ python manage.py db init

    (venv)$ python manage.py db migrate
    ```

    Now migrate your migrations to persist on you database
    ```
    (venv)$ python manage.py db upgrade
    ```


* #### Running It
    Finally, to run the app, on your terminal, run the server using the following command:
    ```
    (venv)$ flask run
    ```
    You can now access the app on your browser or test the various endpoints using Postman by using the URL
    ```
    http://localhost:5000/
    ```

Enjoy the app 😄


