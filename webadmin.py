"""
TODO
"""
import web
from config import config
import model


def checkDB():
    msg = ["Checking tables..."]
    tables = ['geboekt', 'obligo', 'plan', 'salaris', 'test']
    for table in tables:
        if model.check_table_exists(table):
            msg.append(table + " " + "ok")
        else:
            msg.append(table + " " + "FAIL")

    return msg
