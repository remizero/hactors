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
from copy   import copy
from flask  import Flask
from typing import Any
from typing import Dict
from typing import Optional
import re
import uuid

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                 import SuccessClass
from success.common.infra.config.SuccessAppEnv        import SuccessAppEnv
from success.common.infra.logger.SuccessLogger        import SuccessLogger
from success.common.tools.SuccessPathResolver         import SuccessPathResolver
from success.engine.infrastructure.SuccessHookManager import SuccessHookManager
from success.common.base.SuccessExtension             import SuccessExtension

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessBuildContext ( SuccessClass ) :
  """
  Build context that travels through the initialization chain.

  Contains all configuration and dependencies needed to build
  a Success application. Passed explicitly between components
  of the build flow.

  Purpose:
  ----------
  SuccessBuildContext groups all information needed for building
  a Success application, avoiding the use of global state and making
  dependencies explicit and easy to trace.

  This object is created once per application under construction and
  passed through the entire initialization chain:

  1. SuccessAppBuilder: Creates the context
  2. SuccessWSGIFactory: Receives and passes the context
  3. SuccessEndpointsLoader: Receives and passes the context
  4. SuccessEndpointBuilder: Receives and uses the context
  5. SuccessViewOptionsBuilder / SuccessRestfulOptionsBuilder: Use the context

  Typical Usage:
  -----------
  # Create context from application information
  ctx = SuccessBuildContext.from_app('synthetos', '/apps/synthetos')

  # Pass through build chain
  factory = SuccessWSGIFactory(build_ctx=ctx)
  app = factory.build()

  # Access in builders
  class SuccessViewOptionsBuilder:
    def __init__(self, build_ctx: SuccessBuildContext):
      self._ctx = build_ctx
      self.__appEnv = build_ctx._appEnv  # Explicit access

  Architecture:
  -------------
  - Each application under construction has its own instance
  - No shared state between applications
  - Thread-safe by design (each thread has its own object)
  - Easy to test (direct mock of the object)

  Attributes:
    appName (str): Unique name of the application under construction.
    appPath (str): Absolute path to the application directory.
    _appEnv (SuccessAppEnv): Provider of application-specific environment variables.
    config_dict (dict): Raw configuration dictionary from .env.
    protocol (str): Default protocol ('view' or 'restful').
    logger (SuccessLogger): Application-specific logger.
    session_id (str): Unique session ID for this build.
    scope (str): Application scope ('application' or 'framework').

  Note:
    - This object is immutable after initial construction
    - Use for_protocol() to create variants with different protocol
    - Logger is initialized during app building
  """
  _app          : Optional [ Flask ]               = None
  _appEnv       : Optional [ SuccessAppEnv ]       = None
  _appName      : str                              = None
  _appPath      : str                              = None
  _hooks        : Optional [ SuccessHookManager ]  = None
  _pathResolver : Optional [ SuccessPathResolver ] = None
  _extensions   : Dict [ str, SuccessExtension ]   = {}


  def __init__ ( self, appName : str, appPath : str ) -> None :
    """
    Initialize an empty build context.

    Note:
      Use SuccessBuildContext.from_app() to create a fully
      initialized context from application information.
    """
    super ().__init__ ()
    self._logger.log ( f"Creating build context for application {appName}", "INFO" )

    self._appName      = appName
    self._appPath      = appPath
    self._appEnv       = SuccessAppEnv ( self._appPath )
    self._pathResolver = SuccessPathResolver ( self._appPath )
    self._hooks        = SuccessHookManager ( self._appPath ) or SuccessHookManager.null ()
    self._hooks.register ()
    self._extensions   = {}

    self._logger.log ( f"Finished creating build context for application {appName}", "INFO" )


  def _determine_scope ( self ) -> str :
    """
    Determine the application scope based on its configuration.

    Returns:
      str: 'application' for user apps, 'framework' for Success internal.
    """
    if self._appName.startswith ( 'success' ) or self._appName == 'success' :
      return 'framework'

    return 'application'


  def get ( self, key : str, default : Any = None ) -> Any :
    """
    Get a configuration value from the app dictionary.

    Utility method for accessing configuration values without
    directly accessing config_dict.

    Args:
      key (str): Configuration key name.
      default: Default value if key does not exist.

    Returns:
      The configuration value or default if not found.

    Example:
      ctx.get('appName', 'DefaultApp')  # → 'Synthetos'
      ctx.get('DEBUG_MODE', False)       # → True
    """
    return self._appEnv.get ( key, default )


  def getApp ( self ) -> Flask :
    """
    Get the Flask application instance.

    Returns:
      Flask: The Flask application instance.
    """
    return self._app


  def isTrue ( self, key : str, default : bool = False ) -> bool :
    """
    Check if a configuration value is 'true'.

    Utility method that delegates to _appEnv.isTrue() for consistency.

    Args:
      key (str): Configuration key name.
      default (bool): Default value if key does not exist.

    Returns:
      bool: True if value is 'true' (case-insensitive), False otherwise.

    Example:
      ctx.isTrue('DEBUG_MODE')      # → True
      ctx.isTrue('CORS_ENABLED')    # → False
    """
    return self._appEnv.isTrue ( key, default )


  def setApp ( self, app : Flask ) -> None :
    """
    Set the Flask application instance.

    Args:
      app (Flask): The Flask application instance.
    """
    self._app = app


  def to_int ( self, key : str, default : int = 0 ) -> int :
    """
    Get and convert a configuration value to integer.

    Utility method that delegates to _appEnv.toInt() for consistency.

    Args:
      key (str): Configuration key name.
      default (int): Default value if key does not exist.

    Returns:
      int: The value converted to int, or default if not found.

    Example:
      ctx.to_int('APP_PORT', 5000)    # → 5001
      ctx.to_int('MAX_RETRIES', 3)    # → 5
    """
    try :
      return self._appEnv.toInt ( key, default )

    except ( ValueError, TypeError ) :
      return default


  def to_list ( self, key : str, default : list = [] ) -> list :
    """
    Get and convert a configuration value to list.

    Utility method that delegates to _appEnv.toList() for consistency.

    Args:
      key (str): Configuration key name.

    Returns:
      list: The converted list. Returns [] if key does not exist.

    Example:
      ctx.to_list('ALLOWED_HOSTS')  # → ['localhost', '127.0.0.1']
    """
    return self._appEnv.toList ( key, default )


  def getExtension ( self, extensionName : str ) -> SuccessExtension | None :
    """
    Retrieves an extension from the current application.

    Searches through multiple locations including app extensions, Flask app extensions,
    and success namespace using various alias keys.

    Args:
      extensionName (str): The name of the extension to retrieve.

    Returns:
      SuccessExtension: The extension instance.

    Raises:
      RuntimeError: If the current application cannot be determined.
    """
    key       = self._normalizeExtensionKey ( extensionName )
    extension = self._extensions.get ( key )
    if extension is not None :
      return extension

    return None


  def setExtension ( self, extensionName : str, extensionInstance : SuccessExtension ) :
    """
    Registers an extension with the current application.

    Stores the extension under multiple alias keys for flexible retrieval.

    Args:
      extensionName (str): The name of the extension.
      extensionInstance (SuccessExtension): The extension instance to register.
    """
    extensionNameNormalized                      = self._normalizeExtensionKey ( extensionName )
    self._extensions [ extensionNameNormalized ] = extensionInstance


  def _normalizeExtensionKey ( self, key : str ) -> str :
    """
    Normalizes an extension key by stripping whitespace and converting to lowercase.

    Args:
      key (str): The extension key to normalize.

    Returns:
      str: The normalized extension key.
    """
    return str ( key or "" ).strip ().lower ()
