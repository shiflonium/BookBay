# blah blah

## if you choose to install virtualenv in hidden folder, do this


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
