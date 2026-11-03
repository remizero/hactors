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
from flask import Flask
import os

# Success Libraries / Librerías Success
from success.common.base.SuccessClass              import SuccessClass
from success.common.infra.config.SuccessSystemEnv  import SuccessSystemEnv
from success.core.app.SuccessAppLoader             import SuccessAppLoader
from success.core.app.SuccessAppValidator          import SuccessAppValidator
from success.core.SuccessSystemState               import SuccessSystemState
from success.common.tools.SuccessAppPlaceholderFactory import SuccessAppPlaceholderFactory

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAppScan ( SuccessClass ) :
  """
  Scanner and loader for Success system applications.

  This class provides a simplified interface for loading individual
  or multiple applications, delegating actual loading to SuccessAppLoader.

  Purpose:
  ----------
  SuccessAppScan is responsible for:
  - Providing convenient methods for loading individual apps
  - Integrating SuccessAppLoader with SuccessSystemState
  - Handling fallback to SuccessAppPlaceholder when needed

  Usage:
  ------
  scanner = SuccessAppScan()
  apps = scanner.getSecondaryApps()  # Load secondary apps
  root = scanner.getRootApp()        # Load main app

  Attributes:
      _rootApp (str): Name of main application from SUCCESS_MAIN_APP.
      _secondaryApps (list): List of secondary apps from SUCCESS_SECONDARY_APPS.

  Note:
    - This class is a wrapper over SuccessAppLoader for compatibility
    - For full loading of all apps, use SuccessAppLoader directly
  """

  _rootApp       : str  = None
  _secondaryApps : list = []


  def __init__ ( self ) :
    """
    Initialize the application scanner.

    Reads SUCCESS_MAIN_APP and SUCCESS_SECONDARY_APPS environment
    variables to determine which applications to load.
    """
    super ().__init__ ()
    self._rootApp       = SuccessSystemEnv.get ( "SUCCESS_MAIN_APP", "" ).strip ()
    self._secondaryApps = SuccessSystemEnv.toList ( "SUCCESS_SECONDARY_APPS" )


  def getSecondaryApps ( self ) -> dict [ str, Flask ] :
    """
    Load and return secondary applications.

    Uses SuccessAppLoader to load all apps and filters only those
    defined as secondary in SUCCESS_SECONDARY_APPS.

    Returns:
      dict[str, Flask]: Dictionary with mount path → Flask instance.
                       Paths have format '/{appName}'.

    Note:
      - Failed apps are registered in SuccessSystemState
      - Returns empty dict if no secondary apps configured
    """
    self._logger.log ( "Iniciando carga de aplicaciones secundarias del sistema.", "INFO" )

    apps = {}

    try :
      # Usar SuccessAppLoader para cargar todas las apps
      # Retorna: {'main': Flask | None, 'secondaries': dict[str, Flask]}
      loader = SuccessAppLoader ()
      result = loader.load ()

      # Obtener secondaries ya filtradas del resultado
      for appName, app in result [ 'secondaries' ].items () :
        if appName in [ str ( a ).strip () for a in self._secondaryApps ] :
          mount_path = f"/{appName}"
          apps [ mount_path ] = app
          self._logger.log ( f"App secundaria '{appName}' cargada en '{mount_path}'.", "INFO" )

      self._logger.log ( "Carga de aplicaciones secundarias del sistema realizada exitosamente.", "INFO" )

    except Exception as e :
      self._logger.log ( f"Error durante carga de apps secundarias: {e}", "ERROR" )
      raise

    return apps


  def getRootApp ( self ) -> Flask | None :
    """
    Load and return the main (root) application.

    Uses SuccessAppLoader to load all apps and returns the app
    defined as main in SUCCESS_MAIN_APP.

    Returns:
      Flask | None: Main app instance, or None if it fails and
                    SUCCESS_ALLOW_NO_MAIN_APP is True (uses placeholder).

    Raises:
      RuntimeError: If main app cannot be loaded and
                    SUCCESS_ALLOW_NO_MAIN_APP is False.

    Note:
      - If SUCCESS_ALLOW_NO_MAIN_APP is True in development, uses placeholder
      - Returns None if fails in non-development mode with ALLOW_NO_MAIN_APP
    """
    self._logger.log ( "Iniciando carga de aplicación principal (root) del sistema.", "INFO" )

    try :
      # Usar SuccessAppLoader para cargar todas las apps
      # Retorna: {'main': Flask | None, 'secondaries': dict[str, Flask]}
      loader = SuccessAppLoader ()
      result = loader.load ()

      # Obtener la app principal del resultado
      if result [ 'main' ] is not None :
        self._logger.log ( "Carga de aplicación principal del sistema realizada exitosamente.", "INFO" )
        return result [ 'main' ]

      # La app principal no se cargó
      if SuccessSystemEnv.isTrue ( "SUCCESS_ALLOW_NO_MAIN_APP" ) :
        if SuccessSystemEnv.get ( "APP_ENV", "development" ) != "development" :
          self._logger.log ( "🚫 'SUCCESS_ALLOW_NO_MAIN_APP' solo permitido en modo desarrollo.", "ERROR" )
          return None

        self._logger.log ( "⚠️ Usando SuccessAppPlaceholder como raíz.", "WARNING" )
        return SuccessAppPlaceholderFactory.build ()

      self._logger.log ( "🚫 No se pudo cargar la aplicación principal y no se permite continuar sin ella.", "ERROR" )
      raise RuntimeError ( f"No se pudo cargar la app principal '{self._rootApp}'." )

    except RuntimeError :
      raise

    except Exception as e :
      self._logger.log ( f"Error durante carga de app principal: {e}", "ERROR" )

      if SuccessSystemEnv.isTrue ( "SUCCESS_ALLOW_NO_MAIN_APP" ) :
        if SuccessSystemEnv.get ( "APP_ENV", "development" ) != "development" :
          self._logger.log ( "🚫 'SUCCESS_ALLOW_NO_MAIN_APP' solo permitido en modo desarrollo.", "ERROR" )
          return None

        self._logger.log ( "⚠️ Usando SuccessAppPlaceholder como raíz.", "WARNING" )
        return SuccessAppPlaceholderFactory.build ()

      raise


  def getAllApps ( self ) -> dict [ str, Flask ] :
    """
    Load all available apps without duplication and return them.

    Uses SuccessAppLoader to load all configured apps and
    returns them as a single dictionary combining main + secondaries.

    Returns:
      dict[str, Flask]: Dictionary with app name → Flask instance.
                       Includes both main and secondary apps.

    Note:
      - Failed apps are registered in SuccessSystemState
      - Combines 'main' and 'secondaries' result from loader
    """
    self._logger.log ( "Iniciando carga total de aplicaciones del sistema.", "INFO" )

    try :
      # Usar SuccessAppLoader para cargar todas las apps
      # Retorna: {'main': Flask | None, 'secondaries': dict[str, Flask]}
      loader = SuccessAppLoader ()
      result = loader.load ()

      # Combinar main + secondaries en un solo dict
      allApps = {}
      
      if result [ 'main' ] is not None :
        # Obtener nombre de la app principal para la clave
        mainName = self._rootApp or 'main'
        allApps [ mainName ] = result [ 'main' ]
      
      allApps.update ( result [ 'secondaries' ] )

      self._logger.log ( f"Carga total de aplicaciones finalizada. {len ( allApps )} app(s) cargada(s).", "INFO" )

      return allApps

    except Exception as e :
      self._logger.log ( f"Error durante carga total de apps: {e}", "ERROR" )
      raise


  @staticmethod
  def report ( base_dir : str = 'apps' ) -> list [ dict ] :
    """
    Generate a report of available applications in a directory.

    Scans the specified directory and returns information about
    each found application, including its structural validity.

    Args:
      base_dir: Base directory to scan (default 'apps').

    Returns:
      list[dict]: List of dictionaries with app information:
        - name: App name
        - path: Full path
        - valid_dir: True if it's a valid app directory
        - has_factory: True if it has Flask factory or instance

    Usage:
      report = SuccessAppScan.report()
      for app in report:
        print(f"{app['name']}: valid={app['valid_dir']}")
    """
    results = []

    if not os.path.isdir ( base_dir ) :
      return results

    for item in os.listdir ( base_dir ) :
      full_path = os.path.join ( base_dir, item )
      if not os.path.isdir ( full_path ) :
        continue

      result = {
        'name'      : item,
        'path'      : full_path,
        'valid_dir' : SuccessAppValidator.isValidAppDir ( full_path ),
        'has_factory' : SuccessAppValidator.hasFactoryOrInstance ( full_path ),
      }
      results.append ( result )

    return results
