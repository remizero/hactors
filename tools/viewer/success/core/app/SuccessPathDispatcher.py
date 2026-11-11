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
from flask        import Flask
from threading    import Lock
from typing       import Any
from typing       import Callable
from wsgiref.util import shift_path_info

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessPathDispatcher ( SuccessClass ) :
  """
  Path-based application dispatcher for multiApp mode.

  Routes requests to different Flask applications based on
  the URL path prefix.

  Attributes:
    _default_app (Flask): Default application for unmatched paths.
    _mounts (dict[str, Flask]): Dictionary of mounted applications.
    _lock (Lock): Thread lock for instance caching.
    _instances (dict[str, Flask]): Cached application instances.
  """


  def __init__ ( self, default_app : Flask, mounts : dict [ str, Flask ] ) -> None :
    """
    Initialize the path dispatcher.

    Args:
      default_app: Default Flask application for unmatched paths.
      mounts: Dictionary mapping path prefixes to Flask applications.
    """
    super ().__init__ ()
    self._default_app = default_app
    self._mounts      = mounts or {}
    self._lock        = Lock ()
    self._instances   = {}
    self._logger.log ( "Cargando el sub-sistema SuccessPathDispatcher.", "INFO" )


  def get_application ( self, prefix : str | None ) -> Flask | None :
    if prefix is None :
      return None

    with self._lock :
      app = self._instances.get ( prefix )
      if app is None :
        app = self._mounts.get ( f"/{prefix}" )
        if app is not None :
          self._instances [ prefix ] = app
      return app


  def __call__ ( self, environ : dict, start_response : Callable ) -> Any :
    app = self.get_application ( self._peek_path_info ( environ ) )

    if app is not None :
      shift_path_info ( environ )

    else :
      app = self._default_app

    return app ( environ, start_response )


  @staticmethod
  def _peek_path_info ( environ : dict [ str, str ] | dict ) -> str | None :
    """
    Return the first segment of PATH_INFO without modifying the environment.

    Args:
      environ: WSGI environment dictionary.

    Returns:
      str | None: First path segment or None if path is empty.
    """
    path = environ.get ( "PATH_INFO", "" ).lstrip ( "/" )
    return path.split ( "/", 1 ) [ 0 ] if path else None
