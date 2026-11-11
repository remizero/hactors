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


class SuccessPermissionsPolicyProvider ( SuccessPolicyProvider ) :
  """
  Permissions policy provider.

  Evaluates role and permission-based policies by checking user
  roles and permissions stored in the session.
  """


  def supports ( self, spec : dict, context : dict ) -> bool :
    """
    Check if this provider supports the permissions policy specification.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      bool: True if spec contains 'roles_any', 'permissions_all', or 'require_acl'.
    """
    if not isinstance ( spec, dict ) :
      return False
    return bool ( spec.get ( "roles_any" ) ) or bool ( spec.get ( "permissions_all" ) ) or bool ( spec.get ( "require_acl" ) )


  def evaluate ( self, spec : dict, context : dict ) -> dict :
    """
    Evaluate the permissions policy against the current session.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      dict: Allow result if permissions are sufficient, deny result otherwise.
    """
    if spec.get ( "require_acl" ) :
      acl = self._getExtension ( context, "acl" )
      if acl is None :
        return self.deny ( 500, "Extensión ACL no disponible.", "ACL_EXTENSION_MISSING", "acl" )

    rolesRequired = self._toList ( spec.get ( "roles_any", [] ) )
    if rolesRequired :
      rolesCurrent = self._currentRoles ()
      if not any ( role in rolesCurrent for role in rolesRequired ) :
        return self.deny ( 403, "Rol no autorizado.", "ROLE_FORBIDDEN", "authorization" )

    permissionsRequired = self._toList ( spec.get ( "permissions_all", [] ) )
    if permissionsRequired :
      permissionsCurrent = self._currentPermissions ()
      missing = [ permission for permission in permissionsRequired if permission not in permissionsCurrent ]
      if missing :
        return self.deny ( 403, "Permisos insuficientes.", "PERMISSION_DENIED", "authorization", { "missing": missing } )

    return self.allow ()


  def _currentRoles ( self ) -> set :
    """
    Get the current user's roles from session.

    Returns:
      set: Set of role strings from session.
    """
    roles = set ()
    for key in [ "user_role", "role", "role_id" ] :
      value = session.get ( key )
      if value is not None :
        roles.add ( str ( value ) )

    sessionRoles = session.get ( "roles" )
    if isinstance ( sessionRoles, list ) :
      for role in sessionRoles :
        roles.add ( str ( role ) )

    return roles


  def _currentPermissions ( self ) -> set :
    """
    Get the current user's permissions from session.

    Returns:
      set: Set of permission strings from session.
    """
    permissions = set ()
    for key in [ "permissions", "perms", "permission" ] :
      value = session.get ( key )
      if isinstance ( value, list ) :
        for permission in value :
          permissions.add ( str ( permission ) )
      elif isinstance ( value, str ) :
        permissions.add ( value )
    return permissions


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
      return [ value ]
    return [ str ( value ) ]


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
