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
from flask import Flask

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass

# Preconditions / Precondiciones


class SuccessExtension ( SuccessClass ) :
  """
  Base class for extensions in the Success framework.

  Provides a common structure for registering and configuring Flask
  extensions within the Success ecosystem.

  Attributes:
    _extension: The extension instance to be registered.
    _app (Flask): The Flask application instance.
  """

  _extension         = None
  _app       : Flask = None


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the extension with the provided Flask application.

    Args:
      app (Flask): The Flask application instance where the extension will be registered.
    """
    super ().__init__ ()
    self._app = app


  def config ( self ) -> None :
    """
    Configure the extension.

    This method must be implemented by subclasses to provide
    extension-specific configuration.
    """
    pass


  def getExtension ( self ) :
    """
    Get the extension instance.

    Returns:
      The extension instance.
    """
    return self._extension


  def register ( self ) -> None :
    """
    Register the extension in the Flask application.

    Uses the init_app method of the extension if available,
    otherwise raises an exception.

    Raises:
      RuntimeError: If the extension does not properly define 'self._extension'
        or does not implement 'init_app'.
    """
    if self._extension and hasattr ( self._extension, "init_app" ) :
      self._extension.init_app ( self._app )

    else :
      raise RuntimeError ( f"La extensión {self.__class__.__name__} no define correctamente 'self._extension' o no implementa 'init_app'" )


  def policyDefaults ( self ) -> dict :
    """
    Provide default values for extension policies.

    Returns:
      dict: Empty dictionary that should be overridden by subclasses to
        provide specific default values.
    """
    return {}


  def userConfig ( self, **kwargs ) -> None :
    """
    Add custom configuration to the Flask application.

    Args:
      **kwargs: Key-value pairs of configuration to add.
    """
    self._app.config.update ( kwargs )
