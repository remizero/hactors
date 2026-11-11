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
from datetime import datetime
from logging  import LogRecord
import os
import traceback

# Success Libraries / Librerías Success

# Preconditions / Precondiciones


class SuccessParsers () :
  """
  Parser utilities for processing log records and exception information.

  Provides static methods for extracting and formatting exception
  and log record data for template rendering.
  """

  @staticmethod
  def exc_info ( exc_info ) -> tuple [ dict, str ] :
    """
    Process exc_info content to extract useful information.

    Returns a dict with data for the template and the template name.

    Args:
      exc_info: Exception information (tuple, BaseException, or None).

    Returns:
      tuple[dict, str]: Tuple containing context dict and template name.
    """
    template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_ERROR' )  # default
    context = {}

    if exc_info is None :
      return context, template

    if isinstance ( exc_info, tuple ) and len ( exc_info ) == 3 :
      exc_type, exc_value, exc_tb = exc_info
      context.update (
        {
          'exception_type': exc_type.__name__,
          'exception_message': str ( exc_value ),
          'traceback': ''.join ( traceback.format_exception ( exc_type, exc_value, exc_tb ) )
        }
      )
      template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_EXCEPTION' )

    elif isinstance ( exc_info, BaseException ) :
      context.update (
        {
          'exception_type': type ( exc_info ).__name__,
          'exception_message': str ( exc_info ),
          'traceback': ''.join ( traceback.format_exception ( type ( exc_info ), exc_info, exc_info.__traceback__ ) )
        }
      )
      template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_EXCEPTION' )

    else :
      context [ 'exception_raw' ] = str ( exc_info )

    return context, template

  @staticmethod
  def record ( record : LogRecord ) -> tuple [ dict, str ] :
    """
    Process a complete LogRecord to prepare context for an HTML template.

    Args:
      record: LogRecord object to process.

    Returns:
      tuple[dict, str]: Tuple containing context dict and template name.
    """
    template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_ERROR' )  # default

    context = {
      'levelname' : record.levelname,
      'message' : record.getMessage (),
      'pathname' : record.pathname,
      'lineno' : record.lineno,
      'module' : record.module,
      'funcName' : record.funcName,
      'asctime' : datetime.fromtimestamp ( record.created ).isoformat (),
      'logger_name' : record.name
    }

    if record.exc_info :
      exc_type, exc_value, exc_tb = record.exc_info
      context.update (
        {
          'exception_type' : exc_type.__name__,
          'exception_message' : str ( exc_value ),
          'traceback' : ''.join ( traceback.format_exception ( exc_type, exc_value, exc_tb ) )
        }
      )
      template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_EXCEPTION' )

    return context, template
