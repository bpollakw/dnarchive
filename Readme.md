www.dnarchive.info

# DNAarchive - v0.01 alpha

A DNA sequence repository for easy, open-access and community based curation.

## Description

DNArchive aims to simplify the retrieval of DNA sequences used commonly in genetic engineering. It is particularily well suited for part level accessions (for ease of sequence retrieval), but also capable of dealing with composite level constructs.

## Installation
To install DNArchive, just collect the dependencies, set up a postgres database and configure the app.py parameters to find the database and run the webserver.

## Dependencies

### PartDB - https://github.com/HaseloffLab/PartsDB
The SQLAlchemy extension for registries of biological parts written by Mihails Delmans provides a nice framework for dealing with the nitty gritty of database handling for biological sequences.

```bash
# Go to the src directory and clone
git clone https://github.com/HaseloffLab/PartsDB
cd src/PartsDB
sudo pip install .
```

### PostgreSQL - https://www.postgresql.org
Download the PostgreSQL pre-built binaries https://www.postgresql.org/download/, install and run. Then create a database with a specified database name. This example uses dnarchive as database name.
```bash
createdb dnarchive
```

### Python libraries
- biopython - http://biopython.org
- SQLAlchemy - http://www.sqlalchemy.org
- Flask - http://flask.pocoo.org
- Flask-Sessions - https://pythonhosted.org/Flask-Session/
- Jinja2 - http://jinja.pocoo.org
- waitress - http://docs.pylonsproject.org/projects/waitress/en/latest/

Install through the requirements.txt file in the root of dnarchive git clone.

```bash
# Install through the requirements.txt file in the root of dnarchive
pip install -r requirements.txt
```

### Setup parameters in app.py
This git already contains a generated secret_key for the Flask app, but you might want to generate another one.
```bash
cd src
python secret_key.py
```
Copy the secret key onto `app.secret_key = '73234adae4dd527740b123211473c356b1df1d577e007b90'` in app.py.

Then replace the database name in `partsdb = PartsDB('postgresql:///dnarchive', clean = False, Base = Base)` where dnarchive is.

### Run the webserver and go to http://localhost:5000
```bash
python app.py
```