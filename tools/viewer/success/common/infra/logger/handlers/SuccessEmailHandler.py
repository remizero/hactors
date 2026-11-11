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

# Success Libraries / Librerías Success
from success.common.base.SuccessLoggerHandler        import SuccessLoggerHandler
from success.common.infra.logger.SuccessLoggerMailer import SuccessLoggerMailer

# Preconditions / Precondiciones


class SuccessEmailHandler ( SuccessLoggerHandler ) :
  """
  Handler for sending logs via email.

  This handler implements sending log records via email using the internal
  ``SuccessLoggerMailer``. It is useful for critical notifications or alerts
  that require immediate attention.

  Example:
    >>> handler = SuccessEmailHandler()
    >>> logger.addHandler(handler)
  """


  def __init__ ( self ) -> None :
    """
    Initialize the email handler configuring the formatter.

    Creates a ``SuccessLoggerMailer`` instance and configures the appropriate
    formatter for email messages.
    """
    super ().__init__ ()
    self._handler = SuccessLoggerMailer ()
    self._getFormatter ()


  def _getFormatter ( self ) -> None :
    """
    Configure the formatter for email messages.

    Gets the base format from the parent class and applies it to the handler
    using the standard logging ``Formatter``.
    """
    self._format = super ()._getFormatter ()
    self._handler.setFormatter ( Formatter ( self._format ) )
