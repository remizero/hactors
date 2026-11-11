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
from os                          import makedirs
from logging                     import Formatter
from logging.handlers            import RotatingFileHandler
from logging.handlers            import TimedRotatingFileHandler
from os.path                     import dirname
from pythonjsonlogger.jsonlogger import JsonFormatter

# Success Libraries / Librerías Success
from success.common.base.SuccessLoggerHandler     import SuccessLoggerHandler
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv

# Preconditions / Precondiciones


class SuccessFileHandler ( SuccessLoggerHandler ) :
  """
  Handler for writing logs to files with time-based or size-based rotation.

  This handler implements writing log records to files, with support for
  automatic rotation based on time (daily, hourly, etc.) or file size.
  It uses ``TimedRotatingFileHandler`` as the primary option and
  ``RotatingFileHandler`` as a fallback in case of error.

  Attributes:
    __backupCount (int): Number of log files to keep.
    __fileName (str): Name and path of the log file.
    __maxBytes (int): Maximum file size before rotation.
    __when (str): When to perform file rotation.
    __interval (int): Number of times to perform file rotation.

  Example:
    >>> handler = SuccessFileHandler()
    >>> logger.addHandler(handler)
  """

  # Number of error log files to keep.
  __backupCount : int = 7
  # Error log file name and path.
  __fileName    : str = "./log"
  # Maximum size of the error log file.
  __maxBytes    : int = 500000
  # Time when the error log file rotation should be performed.
  __when        : str = None
  # Number of times to rotate the error log file.
  __interval    : int = 1


  def __init__ ( self ) -> None :
    """
    Initialize the file handler with configuration from environment variables.

    Configures the handler using the following environment variables:
      - LOGGER_BACKUP_COUNT: Number of backups to keep
      - LOGGER_DIR: Directory where logs are stored
      - LOGGER_MAX_BYTES: Maximum file size before rotation
      - LOGGER_ROTATE_WHEN: When to rotate (e.g., 'midnight', 'H', 'D')
      - LOGGER_ROTATE_INTERVAL: Rotation interval
      - LOGGER_ENCODING: File encoding (default: 'utf-8')
      - LOGGER_FORMATER: Log format ('json' or standard)

    Note:
      Attempts to create a TimedRotatingFileHandler first. If it fails,
      uses RotatingFileHandler as an alternative.
    """
    super ().__init__ ()
    self.__backupCount = SuccessSystemEnv.toInt ( 'LOGGER_BACKUP_COUNT' )
    self.__fileName    = SuccessSystemEnv.get   ( 'LOGGER_DIR' )
    self.__maxBytes    = SuccessSystemEnv.toInt ( 'LOGGER_MAX_BYTES' )
    self.__when        = SuccessSystemEnv.get   ( 'LOGGER_ROTATE_WHEN', 'midnight' )
    self.__interval    = SuccessSystemEnv.toInt ( 'LOGGER_ROTATE_INTERVAL' )
    fileEncoding       = SuccessSystemEnv.get   ( 'LOGGER_ENCODING', 'utf-8' )

    self.__ensureLogPath ( fileEncoding )

    try :
      self._handler = TimedRotatingFileHandler (
        self.__fileName,
        when        = self.__when,
        interval    = self.__interval,
        backupCount = self.__backupCount,
        encoding    = fileEncoding
      )

    except Exception as e :
      self._handler = RotatingFileHandler (
        self.__fileName,
        maxBytes    = self.__maxBytes,
        backupCount = self.__backupCount,
        encoding    = fileEncoding
      )

    self._getFormatter ()


  def _getFormatter ( self ) -> None :
    """
    Configure the handler formatter based on environment configuration.

    If the LOGGER_FORMATER environment variable is set to 'json', uses
    ``JsonFormatter`` for JSON format output. Otherwise, uses the standard
    logging ``Formatter``.
    """
    formater = None
    if ( SuccessSystemEnv.get ( 'LOGGER_FORMATER' ) == 'json' ) :
      formater = JsonFormatter ( self._format )

    else :
      formater = Formatter ( self._format )

    self._handler.setFormatter ( formater )


  def __ensureLogPath ( self, encoding : str ) -> None :
    """
    Ensure the log directory and file exist to avoid startup crashes.
    """
    if ( self.__fileName is None or self.__fileName.strip () == '' ) :
      self.__fileName = './log/error_success.log'

    directory = dirname ( self.__fileName )
    if ( directory != '' ) :
      makedirs ( directory, exist_ok = True )

    with open ( self.__fileName, 'a', encoding = encoding ) :
      pass
