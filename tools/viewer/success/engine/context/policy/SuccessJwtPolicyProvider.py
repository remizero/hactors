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
from flask import request

# Success Libraries / Librerías Success
from success.engine.context.policy.SuccessPolicyProvider import SuccessPolicyProvider

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
try :
  from flask_jwt_extended import verify_jwt_in_request
except Exception :
  verify_jwt_in_request = None


class SuccessJwtPolicyProvider ( SuccessPolicyProvider ) :
  """
  JWT (JSON Web Token) policy provider.

  Evaluates JWT authentication policies by verifying the presence
  and validity of JWT tokens in the request.
  """


  def supports ( self, spec : dict, context : dict ) -> bool :
    """
    Check if this provider supports the JWT policy specification.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      bool: True if spec contains 'require_jwt'.
    """
    if not isinstance ( spec, dict ) :
      return False
    return bool ( spec.get ( "require_jwt" ) )


  def evaluate ( self, spec : dict, context : dict ) -> dict :
    """
    Evaluate the JWT policy against the current request.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      dict: Allow result if JWT is valid, deny result otherwise.
    """
    extension = self._getExtension ( context, "jwt" )
    if extension is None :
      return self.deny ( 500, "Extensión JWT no disponible.", "JWT_EXTENSION_MISSING", "jwt" )

    if verify_jwt_in_request is None :
      # Fallback: check for token presence.
      if not self._hasTokenInRequest () :
        return self.deny ( 401, "JWT requerido.", "JWT_REQUIRED", "jwt" )
      return self.allow ()

    try :
      verify_jwt_in_request ()
      return self.allow ()

    except Exception as e :
      return self.deny ( 401, "JWT inválido o ausente.", "JWT_INVALID_OR_MISSING", "jwt", str ( e ) )


  def _hasTokenInRequest ( self ) -> bool :
    """
    Check if a JWT token is present in the request.

    Returns:
      bool: True if token is found in Authorization header or cookie.
    """
    authHeader = request.headers.get ( "Authorization", "" )
    if isinstance ( authHeader, str ) and authHeader.strip ().lower ().startswith ( "bearer " ) :
      return True

    accessCookie = request.cookies.get ( "access_token_cookie" )
    if accessCookie :
      return True

    return False


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
