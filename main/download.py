__author__ = 'Vincent'

from injector import Module, Key, provides, Injector, inject, singleton
import mysql.connector


class RequestHandler(object):
    @inject(db=mysql.connector.MySQLConnection)
    def __init__(self, db):
        self._db = db

    def get(self):
        cursor = self._db.cursor()
        cursor.execute('SELECT key, value FROM data ORDER BY key')
        return cursor.fetchall()


Configuration = Key('configuration')


def configure_for_testing(binder):
    configuration = {
        'db_connection_string': 'host="localhost", user="root", password="capic_20_04_1982", database="plowshare"'}
    binder.bind(Configuration, to=configuration, scope=singleton)


class DatabaseModule(Module):
    @singleton
    @provides(mysql.connector.MySQLConnection)
    @inject(configuration=Configuration)
    def provide_sqlite_connection(self, configuration):
        conn = mysql.connector.connect(configuration['db_connection_string'])
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS data (key PRIMARY KEY, value)')
        cursor.execute('INSERT OR REPLACE INTO data VALUES ("hello", "world")')

        return conn


injector = Injector([configure_for_testing, DatabaseModule()])
handler = injector.get(RequestHandler)
tuple(map(str, handler.get()[0]))