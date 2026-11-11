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
from flask                          import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                  import SuccessClass
from success.common.infra.config.SuccessSystemEnv      import SuccessSystemEnv
from success.common.tools.SuccessAppPlaceholderFactory import SuccessAppPlaceholderFactory
from success.core.SuccessSystemState                   import SuccessSystemState
from success.core.app.SuccessAppLoader                 import SuccessAppLoader
from success.core.app.SuccessPathDispatcher            import SuccessPathDispatcher
from success.core.app.SuccessSubdomainDispatcher       import SuccessSubdomainDispatcher

# Preconditions / Precondiciones


class SuccessDispatcherFactory ( SuccessClass ) :
  """
  Application dispatcher factory for multiApp mode.

  Creates and configures the routing system for multiple applications
  according to the configured mode (path, subdomain, standard).

  Purpose:
  ----------
  SuccessDispatcherFactory is responsible for:
  - Loading the main application and secondary applications
  - Selecting the dispatch strategy according to SUCCESS_APP_MODE
  - Creating the DispatcherMiddleware or specific strategy

  Supported modes:
  - path: Dispatch based on route prefixes (/app1, /app2)
  - subdomain: Dispatch based on subdomains (app1.domain.com)
  - standard: Standard dispatch with DispatcherMiddleware

  Usage:
  ------
  factory = SuccessDispatcherFactory()
  dispatcher = factory.build()
  # dispatcher is a WSGI application that routes to multiple apps

  Attributes:
    _appMode (str): Configured dispatch mode (path/subdomain/standard).
    _mainApp (str): Name of the main application.
    _secondaries (list): List of secondary applications to load.

  Note:
    - SUCCESS_APP_MODE determines the routing strategy
    - SUCCESS_MAIN_APP defines the root application
    - SUCCESS_SECONDARY_APPS are additional applications
  """

  _appMode     : str  = None
  _mainApp     : str  = None
  _secondaries : list = []


  def __init__ ( self ) -> None :
    """
    Initialize the dispatcher factory by reading environment configuration.

    Reads SUCCESS_APP_MODE, SUCCESS_MAIN_APP, and SUCCESS_SECONDARY_APPS
    environment variables to configure dispatcher behavior.

    Note:
      SUCCESS_APP_MODE is the current variable.
      SUCCESS_APP_DOMAIN remains as deprecated fallback for compatibility.
    """
    super ().__init__ ()
    self._appMode     = SuccessSystemEnv.get ( "SUCCESS_APP_MODE", SuccessSystemEnv.get ( "SUCCESS_APP_DOMAIN", "standard" ) ).strip ().lower ()
    self._mainApp     = SuccessSystemEnv.get ( "SUCCESS_MAIN_APP", "success" ).strip ().lower ()
    self._secondaries = SuccessSystemEnv.toList ( "SUCCESS_SECONDARY_APPS" )
    self._logger.log ( f"Cargando sistema de enrutamiento multiApp, SUCCESS_APP_MODE={self._appMode}.", "INFO" )


  def build ( self ) :
    """
    Build and return the configured application dispatcher.

    Loads applications and selects the dispatch strategy according to
    the configured mode (path, subdomain, standard).

    Returns:
      DispatcherMiddleware or specific dispatch strategy.

    Raises:
      RuntimeError: If main app cannot be loaded and
                    SUCCESS_ALLOW_NO_MAIN_APP=False.
    """
    rootApp, secondaryApps = self._loadApps ()

    if self._appMode == "path" :
      self._logger.log ( "Cargando sistema Success en mode=path.", "INFO" )
      return SuccessPathDispatcher ( rootApp, secondaryApps )

    if self._appMode == "subdomain" :
      self._logger.log ( "Cargando sistema Success en mode=subdomain.", "INFO" )

      subdomainApps                         = dict ( secondaryApps )
      subdomainApps [ f"/{self._mainApp}" ] = rootApp
      subdomainApps [ self._mainApp ]       = rootApp
      # Permite resolver dominio raíz (sin subdominio explícito) hacia la app principal.
      subdomainApps [ "/" ]                 = rootApp
      subdomainApps [ "" ]                  = rootApp

      return SuccessSubdomainDispatcher (
        SuccessSystemEnv.get ( "SERVER_NAME", "success.local" ).strip ().lower (),
        subdomainApps
      )

    self._logger.log ( "Cargando sistema Success en mode=standard.", "INFO" )

    return DispatcherMiddleware ( rootApp, secondaryApps )


  def _loadApps ( self ) -> tuple [ Flask, dict [ str, Flask ] ] :
    """
    Load the main application and secondary applications.

    Internal method that loads all configured applications from
    the apps/ directory using SuccessAppLoader.

    Returns:
      tuple[Flask, dict[str, Flask]]: Tuple with main app and
          a dictionary of secondary apps mapped by route.

    Raises:
      RuntimeError: If main app cannot be loaded and
                    SUCCESS_ALLOW_NO_MAIN_APP=False, or if in
                    non-development environment with ALLOW_NO_MAIN_APP.

    Note:
      - Failed secondary apps are registered in SuccessSystemState
      - In development with SUCCESS_ALLOW_NO_MAIN_APP=True, uses placeholder
    """
    # Usar SuccessAppLoader para cargar todas las apps
    # Retorna: {'main': Flask | None, 'secondaries': dict[str, Flask]}
    loader       = SuccessAppLoader ()
    loadedResult = loader.load ()
    rootApp      = loadedResult [ 'main' ]

    if rootApp is None :
      SuccessSystemState.addAppOmitida ( self._mainApp, "No se pudo cargar app principal" )
      
      if SuccessSystemEnv.isTrue ( "SUCCESS_ALLOW_NO_MAIN_APP" ) :
        if SuccessSystemEnv.get ( "APP_ENV", "development" ) != "development" :
          raise RuntimeError ( "'SUCCESS_ALLOW_NO_MAIN_APP' solo permitido en development." )

        self._logger.log ( "⚠️ Usando SuccessAppPlaceholder como raíz.", "WARNING" )
        rootApp = SuccessAppPlaceholderFactory.build ()

      else :
        raise RuntimeError ( f"No se pudo cargar la app principal {self._mainApp} y SUCCESS_ALLOW_NO_MAIN_APP={SuccessSystemEnv.get ( 'SUCCESS_ALLOW_NO_MAIN_APP' )}." )

    # Convertir secondaries de dict[nombre, Flask] a dict[ruta, Flask]
    secondaryApps : dict [ str, Flask ] = {}
    for appName, app in loadedResult [ 'secondaries' ].items () :
      secondaryApps [ f"/{appName}" ] = app

    return rootApp, secondaryApps
