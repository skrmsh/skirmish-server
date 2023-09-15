"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import abort

from skirmserv.models.user import UserModel
from skirmserv.api import requires_auth

from flasgger import swag_from

from logging import getLogger

# Request argument parser for user registration.
user_register_reqparse = reqparse.RequestParser()
user_register_reqparse.add_argument(
    "name", type=str, help="name field is required", required=True
)
user_register_reqparse.add_argument(
    "email", type=str, help="email field is required", required=True
)
user_register_reqparse.add_argument(
    "password", type=str, help="password field is required", required=True
)


class UserAPI(Resource):
    @requires_auth
    @swag_from("openapi/user/get.yml")
    def get(self, user: UserModel):
        """Returns base information about the user"""
        return {"username": user.name, "email": user.email}

    @swag_from("openapi/user/post.yml")
    def post(self):
        """Registers a new user.
        Todo: Figure out if its a good idea to do this
        via the api, or move it to a web interface?"""
        args = user_register_reqparse.parse_args()

        # Check if there is already a user with this email address
        existing_user = UserModel.get_or_none(UserModel.email == args.get("email"))
        if existing_user is not None:
            abort(409, message="Email Adress already in use!")

        user = UserModel.register(
            args.get("name"), args.get("email"), args.get("password")
        )

        access_token = user.generate_access_token()

        getLogger(__name__).info("Created user %s via API", str(user))

        return {"message": "user_created", "access_token": access_token}, 201

    @requires_auth
    def delete(self, user: UserModel):
        """Delete an authenticated user profile"""
        getLogger(__name__).info("Delted user %s via API", str(user))
        user.delete_instance()
        return {}, 204


# Request argument parser for users to login
user_login_reqparse = reqparse.RequestParser()
user_login_reqparse.add_argument(
    "email", type=str, help="Email field is required to login", required=True
)
user_login_reqparse.add_argument(
    "password", type=str, help="Password field is required to login", required=True
)


class AuthAPI(Resource):
    @swag_from("openapi/user/auth_post.yml")
    def post(self):
        """
        Creates a new access token for the user authenticated by email and
        password
        """
        # parse args
        args = user_login_reqparse.parse_args()

        # get user model by email and password
        user = UserModel.authenticate(args.get("email"), args.get("password"))
        if user is None:
            abort(401, message="Invalid email or password")

        # Generate a new access token
        access_token = user.generate_access_token()

        getLogger(__name__).debug("Authenticated user %s via API", str(user))

        return {"message": "authenticated", "access_token": access_token}, 200
