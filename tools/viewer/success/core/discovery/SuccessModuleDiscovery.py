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
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


@dataclass ( frozen = True )
class DiscoveredModule () :
  """
  Represents a module discovered in the filesystem.

  Attributes:
    fs_path: Absolute path in the filesystem.
    import_path: Python import path (e.g., 'apps.myapp.services.MyModule').
    is_package: True if it is a package (has __init__.py).
  """
  fs_path     : Path
  import_path : str
  is_package  : bool


class SuccessModuleDiscovery () :
  """
  Module discovery in filesystem.

  Provides utilities for discovering Python packages and modules
  in the filesystem without importing anything at runtime.

  This class can depend on common reflection without violating architecture.
  """

  def __init__ ( self, root : Path ) -> None :
    """
    Initialize the module discoverer.

    Args:
      root: Root path to start discovery from.
    """
    self.root = Path ( root ).resolve ()


  def discoverModules ( self, subdir : Optional [ str ] = None,
                        excludePatterns : List [ str ] = None ) -> List [ DiscoveredModule ] :
    """
    Discover modules and packages in the filesystem.

    Args:
      subdir: Optional subdirectory within root to search.
      excludePatterns: List of patterns to exclude (e.g., ['__pycache__', '*.pyc']).

    Returns:
      List[DiscoveredModule]: List of discovered modules.
    """
    excludePatterns = excludePatterns or [ '__pycache__', '*.pyc', '*.pyo', '.git', 'venv', 'node_modules' ]
    
    base    = self.root / subdir if subdir else self.root
    modules = []

    for path in base.rglob ( "*.py" ) :
      # Excluir patrones
      if any ( pattern in str ( path ) for pattern in excludePatterns ) :
        continue
      
      # Determinar si es paquete o módulo
      is_pkg = path.name == "__init__.py"
      
      # Calcular import path relativo a root
      try :
        relative = path.relative_to ( base )
        
        if is_pkg :
          # Para paquetes, usar el directorio padre
          import_parts = list ( relative.parts [ : -1 ] )  # Excluir __init__.py
        else :
          # Para módulos, excluir extensión .py
          import_parts = list ( relative.parts )
          import_parts [ -1 ] = Path ( import_parts [ -1 ] ).stem
        
        import_path = ".".join ( import_parts ) if import_parts else ""
        
        modules.append ( DiscoveredModule ( 
          fs_path     = path.resolve (), 
          import_path = import_path, 
          is_package  = is_pkg 
        ) )
      
      except ValueError :
        # Path no es relativo a base, saltar
        continue

    return modules


  def discoverPackages ( self, subdir : Optional [ str ] = None ) -> List [ Path ] :
    """
    Discover only packages (directories with __init__.py).

    Args:
      subdir: Optional subdirectory within root to search.

    Returns:
      List[Path]: List of discovered package paths.
    """
    packages = []
    base = self.root / subdir if subdir else self.root

    for init_file in base.rglob ( "__init__.py" ) :
      packages.append ( init_file.parent.resolve () )

    return packages


  def discoverActions ( self, appPath : str ) -> List [ DiscoveredModule ] :
    """
    Discover Action modules in a specific application.

    Args:
      appPath: Application path (e.g., 'apps/myapp').

    Returns:
      List[DiscoveredModule]: List of discovered Action modules.
    """
    actions_path = Path ( appPath ) / "services"
    
    if not actions_path.exists () :
      return []
    
    discovery = SuccessModuleDiscovery ( actions_path )
    modules = discovery.discoverModules ()
    
    # Filtrar solo módulos que terminan en 'Action'
    action_modules = [ 
      m for m in modules 
      if not m.is_package and m.import_path.endswith ( "Action" ) 
    ]
    
    return action_modules


  def fsPathToModule ( self, appPath : str, fsPath : str ) -> str :
    """
    Convert a filesystem path to Python module path.

    Args:
      appPath: Base application path.
      fsPath: Filesystem path to convert.

    Returns:
      str: Python module path.

    Raises:
      ValueError: If fsPath is not within appPath.
    """
    base   = Path ( appPath ).resolve ()
    target = Path ( fsPath ).resolve ()

    try :
      relative = target.relative_to ( base )

    except ValueError :
      raise ValueError ( f"Action fuera del appPath: {fsPath}" )

    parts = list ( relative.parts )

    # Quitar slash final si existe
    if parts and parts [ -1 ] == "" :
      parts = parts [ : -1 ]

    # Convertir a notación de módulo
    module_parts = []
    for part in parts :
      if part.endswith ( ".py" ) :
        module_parts.append ( part [ : -3 ] )  # Quitar .py
      else :
        module_parts.append ( part )

    return ".".join ( module_parts )


  def moduleToFsPath ( self, appPath : str, modulePath : str ) -> Path :
    """
    Convert a Python module path to filesystem path.

    Args:
      appPath: Base application path.
      modulePath: Module path to convert.

    Returns:
      Path: Corresponding filesystem path.
    """
    base = Path ( appPath ).resolve ()
    parts = modulePath.split ( "." )
    
    return base / "/".join ( parts ) / f"{parts [ -1 ]}.py"


  def countModules ( self, subdir : Optional [ str ] = None ) -> dict :
    """
    Count discovered modules and packages.

    Args:
      subdir: Optional subdirectory to count.

    Returns:
      dict: Dictionary with module and package counts.
    """
    modules = self.discoverModules ( subdir )
    
    return {
      "total_modules" : len ( [ m for m in modules if not m.is_package ] ),
      "total_packages" : len ( [ m for m in modules if m.is_package ] ),
      "total" : len ( modules )
    }
