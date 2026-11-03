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
from dotenv import dotenv_values
from flask  import json
from typing import Any
from typing import Optional
from typing import Dict
from typing import List
import os

# Success Libraries / Librerías Success
from success.common.base.SuccessClass             import SuccessClass
from success.common.tools.SuccessEnv              import SuccessEnv
from success.common.path.SuccessPathUtils         import SuccessPathUtils
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv

# Preconditions / Precondiciones


class SuccessAppEnv ( SuccessClass ) :
  """
  Provider of application-specific environment variables.

  This class loads and provides access to environment variables from
  .env files specific to each application. Unlike SuccessSystemEnv, each
  SuccessAppEnv instance maintains its own dictionary of variables,
  allowing isolated configuration per application.

  Purpose:
  ----------
  SuccessAppEnv is the interface for accessing application-specific
  configuration in multi-app environments:
  - APP_NAME (specific app name)
  - APP_PORT (dedicated port)
  - DATABASE_URL (app-specific connection)
  - Extension configuration per app
  - And any application-specific variables

  Typical Usage:
  -----------
  # Create instance for a specific application
  app_env = SuccessAppEnv('/apps/synthetos')

  # Get app-specific values
  app_env.get('APP_NAME')
  app_env.get('DATABASE_URL')

  # Get typed values
  app_env.isTrue('DEBUG_ENABLED')
  app_env.toInt('APP_PORT')
  app_env.toList('ALLOWED_ORIGINS')
  app_env.getJson('EXTENSION_CONFIG')

  Architecture:
  -------------
  - Requires instance (one per application)
  - Uses dotenv_values() to load into _data dictionary
  - Each instance has its own configuration isolation
  - Delegates value conversion to SuccessEnv

  Multi-App Support:
  ------------------
  In multi-app mode, each application has its own .env file:
  - /apps/synthetos/.env → SuccessAppEnv('/apps/synthetos')
  - /apps/llogos/.env → SuccessAppEnv('/apps/llogos')
  - /apps/prueba_view/.env → SuccessAppEnv('/apps/prueba_view')

  Attributes:
      _data (Dict[str, Optional[str]]): Dictionary with variables
                                       loaded from .env.

  Note:
    - Variables are NOT loaded into os.environ, they remain isolated
    - Ideal for configuration that varies between applications
    - For global framework configuration, use SuccessSystemEnv
  """

  _data : Dict [ str, Optional [ str ] ] = None


  def __init__ ( self, envFilePath : str = None ) -> None :
    """
    Initialize SuccessAppEnv loading variables from a .env file.

    Args:
      envFilePath: Path to the application directory or .env file.
                  If None, searches in the default path relative
                  to this module.

    Example:
      # Load from application directory
      app_env = SuccessAppEnv('/apps/synthetos')

      # Load from specific file
      app_env = SuccessAppEnv('/apps/synthetos/.env')
    """
    super ().__init__ ()
    self._data = self._loadAppEnv ( envFilePath )
    self._applyGlobalNetworkVars ()


  def _applyGlobalNetworkVars ( self ) -> None :
    """
    Inyecta solo variables de red globales para centralización:
    APP_PORT, BASE_URL, SERVER_NAME.
    """
    keys = [ "APP_PORT", "BASE_URL", "SERVER_NAME" ]

    for key in keys :
      globalValue = SuccessSystemEnv.get ( key, None )

      # Si no existe valor global, no forzamos nada (compatibilidad)
      if globalValue is None :
        continue

      globalValue = str ( globalValue ).strip ()
      if globalValue == "" :
        continue

      appValue = self._data.get ( key, None )

      # Aviso si la app tenía otro valor distinto
      if appValue is not None and str ( appValue ).strip () not in [ "", globalValue ] :
        self._logger.log (
          f"'{key}' en app .env fue sobrescrita por valor global '{globalValue}'.",
          "WARNING"
        )

      # Fuente única de verdad: global manda
      self._data [ key ] = globalValue


  def _loadAppEnv ( self, envFilePath : str = None ) -> Dict [ str, Optional [ str ] ] :
    """
    Load environment variables from a .env file into a dictionary.

    Internal method that uses dotenv_values() to read the .env file
    and return a dictionary with the loaded variables.

    Args:
      envFilePath: Path to the .env file. If None, uses the default path.

    Returns:
      Dictionary with loaded variables. Keys are variable names and
      values are strings or None.

    Note:
      - Variables are NOT loaded into os.environ
      - The returned dictionary is independent per instance
    """
    return dotenv_values ( SuccessPathUtils.getEnvPath ( envFilePath ) )


  def get ( self, key : str, default : Any = None ) -> Optional [ str ] :
    """
    Get the value of an application-specific environment variable.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      The variable value, or the default if it does not exist.

    Example:
      app_env.get('APP_NAME', 'DefaultApp')
      app_env.get('DATABASE_URL')
    """
    return self._data.get ( key, default )


  def getJson ( self, key : str, default : Any = None ) -> Any :
    """
    Get and parse an environment variable as JSON.

    Args:
      key: Name of the app-specific environment variable.

    Returns:
      The parsed JSON object.

    Raises:
      json.JSONDecodeError: If the value is not valid JSON.

    Example:
      app_env.getJson('EXTENSION_CONFIG')  # → {'enabled': True, ...}
    """
    return SuccessEnv.getJson ( self.get ( key, default ) )


  def isEmpty ( self, key : str, default : Any = False ) -> bool :
    """
    Check if an application-specific environment variable is empty.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      True if the variable exists but is empty, False otherwise.
      Returns False if the variable does not exist.

    Example:
      app_env.isEmpty('OPTIONAL_CONFIG')
    """
    value = self._data.get ( key )
    if value is None :
      return False
    
    return SuccessEnv.isEmpty ( value )


  def isNone ( self, key : str, default : Any = False ) -> bool :
    """
    Check if an application-specific environment variable has the value 'none'.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      True if the value is 'none' (case-insensitive), False otherwise.
      Returns False if the variable does not exist or is None.

    Example:
      app_env.isNone('DATABASE_URL')  # True if value is 'none'
    """
    value = self._data.get ( key )
    if value is None :
      return False
    
    return SuccessEnv.isNone ( value )


  def isTrue ( self, key : str, default : Any = False ) -> bool :
    """
    Check if an application-specific environment variable is set to 'true'.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      True if the value is 'true' (case-insensitive), False otherwise.
      Returns False if the variable does not exist or is None.

    Example:
      app_env.isTrue('DEBUG_ENABLED')
      app_env.isTrue('EXTENSION_CORS')
    """
    value = self._data.get ( key )
    if value is None :
      return default
    
    return SuccessEnv.isTrue ( value )


  def toInt ( self, key : str, default : Any = 0 ) -> int :
    """
    Get and convert an application-specific environment variable to an integer.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      The value converted to int, or the default if it does not exist.

    Raises:
      ValueError: If the value cannot be converted to an integer.

    Example:
      app_env.toInt('APP_PORT')  # → 5000
    """
    value = self._data.get ( key )
    if value is None :
      return default
    
    return SuccessEnv.toInt ( value )


  def toList ( self, key : str, default : Any = [] ) -> List [ Any ] :
    """
    Get and convert an application-specific environment variable to a list.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      The converted list. Returns [] if the variable does not exist or is empty.

    Example:
      app_env.toList('ALLOWED_ORIGINS')  # → ['http://localhost', ...]
    """
    value = self._data.get ( key )
    if value is None :
      return default if default is not None else []
    
    return SuccessEnv.toList ( value )
