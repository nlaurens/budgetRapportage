Installation
------------

* Requires 
  web.py, mysqldb, xlsx2csv, 
  web.py-auth (https://github.com/galeo/web.py-auth v0.3)
 
* Setup config
  Copy config.py.example to config.py and fill out required fields (mysql)

* Initalize web.py-auth database:
    $ python server.py --init

Run
---

* Web.py has a stand alone webserver:
    $ python server.py <port# optional>

* Use WSGI mod from apache
    see: http://webpy.org/cookbook/mod_wsgi-apache

Usage
-----

* Edit config to match excel dumps of SAP (see example excels in /data/examples)
* Load excel files using the admin panel


Todo
----

add examples for ksgroup and ordergroups
