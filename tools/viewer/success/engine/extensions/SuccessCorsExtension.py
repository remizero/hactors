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
from flask      import Flask
from flask_cors import CORS

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessExtension import SuccessExtension
from success.common.tools.SuccessEnv      import SuccessEnv

# Preconditions / Precondiciones


class SuccessCorsExtension ( SuccessExtension ) :
  """
  CORS (Cross-Origin Resource Sharing) extension for the Success framework.

  Integrates Flask-CORS for handling cross-origin requests
  and configuring CORS policies.

  Attributes:
    _corsConfigDefault (dict): Default CORS configuration.
    _resources (dict): CORS resources configuration.
    _supportsCredentials (bool): Whether credentials are supported.
  """

  _corsConfigDefault   : dict = {}
  _resources           : dict = None
  _supportsCredentials : bool = False


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the CORS extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    self._extension = CORS ()
    self._corsConfigDefault = {
      r"*" : {
        "origins"        : [ "/*" ],
        "methods"        : [ "DELETE", "GET", "POST", "PUT" ],
        "allow_headers"  : [ "Authorization", "Content-Type", "X-Requested-With", "Accept", "Set-Cookie" ],
        "expose_headers" : [ "Content-Type", "X-CSRFToken" ]
      }
    }
    self.config ()


  def config ( self ) -> None :
    """
    Configure CORS resources based on application configuration.

    Reads CORS configuration from app config and sets up resources
    accordingly.
    """
    # DO NOT MODIFY (BEGIN) / NO MODIFICAR (INICIO)
    if ( not SuccessEnv.isEmpty ( self._app.config [ 'CORS_RESOURCES_APP_RESOURCES' ] ) ) :
      self._resources = SuccessEnv.getCorsResources ( self._app.config )

    elif ( not SuccessEnv.isEmpty ( self._app.config [ 'CORS_RESOURCES' ] ) ) :
      # TODO Que hacer aqui
      self._resources = self._corsConfigDefault

    else :
      self._resources = self._corsConfigDefault
    # DO NOT MODIFY (END) / NO MODIFICAR (FIN)


  def register ( self ) -> None :
    """
    Register the CORS extension with the Flask application.

    Initializes CORS with configured resources and credentials support.
    """
    if ( self._app.config [ 'CORS_SUPPORTS_CREDENTIALS' ] != '' ) :
      self._supportsCredentials = SuccessEnv.isTrue ( self._app.config [ 'CORS_SUPPORTS_CREDENTIALS' ] )

    self._extension.init_app (
      app                  = self._app,
      resources            = self._resources,
      supports_credentials = self._supportsCredentials
    )


  def policyDefaults ( self ) -> dict :
    """
    Get default policy settings for CORS.

    Returns:
      dict: Dictionary with default CORS policy settings.
    """
    allowedOrigins = self._toList ( self._app.config.get ( "CORS_ORIGINS" ) )
    requireCors    = bool ( allowedOrigins ) and "*" not in allowedOrigins
    return {
      "require_cors"    : requireCors,
      "allowed_origins" : allowedOrigins
    }


  def _toList ( self, value ) -> list :
    """
    Convert a value to a list of strings.

    Args:
      value: Value to convert (list, tuple, set, string, or None).

    Returns:
      list: List of string values.
    """
    if value is None :
      return []

    if isinstance ( value, list ) :
      return [ str ( item ) for item in value ]

    if isinstance ( value, tuple ) :
      return [ str ( item ) for item in value ]

    if isinstance ( value, set ) :
      return [ str ( item ) for item in value ]

    if isinstance ( value, str ) :
      value = value.strip ()
      if not value :
        return []

      if value.startswith ( "[" ) and value.endswith ( "]" ) :
        raw = value [ 1 : -1 ]
        return [ item.strip ().strip ( "'" ).strip ( '"' ) for item in raw.split ( "," ) if item.strip () ]

      return [ value ]

    return [ str ( value ) ]
