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

# Success Libraries / Librerías Success
from success.common.base.SuccessClass             import SuccessClass
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv
from success.common.types.WSGIApplication         import WSGIApplication
from success.core.app.SuccessAppBuilder           import SuccessAppBuilder
from success.core.app.SuccessDispatcherFactory    import SuccessDispatcherFactory

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessWSGIFactory ( SuccessClass ) :
  """
  WSGI application factory for the Success framework.

  Creates and configures WSGI applications according to the type and mode
  configured in SUCCESS_APP_TYPE and SUCCESS_APP_MODE environment variables.

  Purpose:
  ----------
  SuccessWSGIFactory is responsible for:
  - Interpreting SUCCESS_APP_TYPE (singleapp/multiapp)
  - Interpreting SUCCESS_APP_MODE (flask/path/subdomain/standard)
  - Validating valid type/mode combinations
  - Delegating construction to SuccessAppBuilder or SuccessDispatcherFactory

  Valid Combinations:
  ----------------------
  - singleapp + flask: Simple Flask application
  - singleapp + subdomain: Application with single subdomain
  - multiapp + standard: Multiple apps with DispatcherMiddleware
  - multiapp + path: Multiple apps with path-based dispatch
  - multiapp + subdomain: Multiple apps with subdomain dispatch

  Usage:
  ------
  factory = SuccessWSGIFactory()
  app = factory.build()  # Configured WSGIApplication

  Attributes:
    _logger: Logger for event logging.

  Raises:
    ValueError: If TYPE/MODE combination is invalid.

  Note:
    - SUCCESS_APP_TYPE defines if singleapp or multiapp
    - SUCCESS_APP_MODE defines the routing strategy
  """


  def __init__ ( self ) -> None :
    """
    Initialize the WSGI factory.
    """
    super ().__init__ ()


  def build ( self ) -> WSGIApplication :
    """
    Build and return a configured WSGI application.

    Reads SUCCESS_APP_TYPE and SUCCESS_APP_MODE, validates the combination,
    and delegates construction to the appropriate builder.

    Returns:
      WSGIApplication: Configured WSGI application (Flask or DispatcherMiddleware).

    Raises:
      ValueError: If TYPE/MODE combination is invalid.

    Note:
      - singleapp delegates to _buildSingleApp()
      - multiapp delegates to _buildMultiApp()
    """
    _type = SuccessSystemEnv.get ( "SUCCESS_APP_TYPE", "singleapp" ).lower ()
    _mode = SuccessSystemEnv.get (
      "SUCCESS_APP_MODE",
      SuccessSystemEnv.get ( "SUCCESS_APP_DOMAIN", "standard" if _type == "singleapp" else "standard" )
    ).lower ()

    self._logger.log ( f"Creating WSGI application in type=[{_type}] mode=[{_mode}].", "INFO" )

    if _type == "singleapp" and _mode not in [ "standard", "subdomain" ] :
      raise ValueError ( f"Invalid combination: SUCCESS_APP_TYPE={_type}, SUCCESS_APP_MODE={_mode}. Allowed for singleApp: flask|subdomain." )

    if _type == "multiapp" and _mode not in [ "standard", "path", "subdomain" ] :
      raise ValueError ( f"Invalid combination: SUCCESS_APP_TYPE={_type}, SUCCESS_APP_MODE={_mode}. Allowed for multiApp: standard|path|subdomain." )

    if _type == "singleapp" :
      return self._buildSingleApp ()

    elif _type == "multiapp" :
      return self._buildMultiApp ()

    else :
      raise ValueError ( f"Invalid SUCCESS_APP_TYPE: {_type}" )


  def _buildSingleApp ( self ) -> WSGIApplication :
    """
    Build a singleApp application (simple Flask).

    Uses SuccessAppBuilder to create a single Flask application
    based on SUCCESS_MAIN_APP.

    Returns:
      WSGIApplication: Configured Flask instance.

    Note:
      - SUCCESS_MAIN_APP defines the application to build
      - Defaults to 'success' as main app
    """
    builder = SuccessAppBuilder ( SuccessSystemEnv.get ( "SUCCESS_MAIN_APP", "success" ).lower () )

    return builder.build ()


  def _buildMultiApp ( self ) -> WSGIApplication :
    """
    Build a multiApp system (multiple applications).

    Uses SuccessDispatcherFactory to create a dispatcher that
    routes to multiple applications according to SUCCESS_APP_MODE.

    Returns:
      WSGIApplication: DispatcherMiddleware or specific strategy.

    Note:
      - SUCCESS_APP_MODE determines dispatch strategy
      - Loads main and secondary apps
    """
    builder = SuccessDispatcherFactory ()

    return builder.build ()
