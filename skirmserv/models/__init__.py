"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from peewee import SqliteDatabase
from peewee import MySQLDatabase
from peewee import PostgresqlDatabase
from flask import current_app
from logging import getLogger

from playhouse.shortcuts import ReconnectMixin


class ReconnectingMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


class ReconnectingPostgresqlDatabase(ReconnectMixin, PostgresqlDatabase):
    pass


class Database(object):
    instance = None

    @staticmethod
    def get():
        """Returns the current instance of the database connection"""
        if Database.instance is not None:
            return Database.instance._db
        else:
            Database()
            return Database.instance._db

    @staticmethod
    def register_models(*models):
        """Creates tabels for the models in the currently connected
        database"""
        db = Database.get()
        db.create_tables(models)

        for model in models:
            getLogger(__name__).debug("Registered table: %s", str(model))

    def __init__(self):
        # Don't override existing instance
        if Database.instance is not None:
            return
        Database.instance = self

        if current_app.config["DB_TYPE"] == "sqlite":
            getLogger(__name__).info(
                "SQLite DB Type configured @ " + current_app.config["DB_LOCATION"]
            )
            self._db = SqliteDatabase(current_app.config["DB_LOCATION"])

        elif current_app.config["DB_TYPE"] == "mysql":
            getLogger(__name__).info(
                "MySQL DB Type configured @ {0} ({1})".format(
                    current_app.config["DB_HOST"], current_app.config["DB_DATABASE"]
                )
            )
            self._db = ReconnectingMySQLDatabase(
                current_app.config["DB_DATABASE"],
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASS"],
                host=current_app.config["DB_HOST"],
                port=current_app.config.get("DB_PORT", 3306),
            )

        elif current_app.config["DB_TYPE"] == "postgresql":
            getLogger(__name__).info(
                "Postgresql DB Type configured @ {0} ({1})".format(
                    current_app.config["DB_HOST"], current_app.config["DB_DATABASE"]
                )
            )
            self._db = ReconnectingPostgresqlDatabase(
                current_app.config["DB_DATABASE"],
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASS"],
                host=current_app.config["DB_HOST"],
                port=current_app.config.get("DB_PORT", 5432),
            )

        else:
            # Remove this instance if no valid DB_TYPE is configured
            Database.instance = None
