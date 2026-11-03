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
from flask         import Flask
from flask         import session
from flask_redis   import FlaskRedis
from flask_session import Session

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessExtension            import SuccessExtension
from success.core.SuccessContext                     import SuccessContext
from success.engine.context.SuccessExtensionResolver import SuccessExtensionResolver

# Preconditions / Precondiciones


class SuccessSessionExtension ( SuccessExtension ) :
  """
  Session extension for the Success framework.

  Integrates Flask-Session for server-side session management
  with optional Redis backend support.
  """


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the Session extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    self._extension = Session ()


  def config ( self ) -> None :
    """
    Configure the Session extension with Redis backend.

    Sets up Redis connection for session storage if available.
    """
    resolver  = SuccessExtensionResolver ( self._app )
    redis_ext = resolver.get ( "redis" )
    if redis_ext :
      self._app.config [ "SESSION_REDIS" ] = redis_ext


  def policyDefaults ( self ) -> dict :
    """
    Get default policy settings for Session.

    Returns:
      dict: Dictionary with default Session policy settings.
    """
    return {
      "require_session"   : False,
      "session_keys_all"  : []
    }
