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
from flask import request
import uuid

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessClass      import SuccessClass
from success.core.SuccessContext           import CURRENT_APP
from success.engine.context.RequestContext import RequestContext

# Preconditions / Precondiciones


class RequestContextMiddleware ( SuccessClass ) :
  """
  Middleware for managing request context in Flask applications.

  Handles the lifecycle of request context by setting up unique
  request identifiers and app identifiers before each request,
  and cleaning up the context after each request completes.

  Attributes:
    __app (Flask): The Flask application instance.
    __appName (str): The name of the application.
  """

  __app : Flask = None


  def __init__ ( self, app : Flask, appName : str | None = None ) :
    """
    Initialize the request context middleware.

    Args:
      app: Flask application instance to attach middleware to.
      appName: Optional application name. If not provided, uses
        the app's name attribute.
    """
    super ().__init__ ()
    self.__app     = app
    self.__appName = appName or getattr ( app, "name", None )
    self._registerHooks ()


  def _registerHooks ( self ) :
    """
    Register before_request and teardown_request hooks.

    Sets up Flask hooks to manage request context lifecycle:
    - before_request: Generates unique request ID and sets app ID
    - teardown_request: Clears request context to prevent leaks
    """
    @self.__app.before_request
    def _set_request_context () :
      # Generar un UUID único para cada request
      RequestContext.setRequestId ( str ( uuid.uuid4 () ) )
      # Asignar dinámicamente el app_id (por ruta actual)
      # RequestContext.setAppId ()
      RequestContext.setAppId ( self.__appName )
      CURRENT_APP.set ( self.__appName )

    @self.__app.teardown_request
    def _clear_request_context ( exception = None ) :
      # Limpiar el contexto para evitar fugas entre threads
      RequestContext.clear ()
      CURRENT_APP.set ( None )
