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
from types  import ModuleType
from typing import Type
from typing import List
import importlib
import os

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessModuleLoader () :
  """
  Dynamic module loading utilities.

  Provides utilities for importing modules and loading classes
  at runtime without depending on upper layers (core/engine).
  """

  @staticmethod
  def importModule ( importPath : str ) -> ModuleType :
    """
    Import a Python module at runtime.

    Args:
      importPath: Import path of the module (e.g., 'success.common.tools.SuccessHttp').

    Returns:
      ModuleType: The imported module.

    Raises:
      ImportError: If the module does not exist.
    """
    return importlib.import_module ( importPath )


  @staticmethod
  def loadClass ( importPath : str, className : str ) -> Type :
    """
    Load a class from a module.

    Args:
      importPath: Import path of the module.
      className: Name of the class to load.

    Returns:
      Type: The requested class.

    Raises:
      ImportError: If the module or class does not exist.
    """
    module = SuccessModuleLoader.importModule ( importPath )
    
    if not hasattr ( module, className ) :
      raise ImportError ( f"No se encontró la clase '{className}' en el módulo '{importPath}'" )
    
    return getattr ( module, className )


  @staticmethod
  def loadClassFromString ( fullClassPath : str ) -> Type :
    """
    Load a class from its full path as a string.

    Args:
      fullClassPath: Full path of the class (e.g., 'success.common.tools.SuccessHttp.MyClass').

    Returns:
      Type: The requested class.

    Raises:
      ImportError: If the path is invalid or the class does not exist.
    """
    if fullClassPath is None :
      raise ImportError ( "Ruta de clase inválida: None" )
    
    parts = fullClassPath.rsplit ( ".", 1 )

    if len ( parts ) != 2 :
      raise ImportError ( f"Ruta de clase inválida: '{fullClassPath}'. Formato esperado: 'modulo.Clase'" )
    
    moduleName, className = parts
    return SuccessModuleLoader.loadClass ( moduleName, className )


  @staticmethod
  def normalizeImportPath ( packagePath : str, moduleParts : List [ str ] ) -> str :
    """
    Normalize an import path by joining package and module parts.

    Args:
      packagePath: Base package path.
      moduleParts: List of module parts.

    Returns:
      str: Normalized import path.
    """
    return ".".join ( [ packagePath ] + moduleParts )


  @staticmethod
  def normalizePackage ( packagePath : str, prefix : str = None ) -> str :
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
  def reloadModule ( module : ModuleType ) -> ModuleType :
    """
    Reload an existing module.

    Args:
      module: Module to reload.

    Returns:
      ModuleType: The reloaded module.
    """
    return importlib.reload ( module )


  @staticmethod
  def isModuleAvailable ( moduleName : str ) -> bool :
    """
    Check if a module is available for import.

    Args:
      moduleName: Name of the module to check.

    Returns:
      bool: True if the module is available, False otherwise.
    """
    try :
      importlib.import_module ( moduleName )
      return True
    except ImportError :
      return False
