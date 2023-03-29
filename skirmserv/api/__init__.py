"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from skirmserv.models.user import UserModel

from flask import request
from flask_restful import abort

from functools import wraps


def requires_auth(endpoint):
    """
    Wraps an endpoint that requires a valid access token to be
    set in the x-access-token header. Aborts the request if no
    user could be authenticated
    """

    @wraps(endpoint)
    def validate_access_token_or_abort(*args, **kwargs):
        """
        Returns the authenticated usermodel object or aborts the
        request if the token isn't valid
        """

        # Get the token from the x-access-token header
        token = request.headers.get("x-access-token")

        # Check if there is a user with this token
        # also checking if the token is None and setting the user model
        # directly to none
        user = UserModel.authenticate_by_token(token) if token else None

        # If there is no user, abort with not authenticated method
        if user is None:
            abort(401, message="Your access token is not valid")

        # Else set the user as argument for the endpoint
        kwargs.update({"user": user})
        return endpoint(*args, **kwargs)

    return validate_access_token_or_abort
