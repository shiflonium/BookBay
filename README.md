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

identifed by = password

```
mysql> grant all privileges on softeng.* to 'apps'@'localhost';
```

```
mysql> flush privileges;
```


After this, you can run python db_create
