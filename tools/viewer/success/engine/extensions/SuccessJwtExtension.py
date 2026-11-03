# Copyright [2026] [Filiberto Zaá Avila "remizero"]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Python Libraries / Librerías Python
from datetime           import datetime
from datetime           import timedelta
from flask              import current_app
from flask              import Flask
from flask              import json
from flask              import Response
from flask              import jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import decode_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import unset_jwt_cookies
from http               import HTTPStatus
from redis              import StrictRedis

# Application Libraries / Librerías de la Aplicación
from success.common.exceptions.RevokeJwtException import RevokeJwtException
from success.common.base.SuccessExtension         import SuccessExtension
from success.common.SuccessDebug                  import SuccessDebug
from success.common.tools.SuccessDatetime         import SuccessDatetime
from success.common.tools.SuccessHttp             import SuccessHttp

# Preconditions / Precondiciones
jwt_redis_blocklist = None


class SuccessJwtExtension ( SuccessExtension ) :
  """
  JWT (JSON Web Token) extension for the Success framework.

  Integrates Flask-JWT-Extended for JWT authentication,
  token management, and Redis-based token blocklisting.
  """


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the JWT extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    self._extension = JWTManager ()


  def config ( self ) -> None :
    """
    Configure the JWT extension with Redis blocklist.

    Sets up Redis connection for token blocklisting.
    """
    super ().config ()
    with self._app.app_context () :
      jwt_redis_blocklist = StrictRedis (
        host              = current_app.config [ 'REDIS_HOST' ],
        port              = current_app.config [ 'REDIS_PORT' ],
        db                = current_app.config [ 'REDIS_DB' ],
        decode_responses  = current_app.config [ 'REDIS_DECODE_RESPONSES' ]
      )


  @staticmethod
  def create ( response : Response ) -> tuple ( [ Response, str ] ) :
    """
    Create JWT tokens and add them to the response.

    Args:
      response: Flask response object.

    Returns:
      tuple: Tuple containing response and access token.
    """
    responseAux = response.get_json ()
    access_token = ''
    refresh_token = ''
    if ( SuccessSystemEnv.isTrue ( 'SUCCESS_OUTPUT_MODEL' ) ) :
      access_token = create_access_token ( identity = responseAux [ 'data' ] [ 0 ] [ 'username' ] )
      refresh_token = create_refresh_token ( identity = responseAux [ 'data' ] [ 0 ] [ 'username' ] )
      responseAux [ 'data' ] [ 0 ] [ 'token' ] = access_token

    else :
      access_token = create_access_token ( identity = responseAux [ 'username' ] )
      refresh_token = create_refresh_token ( identity = responseAux [ 'username' ] )
      responseAux [ 'token' ] = access_token

    response.data = json.dumps ( responseAux )
    set_access_cookies ( response, access_token )
    set_refresh_cookies ( response, refresh_token )

    return tuple ( [ response, access_token ] )


  @staticmethod
  def get () :
    """
    Get JWT token from request.

    Note:
      This method is a placeholder for future implementation.
    """
    pass


  @jwt_required ( refresh = True )
  def refresh () :
    """
    Refresh an expiring JWT token.

    Returns:
      Response: Response with new access token.
    """
    identity = get_jwt_identity ()
    access_token = create_access_token ( identity = identity )
    response = SuccessHttp.returnResponse ( { 'access_token' : access_token }, HTTPStatus.OK )
    set_access_cookies ( response, access_token )
    return response


  @jwt_required ( refresh = True )
  def refresh_expiring_jwts ( self, response ) :
    """
    Refresh JWT tokens that are about to expire.

    Args:
      response: Flask response object.

    Returns:
      Response: Response with refreshed token if needed.
    """
    #logger = SuccessLogger ( __name__ )
    try :
      exp_timestamp = get_jwt () [ 'exp' ]
      now = SuccessDatetime.getNow ()
      target_timestamp = datetime.timestamp ( now + timedelta ( seconds = 5 ) )
      if target_timestamp > exp_timestamp:
        access_token = create_access_token ( identity = get_jwt_identity () )
        set_access_cookies ( response, access_token )

      return response

    except ( RuntimeError, KeyError ) :
      self.__logger.uncatchErrorException ()
      # Case where there is not a valid JWT. Just return the original response
      return response


  def check_if_token_is_revoked ( jwt_header, jwt_payload : dict ) -> bool :
    """
    Check if a JWT token has been revoked.

    Args:
      jwt_header: JWT header.
      jwt_payload: JWT payload.

    Returns:
      bool: True if token is revoked, False otherwise.
    """
    jti = jwt_payload [ 'jti' ]
    token_in_redis = jwt_redis_blocklist.get ( jti )

    return token_in_redis is not None


  def logout ( self ) :
    """
    Logout by revoking the current JWT token.

    Returns:
      Response: JSON response indicating token revocation.
    """
    jti = get_jwt () [ 'jti' ]
    jwt_redis_blocklist.set ( jti, '', ex = current_app.config [ 'JWT_ACCESS_TOKEN_EXPIRES' ] )

    return jsonify ( msg = 'Access token revoked' )


  def policyDefaults ( self ) -> dict :
    """
    Get default policy settings for JWT.

    Returns:
      dict: Dictionary with default JWT policy settings.
    """
    tokenLocations = self._app.config.get ( "JWT_TOKEN_LOCATION", [] )
    if isinstance ( tokenLocations, str ) :
      tokenLocations = [ tokenLocations ]

    return {
      "require_jwt"          : False,
      "jwt_token_locations"  : tokenLocations or [],
      "jwt_cookie_protect"   : self._app.config.get ( "JWT_COOKIE_CSRF_PROTECT", False )
    }
