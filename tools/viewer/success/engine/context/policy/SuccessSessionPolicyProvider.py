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
from flask import session

# Success Libraries / Librerías Success
from success.engine.context.policy.SuccessPolicyProvider import SuccessPolicyProvider

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessSessionPolicyProvider ( SuccessPolicyProvider ) :
  """
  Session policy provider.

  Evaluates session-based policies by checking session state
  and required session keys.
  """


  def supports ( self, spec : dict, context : dict ) -> bool :
    """
    Check if this provider supports the session policy specification.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      bool: True if spec contains 'require_session' or 'session_keys_all'.
    """
    if not isinstance ( spec, dict ) :
      return False
    return bool ( spec.get ( "require_session" ) ) or bool ( spec.get ( "session_keys_all" ) )


  def evaluate ( self, spec : dict, context : dict ) -> dict :
    """
    Evaluate the session policy against the current session.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      dict: Allow result if session requirements are met, deny result otherwise.
    """
    extension = self._getExtension ( context, "session" )
    if extension is None and spec.get ( "require_session" ) :
      return self.deny ( 500, "Extensión de sesión no disponible.", "SESSION_EXTENSION_MISSING", "session" )

    if spec.get ( "require_session" ) and not self._isLoggedIn () :
      return self.deny ( 401, "Sesión no autenticada.", "SESSION_REQUIRED", "session" )

    requiredKeys = spec.get ( "session_keys_all", [] ) or []
    for key in requiredKeys :
      if key not in session :
        return self.deny ( 401, f"Falta clave de sesión requerida: {key}.", "SESSION_KEY_MISSING", "session" )

    return self.allow ()


  def _isLoggedIn ( self ) -> bool :
    """
    Check if the user is logged in based on session state.

    Returns:
      bool: True if the user is logged in.
    """
    value = session.get ( "loggedin", None )
    if isinstance ( value, bool ) :
      return value
    if isinstance ( value, str ) :
      return value.strip ().lower () in [ "true", "1", "yes", "on" ]
    return value is not None


  def _getExtension ( self, context : dict, key : str ) :
    """
    Get an extension from the context.

    Args:
      context: Evaluation context dictionary.
      key: Extension key to retrieve.

    Returns:
      The extension instance or None if not found.
    """
    if not isinstance ( context, dict ) :
      return None
    extensions = context.get ( "extensions", {} )
    if not isinstance ( extensions, dict ) :
      return None
    return extensions.get ( key )
