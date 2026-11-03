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
from dotenv import load_dotenv
from flask  import json
from typing import Any
from typing import List
import os

# Success Libraries / Librerías Success
from success.common.tools.SuccessEnv      import SuccessEnv
from success.common.path.SuccessPathUtils import SuccessPathUtils

# Preconditions / Precondiciones


class SuccessSystemEnv () :
  """
  Provider of global environment variables for the Success framework.

  This class provides access to system environment variables loaded from
  .env files via load_dotenv(). Loaded variables are available globally
  throughout the application process.

  Purpose:
  ----------
  SuccessSystemEnv is the main interface for accessing Success framework
  configuration that is shared across all applications:
  - SUCCESS_APP_MODE (singleapp/multiapp)
  - SUCCESS_MAIN_APP
  - SUCCESS_SECONDARY_APPS
  - FLASK_ENV
  - SERVER_NAME
  - And all system environment variables

  Typical Usage:
  -----------
  # Get simple values
  SuccessSystemEnv.get('FLASK_ENV', 'development')
  SuccessSystemEnv.get('SERVER_NAME')

  # Get typed values
  SuccessSystemEnv.isTrue('DEBUG_MODE')      # → bool
  SuccessSystemEnv.toInt('APP_PORT')         # → int
  SuccessSystemEnv.toList('ALLOWED_HOSTS')   # → list
  SuccessSystemEnv.getJson('CORS_ORIGINS')   # → dict

  # Load .env file
  SuccessSystemEnv.loadEnv('/path/to/.env')

  Architecture:
  -------------
  - All methods are static (no instance required)
  - Uses os.environ as underlying storage
  - Delegates value conversion to SuccessEnv
  - Does not inherit from any base class

  Thread-Safety:
  --------------
  os.environ is thread-safe in Python. Reads are atomic.
  Writes (via loadEnv) should only be done during initialization.

  Note:
      - Loaded variables persist for the entire process lifetime
      - Do not use for application-specific configuration
      - For per-application configuration, use SuccessAppEnv
  """


  @staticmethod
  def loadEnv ( envFilePath : str = None ) -> None :
    """
    Load environment variables from a .env file into global os.environ.

    Searches for the .env file at the specified path or at the default
    path relative to this module. Loaded variables replace existing ones.

    Args:
      envFilePath: Path to the .env file. If None, uses the default path.

    Note:
      - Uses override=True, so existing variables are replaced
      - Should be called during framework initialization
      - Loaded variables are available for the entire application

    Example:
      SuccessSystemEnv.loadEnv()  # Load from default path
      SuccessSystemEnv.loadEnv('/apps/myapp/.env')  # Load from specific path
    """
    load_dotenv ( SuccessPathUtils.getEnvPath ( envFilePath ), override = True )


  @staticmethod
  def get ( key : str, default : Any = None ) -> str :
    """
    Get the value of a system environment variable.

    Args:
      key: Name of the environment variable.
      default: Default value if the variable does not exist.

    Returns:
      The variable value, or the default if it does not exist.

    Example:
      SuccessSystemEnv.get('FLASK_ENV', 'development')
      SuccessSystemEnv.get('DATABASE_URL')
    """
    return os.environ.get ( key, default )


  @staticmethod
  def getJson ( key : str ) -> Any :
    """
    Get and parse an environment variable as JSON.

    Args:
      key: Name of the environment variable.

    Returns:
      The parsed JSON object.

    Raises:
      json.JSONDecodeError: If the value is not valid JSON.

    Example:
      SuccessSystemEnv.getJson('CORS_ORIGINS')  # → ['http://localhost', ...]
    """
    return SuccessEnv.getJson ( SuccessSystemEnv.get ( key ) )


  @staticmethod
  def isEmpty ( key : str ) -> bool :
    """
    Check if an environment variable is empty.

    Args:
      key: Name of the environment variable.

    Returns:
      True if the variable exists but is empty, False otherwise.

    Example:
      SuccessSystemEnv.isEmpty('OPTIONAL_VALUE')
    """
    return SuccessEnv.isEmpty ( SuccessSystemEnv.get ( key ) )


  @staticmethod
  def isNone ( key : str ) -> bool :
    """
    Check if an environment variable has the value 'none'.

    Args:
      key: Name of the environment variable.

    Returns:
      True if the value is 'none' (case-insensitive), False otherwise.

    Example:
      SuccessSystemEnv.isNone('DATABASE_URL')  # True if value is 'none'
    """
    return SuccessEnv.isNone ( SuccessSystemEnv.get ( key ) )


  @staticmethod
  def isTrue ( key : str ) -> bool :
    """
    Check if an environment variable is set to 'true'.

    Args:
      key: Name of the environment variable.

    Returns:
      True if the value is 'true' (case-insensitive), False otherwise.
      Returns False if the variable does not exist.

    Example:
      SuccessSystemEnv.isTrue('DEBUG_MODE')
      SuccessSystemEnv.isTrue('CORS_ENABLED')
    """
    return SuccessEnv.isTrue ( SuccessSystemEnv.get ( key, 'false' ) )


  @staticmethod
  def toInt ( key : str ) -> int :
    """
    Get and convert an environment variable to an integer.

    Args:
      key: Name of the environment variable.

    Returns:
      The value converted to int.

    Raises:
      ValueError: If the value cannot be converted to an integer.

    Example:
      SuccessSystemEnv.toInt('APP_PORT')  # → 5000
    """
    return SuccessEnv.toInt ( SuccessSystemEnv.get ( key ) )


  @staticmethod
  def toList ( key : str ) -> List [ Any ] :
    """
    Get and convert an environment variable to a list.

    Args:
      key: Name of the environment variable.

    Returns:
      The converted list. Returns [] if the variable does not exist or is empty.

    Example:
      SuccessSystemEnv.toList('ALLOWED_HOSTS')  # → ['localhost', '127.0.0.1']
    """
    return SuccessEnv.toList ( SuccessSystemEnv.get ( key ) )
