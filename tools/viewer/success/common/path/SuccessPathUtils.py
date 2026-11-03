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
from pathlib import Path
import os

# Success Libraries / Librerías Success

# Preconditions / Precondiciones


class SuccessPathUtils () :
  """
  Path utilities for filesystem operations.

  Provides utilities for working with file and directory paths
  without depending on upper layers (core/engine).
  """

  __baseDir : str = None


  def __init__ ( self, path : str ) -> None :
    """
    Initialize the path resolver with a base path.

    Args:
      path: Base path for resolving relative paths.
    """
    absPath        = os.path.abspath ( path )
    self.__baseDir = absPath if os.path.isdir ( absPath ) else os.path.dirname ( absPath )


  @staticmethod
  def getEnvPath ( envFilePath : str = None ) -> str :
    if ( envFilePath ) :
      dotEnvPath = os.path.join ( envFilePath, '.env' )

    else :
      dotEnvPath = os.path.join ( os.path.dirname ( __file__ ), '../../.env' )

    return dotEnvPath


  @staticmethod
  def getPath ( path : str ) -> str :
    """
    Get the directory of a path.

    Args:
      path: Path to process.

    Returns:
      str: The directory of the path.
    """
    return os.path.dirname ( os.path.abspath ( path ) )


  @staticmethod
  def join ( *paths ) -> str :
    """
    Join multiple path components.

    Args:
      *paths: Path components to join.

    Returns:
      str: The joined path.
    """
    return os.path.join ( *paths )


  @staticmethod
  def normalize ( path : str ) -> str :
    """
    Normalize a path by removing redundant components.

    Args:
      path: Path to normalize.

    Returns:
      str: The normalized path.
    """
    return os.path.normpath ( path )


  @staticmethod
  def absolute ( path : str ) -> str :
    """
    Convert a relative path to absolute.

    Args:
      path: Path to convert.

    Returns:
      str: The absolute path.
    """
    return os.path.abspath ( path )


  @staticmethod
  def relative ( path : str, start : str = None ) -> str :
    """
    Get the relative path from a starting point.

    Args:
      path: Target path.
      start: Starting path (default: current directory).

    Returns:
      str: The relative path.
    """
    return os.path.relpath ( path, start or os.getcwd () )


  @staticmethod
  def exists ( path : str ) -> bool :
    """
    Check if a path exists.

    Args:
      path: Path to check.

    Returns:
      bool: True if the path exists.
    """
    return os.path.exists ( path )


  @staticmethod
  def isDirectory ( path : str ) -> bool :
    """
    Check if a path is a directory.

    Args:
      path: Path to check.

    Returns:
      bool: True if it is a directory.
    """
    return os.path.isdir ( path )


  @staticmethod
  def isFile ( path : str ) -> bool :
    """
    Check if a path is a file.

    Args:
      path: Path to check.

    Returns:
      bool: True if it is a file.
    """
    return os.path.isfile ( path )


  @staticmethod
  def getAppNameFromPath ( path : str ) -> str :
    """
    Extract the application name from a path.

    Assumes the path always follows the pattern: .../apps/{app_name}/...

    Args:
      path: Path to process.

    Returns:
      str: The application name.

    Raises:
      RuntimeError: If the name cannot be extracted.
    """
    parts = Path ( path ).parts
    try :
      apps_index = parts.index ( "apps" )
      return parts [ apps_index + 1 ]  # el primer valor después de apps/

    except ( ValueError, IndexError ) :
      raise RuntimeError ( f"No se pudo obtener el nombre de la aplicación a partir de appPath: {path}" )


  def templatesFolder ( self ) -> str :
    """
    Get the path to the templates folder.

    Returns:
      str: Full path to the templates folder.
    """
    return os.path.join ( self.__baseDir, "templates" )


  def staticFolder ( self ) -> str :
    """
    Get the path to the static folder.

    Returns:
      str: Full path to the static folder.
    """
    return os.path.join ( self.__baseDir, "static" )


  @staticmethod
  def resolveTemplatesFolder ( baseDir : str ) -> str :
    """
    Resolve the templates folder path from a base directory.

    Args:
      baseDir: Base directory.

    Returns:
      str: Full path to the templates folder.
    """
    return os.path.join ( baseDir, "templates" )


  @staticmethod
  def resolveStaticFolder ( baseDir : str ) -> str :
    """
    Resolve the static folder path from a base directory.

    Args:
      baseDir: Base directory.

    Returns:
      str: Full path to the static folder.
    """
    return os.path.join ( baseDir, "static" )


  @staticmethod
  def resolveConfigFolder ( baseDir : str ) -> str :
    """
    Resolve the config folder path from a base directory.

    Args:
      baseDir: Base directory.

    Returns:
      str: Full path to the config folder.
    """
    return os.path.join ( baseDir, "config" )


  @staticmethod
  def resolveLogFolder ( baseDir : str ) -> str :
    """
    Resolve the log folder path from a base directory.

    Args:
      baseDir: Base directory.

    Returns:
      str: Full path to the log folder.
    """
    return os.path.join ( baseDir, "log" )


  @staticmethod
  def ensureDirectory ( path : str, mode : int = 0o755 ) -> str :
    """
    Ensure a directory exists, creating it if necessary.

    Args:
      path: Directory path.
      mode: Directory permissions (default: 0o755).

    Returns:
      str: The ensured directory path.
    """
    os.makedirs ( path, mode = mode, exist_ok = True )
    return path


  @staticmethod
  def getParent ( path : str, levels : int = 1 ) -> str :
    """
    Get the parent directory of a path.

    Args:
      path: Path to process.
      levels: Number of levels to go up.

    Returns:
      str: The parent directory path.
    """
    result = path
    for _ in range ( levels ) :
      result = os.path.dirname ( result )
    return result


  @staticmethod
  def getExtension ( path : str ) -> str :
    """
    Get the extension of a file.

    Args:
      path: File path.

    Returns:
      str: The file extension (including the dot).
    """
    return os.path.splitext ( path ) [ 1 ]


  @staticmethod
  def getBasename ( path : str, withoutExtension : bool = False ) -> str :
    """
    Get the base name of a path.

    Args:
      path: Path to process.
      withoutExtension: If True, excludes the extension.

    Returns:
      str: The base name of the path.
    """
    basename = os.path.basename ( path )
    
    if withoutExtension :
      return os.path.splitext ( basename ) [ 0 ]
    
    return basename


  @staticmethod
  def listDirectory ( path : str, pattern : str = None, recursive : bool = False ) -> list :
    """
    List the contents of a directory.

    Args:
      path: Directory to list.
      pattern: Optional pattern to filter (e.g., '*.py').
      recursive: If True, list recursively.

    Returns:
      list: List of files/directories.
    """
    if not os.path.isdir ( path ) :
      return []
    
    if recursive :
      import glob
      search_pattern = os.path.join ( path, "**", pattern or "*" )
      return glob.glob ( search_pattern, recursive = True )
    
    if pattern :
      import glob
      search_pattern = os.path.join ( path, pattern )
      return glob.glob ( search_pattern )
    
    return os.listdir ( path )
