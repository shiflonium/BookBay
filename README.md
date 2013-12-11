# blah blah

## if you choose to install virtualenv in hidden folder, do this


# Any DB issues:

Since i should be updating db models quite a few times, the best way(from experience without errors) to get
most recent copy of DB is to

1. log in to mysql

```
mysql> DROP DATABASE softeng;
mysql> CREATE DATABASE softeng;
```

then in the project directory

```
$ rm -r db_repository
```

then run

```
$ python db_create
```

these steps should ensure that you get a clean version of the database. when only small changes to the model are made,
running db_migrate && db_upgrade should be sufficient


```
$ virtualenv --no-site-packages --distribute .env && source .env/bin/activate && pip install -r requirements.txt
```

```
source .env/bin/activate
```

```
deactivate
```

#setting etting up mysql

access your mysql database
```
$ mysql -u root -p
```

then, setup database parameters:
```
mysql> create database softeng character set utf8 collate utf8_bin;
```

```
mysql> create user 'softeng'@'localhost' identified by 'softeng';
```

password is now set as 'softeng'

```
mysql> grant all privileges on softeng.* to 'softeng'@'localhost';
```

```
mysql> flush privileges;
```

for simplicity sake, the username and pw = softeng softeng
After this, you can run python db_create

After you completed the above steps, go to project directory and run the server:
```
$ python runserver.py
```

If your views.py contains no errors, you should be able to access your web application 
by typing the address http://127.0.0.1:5000 in your browser's address bar.