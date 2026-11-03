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


class SuccessPathResolver () :
  """
  Path resolution utilities for the Success framework.

  Provides methods for resolving filesystem paths, templates, and static folders.
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
  def getPath ( path : str ) -> str :
    """
    Get the directory of a path.

    Args:
      path: Path to process.

    Returns:
      str: Directory of the path.
    """
    return os.path.dirname ( os.path.abspath ( path ) )


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
  def getAppNameFromPath ( path : str ) -> str :
    """
    Extract the application name from the appPath.

    Assumes the path always follows the pattern: .../apps/{app_name}/...

    Args:
      path: Path to process.

    Returns:
      str: Application name.

    Raises:
      RuntimeError: If the application name cannot be extracted.
    """
    parts = Path ( path ).parts
    try :
      apps_index = parts.index ( "apps" )
      return parts [ apps_index + 1 ]  # el primer valor después de apps/

    except ( ValueError, IndexError ) :
      raise RuntimeError ( f"No se pudo obtener el nombre de la aplicación a partir de appPath: {path}" )
