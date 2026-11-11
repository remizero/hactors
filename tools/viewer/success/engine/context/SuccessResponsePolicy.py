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
from success.common.base.SuccessClass import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessResponsePolicy ( SuccessClass ) :
  """
  Response policy handler.

  Defines default response settings and provides methods
  for resolving status codes, redirects, and render contexts.

  Attributes:
    _default_mimetype (str): Default MIME type for responses.
    _default_status (int): Default HTTP status code.
    _charset (str): Character set for responses.
    _content_type (str): Default content type header.
  """

  _default_mimetype : str = ''
  _default_status   : int = 0
  _charset          : str = ''
  _content_type     : str = ''


  def __init__ ( self ) -> None :
    """
    Initialize the response policy.

    Sets up default response definitions.
    """
    super ().__init__ ()
    self.definitions ()


  def definitions ( self ) -> None :
    """
    Set up default response definitions.

    Configures default MIME type, status code, charset, and content type.
    """
    self._default_mimetype = "application/json"
    self._default_status   = 200
    self._charset          = "utf-8"
    self._content_type     = "application/json; charset=utf-8"


  def resolve_status ( self, builtOutput : dict ) -> int :
    """
    Resolve the HTTP status code from built output.

    Args:
      builtOutput: The built output dictionary.

    Returns:
      int: Resolved status code or default if not specified.
    """
    if isinstance ( builtOutput, dict ) :
      status = builtOutput.get ( "status" )
      if isinstance ( status, int ) :
        return status

    return self._default_status


  def resolve_redirect_context ( self, builtOutput : dict ) -> dict :
    """
    Resolve the context for redirect operations.

    Args:
      builtOutput: The built output dictionary.

    Returns:
      dict: Context dictionary for redirect.
    """
    if not isinstance ( builtOutput, dict ) :
      return {}

    redirectSpec = builtOutput.get ( "redirect", {} ) or {}
    if isinstance ( redirectSpec.get ( "context" ), dict ) :
      return redirectSpec.get ( "context" )

    if isinstance ( builtOutput.get ( "data" ), dict ) :
      return builtOutput.get ( "data" )

    return builtOutput


  def resolve_render_context ( self, builtOutput : dict ) -> dict :
    """
    Resolve the context for render operations.

    Args:
      builtOutput: The built output dictionary.

    Returns:
      dict: Context dictionary for render.
    """
    if not isinstance ( builtOutput, dict ) :
      return {}

    renderSpec = builtOutput.get ( "render", {} ) or {}
    if isinstance ( renderSpec.get ( "context" ), dict ) :
      return renderSpec.get ( "context", {} )

    return builtOutput


  def response_kwargs ( self, builtOutput : dict = None ) -> dict :
    """
    Get response keyword arguments.

    Args:
      builtOutput: Optional built output dictionary.

    Returns:
      dict: Dictionary with response kwargs (mimetype, content_type, etc.).
    """
    defaults = {
      "mimetype"     : self._default_mimetype,
      "content_type" : self._content_type
    }

    if not isinstance ( builtOutput, dict ) :
      return defaults

    responseMeta = builtOutput.get ( "response", {} ) or {}
    if not isinstance ( responseMeta, dict ) :
      return defaults

    kwargs = responseMeta.get ( "kwargs", {} ) or {}
    if not isinstance ( kwargs, dict ) :
      return defaults

    resolved = defaults.copy ()
    resolved.update ( kwargs )
    return resolved
