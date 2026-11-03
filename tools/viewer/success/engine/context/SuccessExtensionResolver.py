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
from flask import current_app

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass

# Preconditions / Precondiciones


class SuccessExtensionResolver ( SuccessClass ) :
  """
  Runtime extension resolver from current_app.extensions.

  - Does not depend on SuccessContext or SuccessBuildContext.
  - Centralizes capability to Flask internal key mapping.
  - Allows library changes in a single location.
  """

  # capability -> possible keys in current_app.extensions (priority order)
  _MAP = {
    "cors"      : [ "cors", "flask-cors", "flask_cors" ],
    "jwt"       : [ "jwt", "flask-jwt-extended", "flask_jwt_extended" ],
    "session"   : [ "session", "flask-session", "flask_session" ],
    "security"  : [ "security", "flask-security", "flask_security" ],
    "login"     : [ "login_manager", "login", "flask-login", "flask_login" ],
    "acl"       : [ "principal", "acl", "flask-principal", "flask_principal" ],
    "database"  : [ "sqlalchemy", "flask-sqlalchemy", "flask_sqlalchemy" ],
    "cache"     : [ "cache", "flask-caching", "flask_caching" ],
    "migrate"   : [ "migrate", "flask-migrate", "flask_migrate" ],
    "mail"      : [ "mail", "flask-mail", "flask_mail" ],
    "limiter"   : [ "limiter", "flask-limiter", "flask_limiter" ],
    "babel"     : [ "babel", "flask-babel", "flask_babel" ],
    "admin"     : [ "admin", "flask-admin", "flask_admin" ],
    "redis"     : [ "redis", "flask-redis", "flask_redis" ],
    "scheduler" : [ "apscheduler", "flask-apscheduler", "flask_apscheduler" ],
    "marshmallow": [ "ma", "marshmallow", "flask-marshmallow", "flask_marshmallow" ]
  }


  def __init__ ( self, app = None ) -> None :
    """
    Initialize the extension resolver.

    Args:
      app: Optional Flask application instance. If not provided,
        uses current_app from Flask context.
    """
    super ().__init__ ()
    self._app = app


  def _getApp ( self ) :
    """
    Get the Flask application instance.

    Returns:
      The stored app or current_app from Flask context.
    """
    return self._app or current_app


  def get ( self, capability : str, default = None ) :
    """
    Get an extension by capability ('cors', 'jwt', etc.).

    Args:
      capability: Capability name to look up.
      default: Default value if extension not found.

    Returns:
      The extension instance or default if not found.
    """
    app = self._getApp ()
    if app is None :
      return default

    extensions = getattr ( app, "extensions", {} ) or {}
    keys = self._MAP.get ( str ( capability or "" ).strip ().lower (), [] )

    # 1) Direct lookup by expected keys
    for key in keys :
      if key in extensions :
        return extensions.get ( key )

    # 2) Flexible fallback by partial match
    normalized = [ k.replace ( "-", "_" ) for k in keys ]
    for extKey, extValue in extensions.items () :
      probe = str ( extKey ).strip ().lower ().replace ( "-", "_" )
      if probe in normalized :
        return extValue

    return default


  def getMany ( self, capabilities : list [ str ] ) -> dict :
    """
    Return dict { capability: extension|None }.

    Args:
      capabilities: List of capability names to look up.

    Returns:
      dict: Dictionary mapping capabilities to their extensions.
    """
    result = {}
    for cap in capabilities or [] :
      result [ cap ] = self.get ( cap )
    return result


  def buildPolicyExtensions ( self ) -> dict :
    """
    Convenience method for SuccessPreInputPolicy.

    Returns:
      dict: Dictionary with policy-related extensions.
    """
    return self.getMany ( [ "cors", "jwt", "session", "security", "login", "acl" ] )
