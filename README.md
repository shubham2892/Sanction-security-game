#P1-Game

Game Application for Science of Security Policy Group study

##Installation and Setup

_P1-Game is an application-driven website running django 1.8 and python 2.7.x_

To begin, clone the repository into a directory of your choice. 

> $ git clone https://github.ncsu.edu/bynarron/P1-Game.git

Enter the project directory and create a virtual environment to manage the project's dependencies:

> $ cd P1/ <br />
> $ virtualenv [your_virtual_environment_name] <br />
> $ source [your_virtual_environment_name]/bin/activate <br />
> $ cd P1-Game/ <br />
  
Now install the requirements:

> $ pip install -r requirements.pip

The project settings, by default, declare a Sqlite3 database. If you wish to develop locally, this is a good option. To instantiate the Database, simply create the schema migrations for the database and the database file will be created.

> $ python manage.py makemigrations Game

Now, you will need to run migrations for MWG_Site and other tracked apps:

> $ python manage.py migrate

Finally, create a super user for your database

>$ python manage.py createsuperuser

You're all set!

Run your test server and check out the site!

> $ python manage.py runserver

Access the server at _localhost:8000_ or you can declare a specific port number </br>
(see _https://docs.djangoproject.com/en/1.9/ref/django-admin/#runserver-port-or-address-port_)

##Depedencies

Contents of Requirements.pip:

Django==1.8 </br>
django-forms-bootstrap==3.0.1 </br>
wsgiref==0.1.2 </br>

##Screenshot

![Game Application](https://github.ncsu.edu/github-enterprise-assets/0000/1631/0000/1376/785fb8b6-bb93-11e5-9da4-c52cfbae255d.png)


  
