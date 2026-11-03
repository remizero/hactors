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
from typing import List
import os

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessModuleMetadata () :
  """
  Extract metadata from module paths.

  Provides utilities for analyzing module paths and extracting
  information such as application name, scope, protocol, etc.
  WITHOUT depending on upper layers (core/engine).
  """

  @staticmethod
  def getAppName ( modulePath : str ) -> str :
    """
    Extract the application name from a module path.

    Args:
      modulePath: Module path (e.g., 'apps.myapp.services.MyService').

    Returns:
      str: Application name or 'unknown' if it cannot be determined.
    """
    parts = modulePath.split ( "." )

    if not parts :
      return "unknown"

    if parts [ 0 ] == "apps" :
      idx = parts.index ( "apps" )
      return parts [ idx + 1 ]

    if parts [ 0 ] == "success" :
      return "success"

    return "unknown"


  @staticmethod
  def getAppNameFromPath ( fsPath : str ) -> str :
    """
    Extract the application name from a filesystem path.

    Args:
      fsPath: Filesystem path (e.g., '/path/to/apps/myapp/services').

    Returns:
      str: Application name.

    Raises:
      ValueError: If the application name cannot be determined.
    """
    parts = fsPath.split ( "." ) if "." in fsPath else fsPath.split ( os.sep )
    try :
      idx = parts.index ( "apps" )
      return parts [ idx + 1 ]

    except ( ValueError, IndexError ) :
      raise ValueError ( f"No se pudo determinar el nombre de la aplicación a partir de '{fsPath}'" )


  @staticmethod
  def getScope ( modulePath : str ) -> str :
    """
    Determine the base scope from a module path.

    Args:
      modulePath: Module path.

    Returns:
      str: 'application' for apps, 'framework' for success, 'unknown' otherwise.

    Examples:
      >>> getScope ( 'apps.myapp.services.MyService' )
      'application'
      >>> getScope ( 'success.engine.io.SuccessAction' )
      'framework'
    """
    parts = modulePath.split ( "." )

    if not parts :
      return "unknown"

    if parts [ 0 ] == "apps" :
      return "application"

    if parts [ 0 ] == "success" :
      return "framework"

    return "unknown"


  @staticmethod
  def getProtocol ( modulePath : str ) -> str :
    """
    Extract the protocol from a service path.

    Args:
      modulePath: Module path (e.g., 'apps/myapp/services/rest/MyAction').

    Returns:
      str: Protocol name (e.g., 'rest', 'view') or 'unknown'.
    """
    parts = modulePath.split ( '/' )
    try :
      idx = parts.index ( 'services' )
      return parts [ idx + 1 ]

    except ( ValueError, IndexError ) :
      return "unknown"


  @staticmethod
  def normalizePackageName ( packagePath : str, prefix : str = None ) -> str :
    """
    Normalize a package path converting filesystem path to module notation.

    Args:
      packagePath: Package path in filesystem.
      prefix: Optional prefix to add to the last component.

    Returns:
      str: Normalized path in module notation.
    """
    normalizedPath = os.path.normpath ( packagePath )
    parts = normalizedPath.split ( os.sep )

    if parts and prefix :
      last = parts [ -1 ]
      parts [ -1 ] = f"{prefix.strip ( '_' )}_{last}"

    return ".".join ( parts )


  @staticmethod
  def createAppName ( modulePath : str, envPrefix : str = None ) -> str :
    """
    Create an application name with optional prefix.

    Args:
      modulePath: Module path.
      envPrefix: Prefix from SUCCESS_APP_PREFIX environment variable.

    Returns:
      str: Application name with prefix if applicable.
    """
    app_name = SuccessModuleMetadata.getAppName ( modulePath )
    
    if envPrefix :
      return f"{envPrefix}{app_name}"
    
    return app_name


  @staticmethod
  def getModuleName ( modulePath : str ) -> str :
    """
    Extract the module name (last component) from a path.

    Args:
      modulePath: Full module path.

    Returns:
      str: Module name without extension.
    """
    parts = modulePath.split ( "." )
    return parts [ -1 ] if parts else ""


  @staticmethod
  def getPackagePath ( modulePath : str ) -> str :
    """
    Extract the package path (everything except the last component).

    Args:
      modulePath: Full module path.

    Returns:
      str: Package path.
    """
    parts = modulePath.split ( "." )
    return ".".join ( parts [ : -1 ] ) if len ( parts ) > 1 else ""


  @staticmethod
  def getModuleParts ( modulePath : str ) -> List [ str ] :
    """
    Get all parts of a module path.

    Args:
      modulePath: Full module path.

    Returns:
      List[str]: List of module components.
    """
    return modulePath.split ( "." )


  @staticmethod
  def isAppModule ( modulePath : str ) -> bool :
    """
    Check if a module belongs to an application.

    Args:
      modulePath: Module path.

    Returns:
      bool: True if the module is from an application.
    """
    return modulePath.startswith ( "apps." )


  @staticmethod
  def isFrameworkModule ( modulePath : str ) -> bool :
    """
    Check if a module belongs to the Success framework.

    Args:
      modulePath: Module path.

    Returns:
      bool: True if the module is from the framework.
    """
    return modulePath.startswith ( "success." )