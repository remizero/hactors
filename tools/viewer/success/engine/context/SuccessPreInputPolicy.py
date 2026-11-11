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
from success.common.base.SuccessClass                               import SuccessClass
from success.core.SuccessBuildContext                               import SuccessBuildContext
from success.core.SuccessContext                                    import SuccessContext
from success.engine.context.SuccessExtensionResolver                import SuccessExtensionResolver
from success.engine.context.policy.SuccessCorsPolicyProvider        import SuccessCorsPolicyProvider
from success.engine.context.policy.SuccessJwtPolicyProvider         import SuccessJwtPolicyProvider
from success.engine.context.policy.SuccessLoginPolicyProvider       import SuccessLoginPolicyProvider
from success.engine.context.policy.SuccessPermissionsPolicyProvider import SuccessPermissionsPolicyProvider
from success.engine.context.policy.SuccessSecurityPolicyProvider    import SuccessSecurityPolicyProvider
from success.engine.context.policy.SuccessSessionPolicyProvider     import SuccessSessionPolicyProvider

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessPreInputPolicy ( SuccessClass ) :
  """
  Pre-input policy handler.

  Evaluates policies before processing input, including
  permissions, session states, and action-specific authorizations.
  """


  def __init__ ( self, providers : list = None ) -> None :
    """
    Initialize the pre-input policy handler.

    Args:
      providers: List of policy providers. Uses default providers if None.
    """
    super ().__init__ ()
    self._providers = providers or [
      SuccessCorsPolicyProvider (),
      SuccessSessionPolicyProvider (),
      SuccessJwtPolicyProvider (),
      SuccessLoginPolicyProvider (),
      SuccessSecurityPolicyProvider (),
      SuccessPermissionsPolicyProvider ()
    ]


  def evaluate ( self, action, method : str ) -> dict :
    """
    Evaluate pre-input policies for an action.

    This is the central point for pre-input validations:
    - Permissions
    - Session states
    - Action-specific authorizations

    Args:
      action: The action to evaluate.
      method: HTTP method name.

    Returns:
      dict: Allow result if all policies pass, deny result otherwise.
    """
    context = self._buildContext ()
    defaultSpec = self._buildDefaultSpec ( context )
    actionSpec = self._extractSpec ( action, method )
    spec = defaultSpec.copy ()
    spec.update ( actionSpec )

    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION START] ---
    # Security hardening: introduce explicit policy mode (lenient|strict)
    # and optional public actions to avoid fail-open behavior in strict mode.
    policyMode = self._resolvePolicyMode ( context )
    isPublicAction = self._isPublicAction ( spec )
    hasExplicitPolicy = self._hasExplicitPolicy ( action, actionSpec )

    if policyMode == "strict" and not isPublicAction and not hasExplicitPolicy :
      return self._deny (
        status  = 403,
        message = "La acción requiere policySpec explícito o marcarse como pública.",
        code    = "POLICY_SPEC_REQUIRED",
        _type   = "authorization"
      )

    if policyMode == "lenient" and not isPublicAction and not hasExplicitPolicy :
      self._logger.log (
        f"Advertencia de seguridad: acción '{action.__class__.__name__}' sin policySpec explícito (modo lenient).",
        "WARNING"
      )

    if isPublicAction :
      return self._allow ()
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION END] ---

    for provider in self._providers :
      if not provider.supports ( spec, context ) :
        continue
      result = provider.evaluate ( spec, context )
      normalized = self._normalizeResult ( result )
      if not normalized.get ( "allowed", True ) :
        return normalized

    policyCallback = getattr ( action, "preInputPolicy", None )
    if callable ( policyCallback ) :
      result = policyCallback ( method )
      normalized = self._normalizeResult ( result )
      if not normalized.get ( "allowed", True ) :
        return normalized

    return self._allow ()


  def _extractSpec ( self, action, method : str ) -> dict :
    """
    Extract policy specification from the action.

    Args:
      action: The action to extract spec from.
      method: HTTP method name.

    Returns:
      dict: Extracted policy specification.
    """
    policySpec = {}
    policySpecCallback = getattr ( action, "policySpec", None )
    if callable ( policySpecCallback ) :
      rawSpec = policySpecCallback ()
      if isinstance ( rawSpec, dict ) :
        policySpec.update ( rawSpec )

    methodPolicies = policySpec.get ( "methods", {} )
    if isinstance ( methodPolicies, dict ) :
      methodSpec = methodPolicies.get ( method ) or methodPolicies.get ( method.lower () ) or {}
      if isinstance ( methodSpec, dict ) :
        merged = policySpec.copy ()
        merged.update ( methodSpec )
        policySpec = merged

    return policySpec


  def _resolvePolicyMode ( self, context : dict ) -> str :
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION START] ---
    """
    Resolve policy mode from app config.

    Allowed values:
      - lenient (default): keep backward compatibility.
      - strict: fail-closed if action has no explicit policy/public declaration.
    """
    appConfig = context.get ( "app_config", {} ) if isinstance ( context, dict ) else {}
    mode = str ( appConfig.get ( "SUCCESS_POLICY_MODE", "lenient" ) ).strip ().lower ()
    if mode not in [ "lenient", "strict" ] :
      mode = "lenient"
    return mode
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION END] ---


  def _isPublicAction ( self, spec : dict ) -> bool :
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION START] ---
    """
    Determine whether an action is explicitly public.
    """
    if not isinstance ( spec, dict ) :
      return False
    return bool ( spec.get ( "public", False ) )
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION END] ---


  def _hasExplicitPolicy ( self, action, actionSpec : dict ) -> bool :
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION START] ---
    """
    Determine whether action declared an explicit policySpec.

    We require:
      - policySpec callback exists, and
      - extracted actionSpec has at least one key.
    """
    policySpecCallback = getattr ( action, "policySpec", None )
    if not callable ( policySpecCallback ) :
      return False
    if not isinstance ( actionSpec, dict ) :
      return False
    return bool ( actionSpec )
    # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION END] ---


  def _buildContext ( self ) -> dict :
    """
    Build the evaluation context.

    Returns:
      dict: Context dictionary with app_config and extensions.
    """
    appConfig = {}
    try :
      appConfig = dict ( current_app.config )
    except Exception :
      appConfig = {}

    # context = {
    #   "app_config" : appConfig,
    #   "extensions" : {
    #     "cors"     : SuccessContext ().getExtension ( "SuccessCorsExtension" ),
    #     "jwt"      : SuccessContext ().getExtension ( "SuccessJwtExtension" ),
    #     "session"  : SuccessContext ().getExtension ( "SuccessSessionExtension" ),
    #     "security" : SuccessContext ().getExtension ( "SuccessSecurityExtension" ),
    #     "login"    : SuccessContext ().getExtension ( "SuccessLoginExtension" ),
    #     "acl"      : SuccessContext ().getExtension ( "SuccessAclExtension" )
    #   }
    # }
    resolver = SuccessExtensionResolver ()
    context  = {
      "app_config" : appConfig,
      "extensions" : resolver.buildPolicyExtensions ()
    }
    return context


  def _buildDefaultSpec ( self, context : dict ) -> dict :
    """
    Build default specification from extension policy defaults.

    Args:
      context: Evaluation context dictionary.

    Returns:
      dict: Default policy specification.
    """
    defaultSpec = {}
    extensions = context.get ( "extensions", {} ) if isinstance ( context, dict ) else {}
    if not isinstance ( extensions, dict ) :
      return defaultSpec

    for extension in extensions.values () :
      if extension is None :
        continue
      policyDefaults = getattr ( extension, "policyDefaults", None )
      if not callable ( policyDefaults ) :
        continue

      try :
        values = policyDefaults ()
      except Exception :
        values = {}

      if isinstance ( values, dict ) :
        defaultSpec.update ( values )

    return defaultSpec


  def _allow ( self ) -> dict :
    """
    Return an allow result.

    Returns:
      dict: Allow result dictionary.
    """
    return {
      "allowed" : True,
      "status"  : 200,
      "message" : "OK",
      "error"   : None,
      "code"    : None,
      "type"    : None
    }


  def _deny ( self, status : int = 403, message : str = "Acceso denegado", error = None, code : str = "FORBIDDEN", _type : str = "authorization" ) -> dict :
    """
    Return a deny result.

    Args:
      status: HTTP status code (default: 403).
      message: Denial message.
      error: Additional error details.
      code: Error code.
      _type: Denial type.

    Returns:
      dict: Deny result dictionary.
    """
    return {
      "allowed" : False,
      "status"  : status,
      "message" : message,
      "error"   : error or message,
      "code"    : code,
      "type"    : _type
    }


  def _normalizeResult ( self, result ) -> dict :
    """
    Normalize a policy result to standard format.

    Args:
      result: Result to normalize (bool or dict).

    Returns:
      dict: Normalized result dictionary.
    """
    if isinstance ( result, bool ) :
      return self._allow () if result else self._deny ()

    if isinstance ( result, dict ) :
      normalized = self._allow ()
      normalized.update ( result )
      normalized [ "allowed" ] = bool ( normalized.get ( "allowed", True ) )
      return normalized

    return self._allow ()
