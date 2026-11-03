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

# Preconditions / Precondiciones


class SuccessException ( Exception ) :
  """
  Base class for custom exceptions in the Success framework.

  Provides a common structure for handling exceptions with additional
  information such as code, message, details, and arguments.

  Purpose:
  ----------
  SuccessException is the base for all exceptions in the framework,
  providing:
  - Storage of the original exception (e)
  - Custom error code (code)
  - Descriptive message (message)
  - Additional details (details)
  - Format arguments (fargs)

  Usage:
  ------
  # Create basic exception
  raise SuccessException(message="Error processing request")

  # Create exception with code and details
  raise SuccessException(
    code=404,
    message="Resource not found",
    details={"resource": "user", "id": 123}
  )

  # Wrap another exception
  try:
    risky_operation()
  except Exception as e:
    raise SuccessException(e=e, message="Operation failed")

  Attributes:
    e (Exception): Original wrapped exception (optional).
    code (int): Custom error code (optional).
    message (str): Descriptive error message (optional).
    details (dict): Additional error details (optional).
    fargs (tuple): Arguments for formatting the message (optional).

  Note:
    - All attributes are optional
    - __str__ displays only non-None attributes
  """

  e       : Exception = None
  code    : int       = None
  message : str       = None
  details : dict      = None
  fargs   : tuple     = None


  def __init__ ( self, e = None, code = None, message = None, details = None, fargs = None ) -> None :
    """
    Initialize the SuccessException.

    Args:
      e (Exception): Original exception to wrap (optional).
      code (int): Custom error code (optional).
      message (str): Descriptive error message (optional).
      details (dict): Dictionary with additional details (optional).
      fargs (tuple): Arguments for formatting the message (optional).
    """
    self.e       = e
    self.code    = code
    self.message = message
    self.details = details
    self.fargs   = fargs


  def getE ( self ) -> Exception :
    """
    Get the original wrapped exception.

    Returns:
      Exception: The original exception or None if not provided.
    """
    return self.e


  def getCode ( self ) -> int :
    """
    Get the custom error code.

    Returns:
      int: The error code or None if not provided.
    """
    return int ( self.code )


  def getMessage ( self ) -> str :
    """
    Get the descriptive error message.

    Returns:
      str: The error message or None if not provided.
    """
    return self.message


  def getDetails ( self ) -> dict :
    """
    Get additional error details.

    Returns:
      dict: The error details or None if not provided.
    """
    return self.details


  def __str__ ( self ) -> str :
    """
    Return string representation of the exception.

    Returns:
      str: String with non-None attributes in 'key = value' format.
    """
    s_items = []
    if self.e is not  None:
      s_items.append ( 'e = {}'.format ( self.e ) )

    if self.code is not  None:
      s_items.append ( 'code = {}'.format ( self.code ) )

    if self.message is not  None:
      s_items.append ( 'message = {}'.format ( self.message ) )

    if self.details is not  None:
      s_items.append ( 'details = {}'.format ( self.details ) )

    if self.fargs is not  None:
      s_items.append ( 'fargs = {}'.format ( self.fargs ) )

    return ', '.join ( s_items )
