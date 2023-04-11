"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations

import peewee
from skirmserv.models import Database

from logging import getLogger

from argon2 import PasswordHasher  # used for password hashing
from hashlib import sha256  # used for token hashing

from secrets import token_urlsafe


class UserModel(peewee.Model):
    """
    Database Model to store User Accounts
    """

    # Todo: Check if 32 characters fit good on the phaser screen
    name = peewee.CharField(max_length=32)
    email = peewee.CharField()
    password = peewee.CharField(default="")

    # used as API Key and access_token to authenticate socketio comm
    # this field contains a hash of the token and the user has to save
    # it or re-create the token when lost
    access_token = peewee.CharField(default="")

    def set_password(self, plaintext_password: str) -> None:
        """Set Password of this user"""
        ph = PasswordHasher()
        self.password = ph.hash(plaintext_password)
        getLogger(__name__).debug("User %s set password.", str(self))

    def generate_access_token(self) -> str:
        """Generates an access_token, stores a hash of it and returns the
        plaintext value of the token. The token is urlsafe"""

        # Generating 32-Byte (256 bit) randomness
        plaintext_token = token_urlsafe(32)

        # Store the sha256 hash of it
        self.access_token = sha256(plaintext_token.encode("ASCII")).hexdigest()
        self.save()

        getLogger(__name__).debug("Generated new access token for user %s.", str(self))

        # Return the token
        return plaintext_token

    def check_password(self, plaintext_password: str) -> bool:
        """Check password of this user"""
        ph = PasswordHasher()
        try:
            return ph.verify(self.password, plaintext_password)
        except:
            return False

    def check_access_token(self, plaintext_token: str) -> bool:
        """Check if the plaintext token is valid"""
        return self.access_token == sha256(plaintext_token.encode("ASCII")).hexdigest()

    @staticmethod
    def register(name: str, email: str, plaintext_password: str) -> UserModel:
        """Creates and returns a new user model"""
        user = UserModel(
            name=name,
            email=email,
        )
        user.set_password(plaintext_password)
        user.save()
        getLogger(__name__).debug("Created new usermodel for user %s", str(user))
        return user

    @staticmethod
    def authenticate(email: str, plaintext_password: str) -> UserModel | None:
        """Returns an user model based on the given email and password"""
        user = UserModel.get_or_none(UserModel.email == email)
        if user is not None:
            if user.check_password(plaintext_password):
                return user
        return None

    @staticmethod
    def authenticate_by_token(access_token: str) -> UserModel | None:
        """Returns an user model based on the given plaintext access_token"""

        # Do not allow empty access_token's. Maybe not nessecary but better
        # safe than sorry :D
        if access_token == "":
            return

        token_hash = sha256(access_token.encode("ASCII")).hexdigest()
        user = UserModel.get_or_none(UserModel.access_token == token_hash)
        return user

    def __str__(self):
        return "{0} ({1})".format(self.name, self.id)

    class Meta:
        database = Database.get()


# Creating the table directly on import
Database.register_models(UserModel)
