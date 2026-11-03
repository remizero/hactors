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
from success.common.base.SuccessClass             import SuccessClass
from success.core.protocol.SuccessProtocolAdapter import SuccessProtocolAdapter
from success.core.protocol.SuccessProtocolFactory import SuccessProtocolFactory
from success.core.SuccessBuildContext             import SuccessBuildContext
from success.engine.infrastructure.SuccessHookCatalog import SuccessHookCatalog

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessEndpointAdapterBuilder ( SuccessClass ) :
  """
  Protocol adapter builder for endpoints.

  Selects and uses the appropriate protocol adapter (view, restful, default)
  to register the endpoint in the corresponding blueprint.

  Attributes:
    __buildContext (SuccessBuildContext): Build context.
    __blueprint (Blueprint): Flask blueprint to register the endpoint.
    __options (dict): Endpoint configuration including protocol.

  Usage:
    adapter = SuccessEndpointAdapterBuilder(ctx, blueprint, options)
    adapter.build()
  """

  __blueprint    : Blueprint           = None
  __buildContext : SuccessBuildContext = None
  __options      : dict                = None


  def __init__ ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, options : dict ) -> None :
    """
    Initialize the adapter builder.

    Args:
      buildContext: Build context with application configuration.
      blueprint: Flask blueprint to register the endpoint.
      options: Dictionary with endpoint configuration (protocol, action, etc.).
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self.__blueprint    = blueprint
    self.__options      = options


  def build ( self ) -> None :
    """
    Select and execute the appropriate protocol adapter.

    Gets the adapter from SuccessProtocolFactory according to the
    configured protocol and executes it to register the endpoint.
    Executes before/after hooks 'adapter:build:endpoint'.
    """
    self._logger.log ( f"Seleccionando el EndpointAdapter", "INFO" )

    self.__buildContext._hooks.execute ( when = "before", action = SuccessHookCatalog.BUILD_ENDPOINT_ADAPTER_REGISTER )

    adapter = SuccessProtocolFactory.getProtocolAdapter ( self.__options.get ( "protocol" ) )
    adapter.register ( self.__buildContext, self.__blueprint, self.__options )

    self.__buildContext._hooks.execute ( when = "after", action = SuccessHookCatalog.BUILD_ENDPOINT_ADAPTER_REGISTER )

    self._logger.log ( f"EndpointAdapter seleccionado", "INFO" )
