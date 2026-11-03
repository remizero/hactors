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
from flask  import Flask
from typing import Optional
import importlib
import os
import sys

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                           import SuccessClass
from success.common.types.WSGIApplication                       import WSGIApplication
from success.core.app.SuccessAppValidator                       import SuccessAppValidator
from success.core.app.SuccessFlaskOptionsBuilder                import SuccessFlaskOptionsBuilder
from success.engine.infrastructure.SuccessHookManager           import SuccessHookManager
from success.common.infra.config.SuccessConfig                  import SuccessConfig
from success.core.extension.SuccessExtensionsLoader             import SuccessExtensionsLoader
from success.core.blueprint.SuccessBlueprintsLoader             import SuccessBlueprintsLoader
from success.common.infra.config.SuccessSystemEnv               import SuccessSystemEnv
from success.core.SuccessSystemState                            import SuccessSystemState
from success.core.SuccessContext                                import SuccessContext
from success.engine.context.middleware.RequestContextMiddleware import RequestContextMiddleware
from success.core.extension.SuccessExtensionsDiscoverer         import SuccessExtensionsDiscoverer
from success.core.SuccessBuildContext                           import SuccessBuildContext
from success.engine.infrastructure.SuccessHookCatalog           import SuccessHookCatalog

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAppBuilder ( SuccessClass ) :
  """
  Main builder for Success framework applications.

  Responsible for building and fully configuring a Flask application
  within the Success ecosystem. Manages the entire build lifecycle
  from initial validation to blueprint and extension registration.

  Purpose:
  ----------
  SuccessAppBuilder orchestrates the application building process:
  1. Validates application structure and required files
  2. Creates build context (SuccessBuildContext)
  3. Initializes Flask instance with appropriate configuration
  4. Loads custom or standard configuration
  5. Registers basic and custom extensions
  6. Loads and registers all blueprints
  7. Configures request context middleware

  Build flow:
  ----------------------
  SuccessAppBuilder
      ↓
  SuccessAppValidator (validates structure)
      ↓
  SuccessBuildContext (creates context)
      ↓
  SuccessFlaskOptionsBuilder (configures Flask)
      ↓
  SuccessConfig (loads configuration)
      ↓
  SuccessExtensionsLoader (basic extensions)
      ↓
  SuccessExtensionsDiscoverer (custom extensions)
      ↓
  SuccessBlueprintsLoader (registers blueprints)

  Attributes:
    __app (Flask): Built Flask application instance.
    __appName (str): Unique application name.
    __appPath (str): Absolute path to application directory.
    __buildContext (SuccessBuildContext): Current build context.
    __config (SuccessConfig): Loaded application configuration.

  Usage:
    # Build a Success application
    builder = SuccessAppBuilder('synthetos')
    app = builder.build()

    # The application is ready to use
    # builder.loadExtensions() already called internally
    # builder.loadBlueprints() already called internally

  Note:
    - The builder automatically configures sys.path for app imports
    - Uses SuccessSystemEnv to get SUCCESS_APPS_PATH
    - Registers the application in SuccessContext for global access
    - Configures RequestContextMiddleware for request management
  """

  __app          : Flask               = None
  __appName      : str                 = None
  __appPath      : str                 = None
  __buildContext : SuccessBuildContext = None
  __config       : SuccessConfig       = None


  def __init__ ( self, appName : str ) -> None :
    """
    Initialize the builder for a specific application.

    Configures base paths and prepares the environment for application
    building. Adds application paths to sys.path to allow direct imports.

    Args:
      appName (str): Unique name of the application to build.
                    Must correspond to an existing directory
                    under SUCCESS_APPS_PATH.

    Raises:
      FileNotFoundError: If the application path does not exist.

    Example:
      # Initialize builder for application 'synthetos'
      builder = SuccessAppBuilder('synthetos')
      # builder.__appPath → '/home/user/proyecto/apps/synthetos'

    Note:
      - Adds SUCCESS_APPS_PATH to sys.path for imports like
        '<app>.services...' (e.g., 'llogos.services.view.Action')
      - Adds app_path to sys.path for legacy compatibility
        with imports like 'services...'
    """
    super ().__init__ ()
    self.__appName   = appName
    try :
      appsBasePath   = os.path.abspath ( SuccessSystemEnv.get ( "SUCCESS_APPS_PATH", "apps" ) )
      self.__appPath = os.path.abspath ( os.path.join ( appsBasePath, self.__appName ) )

      if not os.path.isdir ( self.__appPath ) :
        raise FileNotFoundError

      # Permite imports estilo "<app>.services..." (ej: llogos.services...)
      if appsBasePath not in sys.path :
        sys.path.insert ( 0, appsBasePath )

      # Compatibilidad legacy para imports estilo "services..."
      if self.__appPath not in sys.path :
        sys.path.insert ( 0, self.__appPath )

    except Exception as e :
      self._logger.log ( f"La ruta a la aplicación {self.__appName} no existe o no puede ser encontrada.", "ERROR" )


  def build ( self ) -> WSGIApplication :
    """
    Build and fully configure the Flask application.

    Executes the entire build flow in the correct order:
    1. Validates application with SuccessAppValidator
    2. Creates SuccessBuildContext with configuration
    3. Builds base Flask instance
    4. Registers in SuccessContext and SuccessSystemState
    5. Configures RequestContextMiddleware
    6. Loads configuration, extensions, and blueprints

    Returns:
      WSGIApplication: The fully configured Flask application
                      ready to be executed.

    Example:
      builder = SuccessAppBuilder('synthetos')
      app = builder.build()
      # app is ready to use with Werkzeug/Flask server

    Note:
      - The method registers the application name in
        SuccessContext as 'current_app_bootstrapping' during
        building for debugging and logging.
      - After build(), the application has:
        - All extensions registered
        - All blueprints loaded
        - Full configuration applied
        - Context middleware configured
    """
    self._logger.log ( f"Iniciando construcción de la aplicación {self.__appName}.", "INFO" )

    validator = SuccessAppValidator ( self.__appName, self.__appPath )
    validator.validate ()

    self.__buildContext = SuccessBuildContext ( self.__appName, self.__appPath )

    self.__buildApp ()

    SuccessContext ().setSuccessValue ( "current_app", self.__appName )
    SuccessContext ().setApp ( self.__app )
    SuccessSystemState.addAppCargada ( self.__app )
    RequestContextMiddleware ( self.__app, self.__appName )
    # SuccessContext ().setAppModule ( module )
    # SuccessContext ().setAppLogger ( self._logger )

    self.loadConfig ()

    self.loadExtensions () # Revisar si esto está creando las extensiones adecuadamente
    self.loadCustomExtensions ()

    self.loadBlueprints ()

    SuccessContext ().setSuccessValue ( "current_app", None )

    self._logger.log ( f"Finalizada la construcción de la aplicación {self.__appName} exitosamente.", "INFO" )

    return self.__app


  def __buildApp ( self ) -> None :
    """
    Create the base Flask instance with appropriate configuration.

    Uses SuccessFlaskOptionsBuilder to build the Flask parameters
    dictionary according to the application mode (singleapp/multiapp)
    and subdomain/host matching configurations.

    Note:
      - Registers the Flask instance in the build context
      - The instance is stored in __app for later use
    """
    self._logger.log ( f"Iniciando creación de la aplicación {self.__appName}.", "INFO" )

    optionsBuilder = SuccessFlaskOptionsBuilder ( self.__buildContext )
    flask_kwargs   = optionsBuilder.build ()
    self.__app     = Flask ( **flask_kwargs )

    self.__buildContext.setApp ( self.__app )

    self._logger.log ( f"Finalizada la creación de la aplicación {self.__appName} exitosamente.", "INFO" )


  def loadBlueprints ( self ) -> None :
    """
    Load and register all blueprints defined in the application.

    Uses SuccessBlueprintsLoader to read blueprints.json and register
    each defined blueprint with its specific configuration.

    Note:
      - Blueprints are defined in {app_path}/blueprints.json
      - Each blueprint can have its own endpoints defined
        in endpoints.json
    """
    blueprints = SuccessBlueprintsLoader ( self.__buildContext )
    blueprints.load ()


  def loadConfig ( self ) -> None :
    """
    Load the application configuration.

    Supports custom configuration via SUCCESS_CUSTOM_CONFIG_CLASS
    or uses SuccessConfig by default. Executes hooks before and after
    configuration loading to allow extensions.

    The loading process:
    1. Executes 'before:config_extend' hook
    2. Checks for custom configuration
    3. Loads standard or custom configuration
    4. Applies configuration to Flask application
    5. Executes 'after:config_extend' hook
    6. Configures PROPAGATE_EXCEPTIONS

    Note:
      - SUCCESS_CUSTOM_CONFIG_CLASS must be a full class path
        (e.g., 'myapp.config.CustomConfig')
      - Custom configuration must inherit from SuccessConfig
        or be compatible with Flask config
    """
    self._logger.log ( f"Iniciando carga de configuración para la aplicación {self.__appName}.", "INFO" )

    self.__buildContext._hooks.execute ( when = "before", action = SuccessHookCatalog.BUILD_APP_CONFIG_LOAD )

    custom_config_class_path = self.__buildContext._appEnv.get ( "SUCCESS_CUSTOM_CONFIG_CLASS" )
    
    # Solo cargar config personalizada si el valor es un string no vacío
    if isinstance ( custom_config_class_path, str ) and custom_config_class_path.strip () :
      self._logger.log ( f"Cargando configuración personalizada de la aplicación...", "INFO" )
      module_name, class_name  = custom_config_class_path.rsplit ( ".", 1 )
      module                   = importlib.import_module ( module_name )
      self.__config            = getattr ( module, class_name )

    else :
      self._logger.log ( "Cargando configuración estandar de la aplicación...", "INFO" )
      self.__config = SuccessConfig ( self.__buildContext._appEnv )

    self.__app.config.from_object ( self.__config )

    self.__buildContext._hooks.execute ( when = "after", action = SuccessHookCatalog.BUILD_APP_CONFIG_LOAD )

    self.__app.config [ "PROPAGATE_EXCEPTIONS" ] = True

    self._logger.log ( f"Finalizada la carga de configuración para la aplicación {self.__appName} exitosamente...", "INFO" )


  def loadCustomExtensions ( self ) -> None :
    """
    Load custom extensions defined by the application.

    Uses SuccessExtensionsDiscoverer to discover and load
    extensions defined in the application's extensions.json.

    Note:
      - Custom extensions are defined in {app_path}/extensions.json
      - Each extension must implement the SuccessExtension interface
      - Extensions are loaded after basic extensions
    """
    loader = SuccessExtensionsDiscoverer ( self.__buildContext )
    loader.discover ()


  def loadExtensions ( self ) -> None :
    """
    Load basic extensions of the Success framework.

    Uses SuccessExtensionsLoader to load all supported
    extensions that are enabled via SUCCESS_EXTENSION_* variables.

    Supported extensions:
    - SUCCESS_EXTENSION_ADMIN (SuccessAdminExtension)
    - SUCCESS_EXTENSION_CORS (SuccessCorsExtension)
    - SUCCESS_EXTENSION_JWT (SuccessJwtExtension)
    - SUCCESS_EXTENSION_LOGGER (SuccessLoginExtension)
    - SUCCESS_EXTENSION_MARSHMALLOW (SuccessMarshmallowExtension)
    - SUCCESS_EXTENSION_MIGRATE (SuccessMigrateExtension)
    - SUCCESS_EXTENSION_REDIS (SuccessRedisExtension)
    - SUCCESS_EXTENSION_SESSION (SuccessSessionExtension)
    - SUCCESS_EXTENSION_SQLALCHEMY (SuccessDatabaseExtension)
    - And others...

    Note:
      - Extensions are loaded before custom extensions
      - Each extension checks its enablement flag before loading
    """
    loader = SuccessExtensionsLoader ( self.__buildContext )
    loader.load ()
