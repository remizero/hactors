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
from logging import Handler

# Success Libraries / Librerías Success
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv

# Preconditions / Precondiciones


class SuccessLoggerHandler () :
  """
  Base class for logging handlers in the Success framework.

  Provides a common structure for creating custom logging handlers
  with configurable formatting.

  Attributes:
    _format (str): The log message format.
    _handler (Handler): The logging handler instance.
  """

  _format  : str     = None
  _handler : Handler = None


  def __init__ ( self ) -> None :
    """
    Initialize the logging handler with the system format.

    Obtains the logging format from the system configuration
    or uses a default format.
    """
    self._format = SuccessSystemEnv.get ( "LOGGER_FORMAT", f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s - %(threadName)s" )


  def _getFormatter ( self ) -> str :
    """
    Get the configured logging format.

    Returns:
      str: The logging format string to use.
    """
    return SuccessSystemEnv.get ( "LOGGER_FORMAT", f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s - %(threadName)s" )


  def getDescriptor ( self ) -> Handler :
    """
    Get the logging handler.

    Returns:
      Handler: The logging handler instance.
    """
    return self._handler
