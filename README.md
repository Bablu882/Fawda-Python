# fawda-python

Fawda is a web-based application that offers a platform for Grahak (customers), Sahayak (helpers), and MachineMalik (machine operators) to manage their job postings, bookings, and payments. The application is built using the Django web framework and is designed to be user-friendly, reliable, and efficient.
## Getting started
Fawda is built using the Django web framework, which follows the Model-View-Controller (MVC) architecture. It uses MySQL as its database management system.

The application consists of three main components: the database, the API layer, and the user interface. The API layer acts as an intermediary between the database and the user interface, handling all the data processing and retrieval.

Overall, the Fawda architecture is designed to be scalable, efficient, and secure. The API layer provides a standardized interface for interacting with the database, making it easy to integrate with other applications or services. The user interface is designed to be intuitive and user-friendly, allowing users to easily navigate and interact with the application.
## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following comman
d:

```
cd existing_repo
git remote add origin https://gitlab.webnyxa.com/webnyxa/fawda-python.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.webnyxa.com/webnyxa/fawda-python/-/settings/integrations)

## Installation

#Clone the project repository using the following command:
```
git clone https://gitlab.webnyxa.com/webnyxa/fawda-python.git
```

#create MySql database in your system if not already installed:
#if MySql will show error than run this command 
```
sudo apt-get install libmysqlclient-dev
```
#python3.8 should be preinstalled 

#Create and activate a virtual environment:
```
python -m venv env
source env/bin/activate
```

#Install the project requirements using pip:
```
pip install -r requirements.txt
```

#Still showing error No Module Found pakage than run the command 
```
pip install pakage-name
```

#Update the DATABASES setting in settings.py with the database details:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'database_name',
        'USER': 'database_user',
        'PASSWORD': 'database_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#Run database migrations to create the required tables:
```
python manage.py migrate
```

#Create a superuser account to access the Django admin site
```
python manage.py createsuperuser
```

#Run the development server:
```
python manage.py runserver
```


