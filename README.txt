Installation
------------

* Requires 
  web.py, mysqldb, iptools, xlsx2csv

* Setup config
  Copy config.py.example to config.py and fill out required fields (mysql)

* Setup sap date and load data
  open: http://localhost:8081/admin/1

Todo/Bugs
---------
* update readme ;)
* Maybe one day for wbs: http://jsfiddle.net/jhfrench/GpdgF/
* Add config and orderlijst table to database status in admin panel


Usage
-----

* Start als server

    Als losse service
        -> $ python server.py 8081 

    In TMUX
    * Start/Enter tmux attach
    * Stop the server (ctrl + c)
    * Rotate log
        -> copy server.log -> server.log.x
        -> remove server.log
    * Restart server:
        -> $ python server.py 8081 > server.log


* Webbrowser
    http://localhost:8081/login/<USER HASH>
    http://localhost:8081/salaris/<USER HASH>
	    http://localhost:8081/view/<USER HASH>
    http://localhost:8081/report/<USER HASH>
    http://localhost:8081/admin
