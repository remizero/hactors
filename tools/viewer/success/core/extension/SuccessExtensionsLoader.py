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
import importlib

from flask  import Flask
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type


# Success Libraries / Librerías Success
from success.common.base.SuccessClass                      import SuccessClass
from success.common.infra.config.SuccessConfig             import SuccessConfig
from success.core.SuccessContext                           import SuccessContext
from success.core.extension.SuccessExtensionBuilder        import SuccessExtensionBuilder
from success.engine.infrastructure.SuccessHookManager      import SuccessHookManager
from success.core.SuccessBuildContext                      import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones

# Cada extensión arrastra su propia dependencia de Flask, así que ninguna se
# importa aquí: se resuelve en el momento de construirla y solo si su flag la
# enciende. Importarlas a nivel de módulo obligaría a instalar las quince
# dependencias aunque la aplicación no use ninguna.
EXTENSION_MODULE  : str            = "success.engine.extensions"
EXTENSION_CLASSES : Dict [ str, str ] = {
  "SUCCESS_EXTENSION_ADMIN"       : "SuccessAdminExtension",
  "SUCCESS_EXTENSION_APSCHEDULER" : "SuccessAPSchedulerExtension",
  "SUCCESS_EXTENSION_BABEL"       : "SuccessBabelExtension",
  "SUCCESS_EXTENSION_CACHE"       : "SuccessCacheExtension",
  "SUCCESS_EXTENSION_CORS"        : "SuccessCorsExtension",
  "SUCCESS_EXTENSION_SQLALCHEMY"  : "SuccessDatabaseExtension",
  "SUCCESS_EXTENSION_EMAIL"       : "SuccessEmailExtension",
  "SUCCESS_EXTENSION_JWT"         : "SuccessJwtExtension",
  "SUCCESS_EXTENSION_LIMITER"     : "SuccessLimiterExtension",
  "SUCCESS_EXTENSION_LOGGIN"      : "SuccessLoginExtension",
  "SUCCESS_EXTENSION_MARSHMALLOW" : "SuccessMarshmallowExtension",
  "SUCCESS_EXTENSION_MIGRATE"     : "SuccessMigrateExtension",
  "SUCCESS_EXTENSION_REDIS"       : "SuccessRedisExtension",
  "SUCCESS_EXTENSION_SECURITY"    : "SuccessSecurityExtension",
  "SUCCESS_EXTENSION_SESSION"     : "SuccessSessionExtension"
}


class SuccessExtensionsLoader ( SuccessClass ) :
  """
  Standard extension loader for the Success framework.

  Loads and registers built-in framework extensions (Admin, CORS,
  Database, JWT, etc.) based on environment configuration.

  Purpose:
  ----------
  SuccessExtensionsLoader is responsible for:
  - Maintaining registry of available standard extensions
  - Iterating over extensions and loading enabled ones
  - Registering each extension in SuccessContext
  - Executing hooks during registration

  Supported extensions:
  -----------------------
  - SUCCESS_EXTENSION_ADMIN: Administration
  - SUCCESS_EXTENSION_APSCHEDULER: Scheduled tasks
  - SUCCESS_EXTENSION_BABEL: Internationalization
  - SUCCESS_EXTENSION_CACHE: Caching
  - SUCCESS_EXTENSION_CORS: Cross-Origin Resource Sharing
  - SUCCESS_EXTENSION_SQLALCHEMY: Database
  - SUCCESS_EXTENSION_EMAIL: Email sending
  - SUCCESS_EXTENSION_JWT: JWT authentication
  - SUCCESS_EXTENSION_LIMITER: Rate limiting
  - SUCCESS_EXTENSION_LOGGIN: Login/authentication
  - SUCCESS_EXTENSION_MARSHMALLOW: Serialization
  - SUCCESS_EXTENSION_MIGRATE: DB migrations
  - SUCCESS_EXTENSION_REDIS: Redis caching
  - SUCCESS_EXTENSION_SECURITY: Security
  - SUCCESS_EXTENSION_SESSION: Session management

  Usage:
  ------
  ctx = SuccessBuildContext.from_app('myapp', '/apps/myapp')
  loader = SuccessExtensionsLoader(ctx)
  extensions = loader.load()  # Load enabled extensions

  Attributes:
      __extensions (list): List of tuples (env_var, extension_class).
      __instances (dict): Dictionary of created instances.
      __context (SuccessContext): Application context.
      __builder (SuccessExtensionBuilder): Extension builder.
      __buildContext (SuccessBuildContext): Build context.

  Note:
    - Each extension loads only if its env variable is 'true'
    - Extensions registered with multiple aliases in context
  """

  # __app        : Flask              = None
  # __config     : SuccessConfig      = None
  # __hooks      : SuccessHookManager = None
  __extensions   : list                    = []
  __instances    : dict                    = {}
  __context      : SuccessContext          = None
  __builder      : SuccessExtensionBuilder = None
  __buildContext : SuccessBuildContext     = None


  def __init__ ( self, buildContext : SuccessBuildContext ) -> None :
    """
    Initialize the extension loader.

    Args:
        buildContext: Build context with application configuration.

    Note:
        The list of standard extensions is defined internally.
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self.__builder      = SuccessExtensionBuilder ( self.__buildContext )
    self.__extensions   = list ( EXTENSION_CLASSES.keys () )


  def getExtension ( self, name : str ) -> Optional [ Type ] :
    """
    Get extension class by name or environment variable.

    Args:
        name: Extension name or environment variable
             (e.g., 'SUCCESS_EXTENSION_CORS' or 'SuccessCorsExtension').

    Returns:
        Optional[Type]: Extension class if exists, None otherwise.

    Example:
        loader.getExtension('SUCCESS_EXTENSION_CORS')  # → SuccessCorsExtension
        loader.getExtension('SuccessCorsExtension')    # → SuccessCorsExtension
    """
    if name in EXTENSION_CLASSES :
      return self._resolve ( name )

    for envVar, className in EXTENSION_CLASSES.items () :
      if className == name :
        return self._resolve ( envVar )

    return None


  def _resolve ( self, envVar : str ) -> Optional [ Type ] :
    """
    Import the extension class behind an environment variable, on demand.

    Args:
        envVar: Environment variable name (e.g., 'SUCCESS_EXTENSION_CORS').

    Returns:
        Optional[Type]: The extension class, or None if envVar is unknown.
    """
    className = EXTENSION_CLASSES.get ( envVar )
    if not className :
      return None

    return getattr ( importlib.import_module ( f"{EXTENSION_MODULE}.{className}" ), className )


  def load ( self ) -> List [ Tuple [ str, Type ] ] :
    """
    Load and register all enabled extensions.

    Iterates over the list of standard extensions, checks if they are
    enabled via SuccessExtensionBuilder, and registers them in
    SuccessContext.

    Returns:
        List[Tuple[str, Type]]: List of tuples (env_var, extension_class)
            of the standard extensions that were enabled and registered.

    Note:
        - Only enabled extensions are imported, instantiated and registered
        - 'before/after extension_register' hooks are executed
        - Each extension is registered with two aliases in the context
    """
    self._logger.log ( f"Iniciando carga de extensiones básicas de la aplicación {self.__buildContext._appName}.", "INFO" )

    loaded : List [ Tuple [ str, Type ] ] = []

    for env_var in self.__extensions :
      if not self.__builder.isEnabled ( env_var ) :
        continue

      ExtensionClass = self._resolve ( env_var )
      instance       = self.__builder.build ( env_var, ExtensionClass )
      if not instance :
        continue

      self.__buildContext.setExtension ( ExtensionClass.__name__, instance )
      self.__instances [ env_var ] = instance
      loaded.append ( ( env_var, ExtensionClass ) )

      self._logger.log ( f"Extensión [{ExtensionClass.__name__}] registrada.", "INFO" )

    self._logger.log ( f"Finalizando la carga de extensiones básicas de la aplicación {self.__buildContext._appName}.", "INFO" )

    return loaded
