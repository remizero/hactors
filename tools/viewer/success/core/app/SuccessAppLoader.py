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
from success.common.base.SuccessClass                  import SuccessClass
from success.common.infra.config.SuccessSystemEnv      import SuccessSystemEnv
from success.common.tools.SuccessAppPlaceholderFactory import SuccessAppPlaceholderFactory
from success.common.tools.SuccessJinja                 import SuccessJinja
from success.core.SuccessSystemState                   import SuccessSystemState
from success.core.app.SuccessAppBuilder                import SuccessAppBuilder
from success.core.app.SuccessAppValidator              import SuccessAppValidator

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAppLoader ( SuccessClass ) :
  """
  Application loader for the Success framework.

  Discovers, validates, and builds Success applications according to
  configuration defined in system environment variables.

  Purpose:
  ----------
  SuccessAppLoader is responsible for:
  - Reading SUCCESS_MAIN_APP and SUCCESS_SECONDARY_APPS (explicit config)
  - Scanning apps/ directory if no explicit config (implicit config)
  - Validating each application's structure (SuccessAppValidator)
  - Building each valid application (SuccessAppBuilder)
  - Returning specialized structure with main and secondary apps

  Load strategies (in priority order):
  ----------------------------------------------
  1. EXPLICIT: Uses SUCCESS_MAIN_APP and SUCCESS_SECONDARY_APPS
  2. IMPLICIT: Scans apps/ directory and loads all valid apps found
  3. DEFAULT: Uses default app or SuccessAppPlaceholder if no apps

  Usage:
  ------
  loader = SuccessAppLoader()
  result = loader.load()  # dict {'main': Flask | None, 'secondaries': dict[str, Flask]}

  Attributes:
      _loadedApps (dict[str, Flask]): Applications loaded successfully.
      _appsPath (str): Base directory of applications.
      _mainApp (str): Name of the configured main application.

  Note:
    - Applications are loaded in order: main first, then secondaries
    - Apps that fail validation/build are registered in SuccessSystemState
    - The load() method can be called multiple times (full reload)
    - The return is a specialized dict: {'main': Flask | None, 'secondaries': dict}
  """

  _loadedApps : dict [ str, Flask ] = None
  _appsPath   : str                 = None
  _mainApp    : str                 = None


  def __init__ ( self ) -> None :
    """
    Initialize the application loader.

    Gets the base application path from SUCCESS_APPS_PATH or uses
    'apps' as default. Also reads SUCCESS_MAIN_APP to identify
    the main application.
    """
    super ().__init__ ()
    self._loadedApps = {}
    self._appsPath   = SuccessSystemEnv.get ( "SUCCESS_APPS_PATH", "apps" )
    self._mainApp    = SuccessSystemEnv.get ( "SUCCESS_MAIN_APP", "" ).strip ()


  def load ( self ) -> dict :
    """
    Load all configured applications.

    Executes the load strategy in priority order:
    1. Explicit (SUCCESS_MAIN_APP + SUCCESS_SECONDARY_APPS)
    2. Implicit (automatic scanning of apps/ directory)
    3. Default (default app or placeholder)

    Returns:
      dict: Specialized structure with two keys:
        - 'main': Flask | None - Main application (may be None if not loaded)
        - 'secondaries': dict[str, Flask] - Secondary apps mapped by name

    Example:
      loader = SuccessAppLoader()
      result = loader.load()
      main_app = result['main']  # Flask or None
      secondary_apps = result['secondaries']  # dict[str, Flask]

    Note:
      - Failed apps are registered in SuccessSystemState
      - Load order is: main first, then secondaries
      - If an app fails, error is logged but continues with others
    """
    self._logger.log ( "Iniciando carga de aplicaciones del sistema.", "INFO" )
    self._loadedApps = {}

    # Intentar estrategia explícita primero
    explicitConfigured = self._tryExplicitLoad ()

    if not explicitConfigured :
      # Si no hay config explícita, intentar escaneo implícito
      self._tryImplicitLoad ()

    # Si aún no hay apps, intentar cargar app por defecto
    if not self._loadedApps :
      self._tryDefaultLoad ()

    # Construir resultado especializado
    result = {
      'main': self._loadedApps.get ( self._mainApp ) if self._mainApp else None,
      'secondaries': {
        name: app for name, app in self._loadedApps.items () if name != self._mainApp
      }
    }

    self._logger.log ( f"Carga de aplicaciones finalizada. Principal='{self._mainApp or 'N/A'} {len ( result [ 'secondaries' ] )} app(s) secundaria(s).", "INFO" )

    return result


  def _tryExplicitLoad ( self ) -> bool :
    """
    Attempt to load applications using explicit configuration.

    Reads SUCCESS_MAIN_APP and SUCCESS_SECONDARY_APPS to determine
    which applications to load.

    Returns:
      bool: True if explicit configuration was used, False otherwise.

    Note:
      - SUCCESS_MAIN_APP defines the main application (optional)
      - SUCCESS_SECONDARY_APPS defines secondary applications (optional)
      - At least one must be defined to consider explicit config
    """
    mainApp       = SuccessSystemEnv.get ( "SUCCESS_MAIN_APP", "" ).strip ()
    secondaryApps = SuccessSystemEnv.toList ( "SUCCESS_SECONDARY_APPS" )

    # Verificar si hay configuración explícita
    if not mainApp and not secondaryApps :
      self._logger.log ( "No se encontró configuración explícita (SUCCESS_MAIN_APP y SUCCESS_SECONDARY_APPS vacías).", "DEBUG" )
      return False

    self._logger.log (
      f"Cargando aplicaciones desde configuración explícita: "
      f"MAIN_APP='{mainApp}', SECONDARY_APPS={secondaryApps}.",
      "INFO"
    )

    # Cargar app principal si está definida
    if mainApp :
      self._loadAndRegisterApp ( mainApp, isMain = True )

    # Cargar apps secundarias
    for appName in secondaryApps :
      appName = str ( appName ).strip ()
      if not appName :
        continue

      if appName == mainApp :
        self._logger.log ( f"App secundaria '{appName}' es igual a MAIN_APP, omitiendo para evitar duplicación.", "WARNING" )
        continue

      self._loadAndRegisterApp ( appName, isMain = False )

    return True


  def _tryImplicitLoad ( self ) -> None :
    """
    Attempt to load applications by automatically scanning the directory.

    Scans the SUCCESS_APPS_PATH directory for valid applications
    and loads all found applications.

    Note:
      - Only used if there is no explicit configuration
      - Load order is alphabetical by app name
      - All found apps are treated equally (no priority)
    """
    self._logger.log ( "Intentando carga implícita mediante escaneo del directorio de aplicaciones.", "INFO" )

    discoveredApps = self._scanAppsDirectory ()

    if not discoveredApps :
      self._logger.log ( "No se encontraron aplicaciones válidas en el directorio de aplicaciones.", "DEBUG" )
      return

    self._logger.log (
      f"Auto-descubrimiento: {len ( discoveredApps )} aplicación(es) encontrada(s): {discoveredApps}.",
      "INFO" if len ( discoveredApps ) == 1 else "WARNING"
    )

    if len ( discoveredApps ) > 1 :
      self._logger.log (
        f"⚠️ Múltiples apps descubiertas sin config explícita. "
        f"Orden de carga (alfabético): {discoveredApps}. "
        f"Considere definir SUCCESS_MAIN_APP y SUCCESS_SECONDARY_APPS.",
        "WARNING"
      )

    # Cargar todas las apps descubiertas
    for appName in discoveredApps :
      self._loadAndRegisterApp ( appName, isMain = False )


  def _tryDefaultLoad ( self ) -> None :
    """
    Attempt to load a default application or use placeholder.

    If there is no explicit configuration or discovered apps, attempts
    to load an app named 'success' as fallback. If it fails, uses
    SuccessAppPlaceholder.

    Note:
      - This is the last fallback strategy
      - Only executed if previous strategies loaded nothing
    """
    self._logger.log ( "Intentando cargar aplicación por defecto.", "INFO" )

    defaultAppName = "success"
    appPath        = os.path.join ( self._appsPath, defaultAppName )

    if os.path.isdir ( appPath ) :
      self._logger.log ( f"App por defecto '{defaultAppName}' encontrada, intentando cargar.", "INFO" )
      self._loadAndRegisterApp ( defaultAppName, isMain = True )

    else :
      self._logger.log (
        f"No se encontró aplicación por defecto '{defaultAppName}' y no hay apps cargadas. "
        f"El sistema puede no funcionar correctamente.",
        "WARNING"
      )


  def _scanAppsDirectory ( self ) -> list [ str ] :
    """
    Scan the applications directory for valid apps.

    Traverses the SUCCESS_APPS_PATH directory and validates each
    subdirectory as a potential Success application.

    Returns:
      list[str]: Alphabetically sorted list of valid app names.
                Empty list if no valid apps found.

    Note:
      - Uses SuccessAppValidator to validate each found app
      - Only includes apps that pass all structure validations
    """
    validApps = []

    if not os.path.isdir ( self._appsPath ) :
      self._logger.log ( f"El directorio de aplicaciones '{self._appsPath}' no existe.", "WARNING" )
      return validApps

    self._logger.log ( f"Escaneando directorio '{self._appsPath}' en busca de aplicaciones válidas.", "INFO" )

    for entry in sorted ( os.listdir ( self._appsPath ) ) :
      appPath = os.path.join ( self._appsPath, entry )

      # Debe ser un directorio
      if not os.path.isdir ( appPath ) :
        continue

      # Validar estructura de la aplicación
      if SuccessAppValidator.isValidAppDir ( appPath ) :
        validApps.append ( entry )
        self._logger.log ( f"App '{entry}' válida encontrada en escaneo.", "INFO" )

      else :
        self._logger.log ( f"App '{entry}' encontrada pero no es válida (estructura incompleta).", "WARNING" )

    return validApps


  def _loadAndRegisterApp ( self, appName : str, isMain : bool = False ) -> None :
    """
    Validate, build, and register a specific application.

    Internal method that executes the complete loading flow for an app:
    1. Validate structure (SuccessAppValidator)
    2. Build instance (SuccessAppBuilder)
    3. Register in _loadedApps if successful

    Args:
      appName: Name of the application to load.
      isMain: True if it is the main application (for logging).

    Note:
      - If validation fails, registers error in SuccessSystemState
      - If building fails, registers error in SuccessSystemState
      - Successful apps are added to _loadedApps
    """
    appPath = os.path.join ( self._appsPath, appName )
    appType = "principal" if isMain else "secundaria"

    self._logger.log ( f"Cargando aplicación {appType} '{appName}'...", "INFO" )

    # Validar que el directorio existe
    if not os.path.isdir ( appPath ) :
      self._logger.log ( f"Directorio de la aplicación '{appName}' no existe en '{appPath}'.", "ERROR" )
      SuccessSystemState.addAppOmitida ( appName, "Directorio no encontrado" )
      return

    # Validar estructura de la aplicación
    validator = SuccessAppValidator ( appName, appPath )
    try :
      validator.validate ()
      
    except Exception as e :
      self._logger.log ( f"App '{appName}' no pasó validación: {e}", "ERROR" )
      SuccessSystemState.addAppOmitida ( appName, f"Falló validación: {str ( e )}" )
      return

    # Construir la aplicación
    try :
      builder = SuccessAppBuilder ( appName )
      app     = builder.build ()

      if app is not None :
        SuccessJinja.registerMethods ( app )
        self._loadedApps [ appName ] = app
        SuccessSystemState.addAppCargada ( app )
        self._logger.log ( f"App '{appName}' cargada exitosamente.", "INFO" )

      else :
        self._logger.log ( f"App '{appName}' retornó None durante construcción.", "ERROR" )
        SuccessSystemState.addAppOmitida ( appName, "Construcción retornó None" )

    except Exception as e :
      self._logger.log ( f"App '{appName}' falló durante construcción: {e}", "ERROR" )
      SuccessSystemState.addAppOmitida ( appName, f"Falló construcción: {str ( e )}" )
