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
from flask         import Blueprint
from flask_restful import Api

# Success Libraries / Librerías Success
from success.core.protocol.SuccessProtocolAdapter               import SuccessProtocolAdapter
from success.core.protocol.options.SuccessRestfulOptionsBuilder import SuccessRestfulOptionsBuilder
from success.core.SuccessBuildContext                           import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessRestProtocolAdapter ( SuccessProtocolAdapter ) :
  """
  Protocol adapter for RESTful type endpoints.

  Registers endpoints that expose REST resources using the 'restful' protocol.
  Each endpoint is registered as a Flask-RESTful resource in the blueprint.

  Usage:
    adapter = SuccessRestProtocolAdapter()
    adapter.register(ctx, blueprint, options)
  """


  def __init__ ( self ) -> None :
    """
    Initialize the RESTful protocol adapter.
    """
    super ().__init__ ()


  def register ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, options : dict ) -> None :
    """
    Register a RESTful type endpoint in the blueprint.

    Builds the endpoint options using SuccessRestfulOptionsBuilder
    and registers the resource in the blueprint's RESTful API.

    Args:
        buildContext: Build context with application configuration.
        blueprint: Flask blueprint where the endpoint will be registered.
        options: Dictionary with endpoint configuration
                (endpoint_id, resource, urls, etc.).

    Example:
      options = {
        "endpoint_id": "users_api",
        "resource": "services/rest/UserResource",
        "urls": "/api/users",
        "endpoint": "users"
      }
      adapter.register(ctx, blueprint, options)
    """
    self._logger.log ( f"Creando endpoint {options.get ( "endpoint_id" )}", "INFO" )

    optionsBuilder    = SuccessRestfulOptionsBuilder ( buildContext, options )
    kwargs            = optionsBuilder.build ()
    api               = Api ( blueprint )
    addResourceKwargs = {
      "endpoint" : kwargs.get ( "endpoint" )
    }
    if kwargs.get ( "host" ) :
      addResourceKwargs [ "host" ] = kwargs.get ( "host" )

    api.add_resource (
      kwargs.get ( "resource" ),
      kwargs.get ( "urls" ),
      **addResourceKwargs
    )

    self._logger.log ( f"Creado endpoint {options.get ( "endpoint_id" )}", "INFO" )
