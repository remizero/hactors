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
from flask  import Blueprint

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                    import SuccessClass
from success.core.endpoint.SuccessEndpointAdapterBuilder import SuccessEndpointAdapterBuilder
from success.core.SuccessBuildContext                    import SuccessBuildContext
from success.engine.infrastructure.SuccessHookCatalog    import SuccessHookCatalog

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessEndpointBuilder ( SuccessClass ) :
  """
  Individual endpoint builder.

  Builds a specific endpoint based on its JSON definition,
  executing hooks before and after building.

  Attributes:
      __buildContext (SuccessBuildContext): Build context.
      __blueprint (Blueprint): Flask blueprint the endpoint belongs to.
      __options (dict): Specific endpoint configuration.

  Usage:
      builder = SuccessEndpointBuilder(ctx, blueprint, endpoint_def)
      builder.build()
  """

  __blueprint    : Blueprint           = None
  __buildContext : SuccessBuildContext = None
  __options      : dict                = None


  def __init__ ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, options : dict ) -> None :
    """
    Initialize the endpoint builder.

    Args:
        buildContext: Build context with application configuration.
        blueprint: Flask blueprint to register the endpoint.
        options: Dictionary with endpoint configuration (rule, action, etc.).
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self.__blueprint    = blueprint
    self.__options      = options


  def build ( self ) :
    """
    Build and register the endpoint in the blueprint.

    Executes before/after 'build:endpoint' hooks and delegates building
    to SuccessEndpointAdapterBuilder according to the configured protocol.
    """
    self._logger.log ( f"Iniciando la creación del endpoint {self.__options.get ( "endpoint_id" )}", "INFO" )

    self.__buildContext._hooks.execute ( when = "before", action = SuccessHookCatalog.BUILD_ENDPOINT_BUILDER_CREATE )

    adapter = SuccessEndpointAdapterBuilder ( self.__buildContext, self.__blueprint, self.__options )
    adapter.build ()

    self.__buildContext._hooks.execute ( when = "after", action = SuccessHookCatalog.BUILD_ENDPOINT_BUILDER_CREATE )

    self._logger.log ( f"Terminada la creación del endpoint {self.__options.get ( "endpoint_id" )}", "INFO" )
