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
from contextvars import ContextVar
from typing      import Optional
import os

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class RequestContext () :
  """
  Request context manager using context variables.

  Provides thread-safe storage for request-specific data such as
  request ID and application ID using Python's contextvars.
  """

  __appId     : ContextVar [ Optional [ str ] ] = ContextVar ( "app_id", default = None )
  __requestId : ContextVar [ Optional [ str ] ] = ContextVar ( "request_id", default = None )


  @classmethod
  def clear ( cls ) -> None :
    """
    Clear all context variables.

    Resets both app_id and request_id to None.
    """
    cls.__appId.set ( None )
    cls.__requestId.set ( None )


  @staticmethod
  def _detectAppId () -> str :
    """
    Dynamically detect the application name from the file path.

    Returns:
      str: Detected application name or 'unknown' if detection fails.
    """
    # Detecta dinámicamente el nombre de la apps a partir de la ruta
    try :
      return os.path.basename ( os.path.dirname ( os.path.abspath ( __file__ ) ) )

    except Exception :
      return "unknown"


  @classmethod
  def getAppId ( cls ) -> Optional [ str ] :
    """
    Get the current application ID from context.

    Returns:
      Optional[str]: The application ID or None if not set.
    """
    return cls.__appId.get ()


  @classmethod
  def getRequestId ( cls ) -> Optional [ str ] :
    """
    Get the current request ID from context.

    Returns:
      Optional[str]: The request ID or None if not set.
    """
    return cls.__requestId.get ()


  @classmethod
  def setAppId ( cls, app_id : Optional [ str ] = None ) -> None :
    """
    Set the application ID in context.

    Args:
      app_id: Application ID to set. If None, auto-detects from path.
    """
    if app_id :
      cls.__appId.set ( app_id )

    else :
      # Fallback automático si no se pasa app_id manualmente
      dynamicAppId = cls._detectAppId ()
      cls.__appId.set ( dynamicAppId )


  @classmethod
  def setRequestId ( cls, request_id : str ) -> None :
    """
    Set the request ID in context.

    Args:
      request_id: Unique request identifier to set.
    """
    cls.__requestId.set ( request_id )
