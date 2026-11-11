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
from flask               import Flask
from flask               import url_for
from threading           import Lock
from typing              import Any
from typing              import Callable
from typing              import Optional
from werkzeug.exceptions import NotFound

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessSubdomainDispatcher ( SuccessClass ) :
  """
  Subdomain-based application dispatcher for multiApp mode.

  Routes requests to different Flask applications based on
  the subdomain in the HTTP host header.

  Attributes:
    _domain (str): Base domain for subdomain matching.
    _mounts (dict[str, Flask]): Dictionary of mounted applications.
    _lock (Lock): Thread lock for instance caching.
    _instances (dict[str, Flask]): Cached application instances.
  """


  def __init__ ( self, domain : str, mounts : dict [ str, Flask ] ) -> None :
    """
    Initialize the subdomain dispatcher.

    Args:
      domain: Base domain for subdomain matching.
      mounts: Dictionary mapping subdomains to Flask applications.
    """
    super ().__init__ ()
    self._domain    = ( domain or "" ).strip ().lower ()
    self._mounts    = mounts or {}
    self._lock      = Lock ()
    self._instances = {}


  def get_application ( self, host : str ) -> Optional [ Flask ] :
    host = ( host or "" ).split ( ':' ) [ 0 ].strip ().lower ()
    if not self._domain or not host.endswith ( self._domain ) :
      return None

    subdomain = host [ : -len ( self._domain ) ].rstrip ( '.' )
    with self._lock :
      app = self._instances.get ( subdomain )
      if app is None :
        app = self._mounts.get ( subdomain ) or self._mounts.get ( f"/{subdomain}" )
        if app is not None :
          self._instances [ subdomain ] = app
      return app


  def __call__ ( self, environ : dict, start_response : Callable ) -> Any :
    app = self.get_application ( environ.get ( 'HTTP_HOST', '' ) )
    if app is None :
      return NotFound () ( environ, start_response )

    return app ( environ, start_response )
