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


class SuccessCorsPolicyProvider ( SuccessPolicyProvider ) :
  """
  CORS (Cross-Origin Resource Sharing) policy provider.

  Evaluates CORS policies by checking if the request origin
  is allowed according to the policy specification.
  """


  def supports ( self, spec : dict, context : dict ) -> bool :
    """
    Check if this provider supports the CORS policy specification.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      bool: True if spec contains 'require_cors' or 'allowed_origins'.
    """
    if not isinstance ( spec, dict ) :
      return False
    return bool ( spec.get ( "require_cors" ) ) or bool ( spec.get ( "allowed_origins" ) )


  def evaluate ( self, spec : dict, context : dict ) -> dict :
    """
    Evaluate the CORS policy against the current request.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      dict: Allow result if origin is permitted, deny result otherwise.
    """
    origin = request.headers.get ( "Origin" )
    if not origin :
      return self.allow ()

    allowedOrigins = spec.get ( "allowed_origins" )
    if not allowedOrigins :
      appConfig = context.get ( "app_config", {} ) if isinstance ( context, dict ) else {}
      allowedOrigins = appConfig.get ( "CORS_ORIGINS", [] )

    normalized = self._toList ( allowedOrigins )
    if not normalized :
      return self.allow ()

    if "*" in normalized or origin in normalized :
      return self.allow ()

    return self.deny ( 403, "Origen no permitido por política CORS.", "CORS_ORIGIN_FORBIDDEN", "cors" )


  def _toList ( self, value ) -> list :
    """
    Convert a value to a list of strings.

    Args:
      value: Value to convert (list, tuple, set, string, or None).

    Returns:
      list: List of string values.
    """
    if value is None :
      return []
    if isinstance ( value, list ) :
      return [ str ( item ) for item in value ]
    if isinstance ( value, tuple ) :
      return [ str ( item ) for item in value ]
    if isinstance ( value, set ) :
      return [ str ( item ) for item in value ]
    if isinstance ( value, str ) :
      value = value.strip ()
      if not value :
        return []
      if value.startswith ( "[" ) and value.endswith ( "]" ) :
        raw = value [ 1 : -1 ]
        return [ item.strip ().strip ( "'" ).strip ( '"' ) for item in raw.split ( "," ) if item.strip () ]
      return [ value ]
    return [ str ( value ) ]
