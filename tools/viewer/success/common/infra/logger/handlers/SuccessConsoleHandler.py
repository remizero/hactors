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
from logging import Formatter
from logging import StreamHandler

# Success Libraries / Librerías Success
from success.common.base.SuccessLoggerHandler import SuccessLoggerHandler

# Preconditions / Precondiciones


class SuccessConsoleHandler ( SuccessLoggerHandler ) :
  """
  Handler for writing logs to the standard console.

  This handler implements writing log records to the standard output
  (console/stream), using ``StreamHandler`` from the standard logging
  library. It is useful for development, debugging, or CLI applications.

  Example:
    >>> handler = SuccessConsoleHandler()
    >>> logger.addHandler(handler)
  """


  def __init__ ( self ) -> None :
    """
    Initialize the console handler configuring the formatter.

    Creates a ``StreamHandler`` instance and configures the appropriate
    formatter for console output.
    """
    super ().__init__ ()
    self._handler = StreamHandler ()
    self._getFormatter ()


  def _getFormatter ( self ) -> None :
    """
    Configure the formatter for console output.

    Gets the base format from the parent class and applies it to the handler
    using the standard logging ``Formatter``.
    """
    self._format = super ()._getFormatter ()
    self._handler.setFormatter ( Formatter ( self._format ) )
