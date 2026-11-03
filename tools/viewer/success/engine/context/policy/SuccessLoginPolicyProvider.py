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


class SuccessLoginPolicyProvider ( SuccessPolicyProvider ) :
  """
  Login policy provider.

  Evaluates login/authentication policies by checking if the user
  is logged in via session state.
  """


  def supports ( self, spec : dict, context : dict ) -> bool :
    """
    Check if this provider supports the login policy specification.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      bool: True if spec contains 'require_login'.
    """
    if not isinstance ( spec, dict ) :
      return False
    return bool ( spec.get ( "require_login" ) )


  def evaluate ( self, spec : dict, context : dict ) -> dict :
    """
    Evaluate the login policy against the current session.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      dict: Allow result if logged in, deny result otherwise.
    """
    extension = self._getExtension ( context, "login" )
    if extension is None :
      return self.deny ( 500, "Extensión Login no disponible.", "LOGIN_EXTENSION_MISSING", "login" )

    logged = session.get ( "loggedin", None )
    if logged is True :
      return self.allow ()
    if isinstance ( logged, str ) and logged.strip ().lower () in [ "true", "1", "yes", "on" ] :
      return self.allow ()

    return self.deny ( 401, "Login requerido.", "LOGIN_REQUIRED", "login" )


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
