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
import sys
import inspect
import os

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAppMode () :
  """
  Utility class for checking the application execution mode.

  Provides static methods to check the current environment and mode
  of the Success application (development, production, testing, etc.).
  """


  @staticmethod
  def __isMode ( mode : str ) -> bool :
    """
    Check if the current mode matches the specified mode.

    Args:
      mode (str): Name of the mode to check.

    Returns:
      bool: True if current mode matches, False otherwise.
    """

    return os.environ.get ( 'APP_ENV' ) == mode


  @staticmethod
  def isDebugMode () -> bool :
    """
    Check if the application is in debug mode.

    Returns:
      bool: True if FLASK_DEBUG or DEBUG is enabled, False otherwise.
    """

    return bool ( os.environ.get ( 'FLASK_DEBUG' ) ) or bool ( os.environ.get ( 'DEBUG' ) )


  @staticmethod
  def isDefaultMode () -> bool :
    """
    Check if the application is in default mode.

    Returns:
      bool: True if current mode is 'default', False otherwise.
    """

    return SuccessAppMode.__isMode ( 'default' )


  @staticmethod
  def isDevelopmentMode () -> bool :
    """
    Check if the application is in development mode.

    Returns:
      bool: True if current mode is 'development', False otherwise.
    """

    return SuccessAppMode.__isMode ( 'development' )


  @staticmethod
  def isLocalMode () -> bool :
    """
    Check if the application is in local mode.

    Returns:
      bool: True if current mode is 'local', False otherwise.
    """

    return SuccessAppMode.__isMode ( 'local' )


  @staticmethod
  def isProductionMode () -> bool :
    """
    Check if the application is in production mode.

    Returns:
      bool: True if current mode is 'production', False otherwise.
    """

    return SuccessAppMode.__isMode ( 'production' )


  @staticmethod
  def isTestingMode () -> bool :
    """
    Check if the application is in testing mode.

    Returns:
      bool: True if SUCCESS_TESTING is enabled, False otherwise.
    """

    return bool ( os.environ.get ( 'SUCCESS_TESTING' ) )


  @staticmethod
  def isStagingMode () -> bool :
    """
    Check if the application is in staging mode.

    Returns:
      bool: True if SUCCESS_STAGING is enabled, False otherwise.
    """

    return bool ( os.environ.get ( 'SUCCESS_STAGING' ) )
