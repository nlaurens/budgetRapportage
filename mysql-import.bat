echo off
setlocal enabledelayedexpansion
FOR %%f IN ("*.csv") DO (
  set old=%%~dpnxf
  set new=!old:\=\\!
  mysql -e "load data local infile '"!new!"' IGNORE into table <db>.<table> COLUMNS TERMINATED BY ','" -u root
  echo %%~nxf DONE
)
