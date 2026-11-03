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
from flask import Blueprint

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                      import SuccessClass
from success.core.blueprint.SuccessBlueprintOptionsBuilder import SuccessBlueprintOptionsBuilder
from success.common.reflection.SuccessModuleMetadata       import SuccessModuleMetadata
from success.core.endpoint.SuccessEndpointsLoader          import SuccessEndpointsLoader
from success.core.SuccessBuildContext                      import SuccessBuildContext
from success.engine.infrastructure.SuccessHookCatalog      import SuccessHookCatalog

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessBlueprintBuilder ( SuccessClass ) :
  """
  Flask blueprint builder for the Success framework.

  Builds and configures Flask blueprints based on the application's
  JSON definition, registering associated endpoints.

  Purpose:
  ----------
  SuccessBlueprintBuilder is responsible for:
  - Building blueprint options from JSON configuration
  - Creating the Flask Blueprint instance
  - Loading and registering blueprint endpoints
  - Executing hooks before/after building

  Usage:
  ------
  ctx = SuccessBuildContext.from_app('myapp', '/apps/myapp')
  builder = SuccessBlueprintBuilder(ctx, blueprint_def)
  blueprint = builder.build()
  app.register_blueprint(blueprint)

  Attributes:
      __buildContext (SuccessBuildContext): Build context.
      __options (dict): Blueprint configuration from JSON.

  Note:
    - Each blueprint represents an endpoint module
    - Endpoints are loaded from endpoints.json
    - 'before/after build:blueprint' hooks are executed
  """

  __buildContext : SuccessBuildContext = None
  __options      : dict                = None


  def __init__ ( self, buildContext : SuccessBuildContext, options : dict ) -> None :
    """
    Initialize the blueprint builder.

    Args:
        buildContext: Build context with application configuration.
        options: Dictionary with blueprint configuration (id, module, path).
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self.__options      = options


  def build ( self ) -> Blueprint :
    """
    Build and return a configured Flask blueprint.

    Creates the blueprint using SuccessBlueprintOptionsBuilder, executes hooks,
    and loads associated endpoints from endpoints.json.

    Returns:
        Blueprint: Flask blueprint instance with registered endpoints.

    Note:
        - Executes 'before/after build:blueprint' hooks
        - Endpoints are loaded from SuccessEndpointsLoader
    """
    self._logger.log ( f"Iniciando la creación del blueprint {self.__options.get ( "id" )}", "INFO" )

    optionsBuilder = SuccessBlueprintOptionsBuilder ( SuccessModuleMetadata.getAppNameFromPath ( self.__buildContext._appPath ), self.__options )
    kwargs         = optionsBuilder.build ()

    if self.__buildContext._hooks :
      self.__buildContext._hooks.execute ( when = "before", action = SuccessHookCatalog.BUILD_BLUEPRINT_BUILDER_CREATE )

    bp        = Blueprint ( **kwargs )
    endpoints = SuccessEndpointsLoader ( self.__buildContext, bp, self.__options.get ( "id" ) )
    endpoints.load ()

    if self.__buildContext._hooks :
      self.__buildContext._hooks.execute ( when = "after", action = SuccessHookCatalog.BUILD_BLUEPRINT_BUILDER_CREATE )

    self._logger.log ( f"Terminada la creación del blueprint {kwargs.get ( "name" )}", "INFO" )

    return bp
