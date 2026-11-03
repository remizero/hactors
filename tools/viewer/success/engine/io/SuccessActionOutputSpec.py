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
from success.common.types.SuccessProtocol import SuccessProtocol

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessActionOutputSpec () :
  """
  Output specification container for actions.

  Centralizes protocol and rendering/redirect metadata so actions can
  pass a single object to output resolution logic.
  """

  _protocol          : SuccessProtocol = None
  _template          : str             = None
  _redirect          : str             = None
  _redirect_to       : str             = None
  _fallback_redirect : str             = None


  def __init__ (
      self,
      _protocol          : SuccessProtocol = None,
      _template          : str             = None,
      _redirect          : str             = None,
      _redirect_to       : str             = None,
      _fallback_redirect : str             = None
    ) -> None :
    """
    Initialize output specification metadata.

    Args:
      _protocol: Action protocol (VIEW/RESTFUL).
      _template: Template path/name for render intent.
      _redirect: Redirect endpoint alias (optional).
      _redirect_to: Redirect target endpoint/url (optional).
      _fallback_redirect: Fallback redirect target (optional).
    """
    self._protocol          = _protocol
    self._template          = _template
    self._redirect          = _redirect
    self._redirect_to       = _redirect_to
    self._fallback_redirect = _fallback_redirect


  @property
  def protocol ( self ) -> SuccessProtocol :
    """
    Get action protocol.

    Returns:
      SuccessProtocol: Protocol value.
    """
    return self._protocol


  @protocol.setter
  def protocol ( self, value : SuccessProtocol ) -> None :
    """
    Set action protocol.

    Args:
      value: Protocol value.
    """
    self._protocol = value


  @property
  def template ( self ) -> str :
    """
    Get render template.

    Returns:
      str: Template value.
    """
    return self._template


  @template.setter
  def template ( self, value : str ) -> None :
    """
    Set render template.

    Args:
      value: Template value.
    """
    self._template = value


  @property
  def redirect ( self ) -> str :
    """
    Get redirect alias.

    Returns:
      str: Redirect alias.
    """
    return self._redirect


  @redirect.setter
  def redirect ( self, value : str ) -> None :
    """
    Set redirect alias.

    Args:
      value: Redirect alias.
    """
    self._redirect = value


  @property
  def redirect_to ( self ) -> str :
    """
    Get redirect target.

    Returns:
      str: Redirect target.
    """
    return self._redirect_to


  @redirect_to.setter
  def redirect_to ( self, value : str ) -> None :
    """
    Set redirect target.

    Args:
      value: Redirect target.
    """
    self._redirect_to = value


  @property
  def fallback_redirect ( self ) -> str :
    """
    Get fallback redirect target.

    Returns:
      str: Fallback redirect target.
    """
    return self._fallback_redirect


  @fallback_redirect.setter
  def fallback_redirect ( self, value : str ) -> None :
    """
    Set fallback redirect target.

    Args:
      value: Fallback redirect target.
    """
    self._fallback_redirect = value


  def lazyInit (
      self,
      _protocol          : SuccessProtocol = None,
      _template          : str             = None,
      _redirect          : str             = None,
      _redirect_to       : str             = None,
      _fallback_redirect : str             = None
    ) -> None :
    """
    Initialize output specification metadata.

    Args:
      _protocol: Action protocol (VIEW/RESTFUL).
      _template: Template path/name for render intent.
      _redirect: Redirect endpoint alias (optional).
      _redirect_to: Redirect target endpoint/url (optional).
      _fallback_redirect: Fallback redirect target (optional).
    """
    self._protocol          = _protocol
    self._template          = _template
    self._redirect          = _redirect
    self._redirect_to       = _redirect_to
    self._fallback_redirect = _fallback_redirect
