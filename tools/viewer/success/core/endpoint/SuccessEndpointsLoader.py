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
import os

# Success Libraries / Librerías Success
from success.common.base.SuccessClass             import SuccessClass
from success.common.tools.SuccessFile             import SuccessFile
from success.core.endpoint.SuccessEndpointBuilder import SuccessEndpointBuilder
from success.core.SuccessBuildContext             import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessEndpointsLoader ( SuccessClass ) :
  """
  Endpoint loader from endpoints.json file.

  Reads endpoint definitions from the application's JSON file
  and builds each endpoint using SuccessEndpointBuilder.

  Attributes:
    __buildContext (SuccessBuildContext): Build context with
                                          application configuration.
    __blueprint (Blueprint): Flask blueprint the endpoints belong to.
    __blueprint_id (str): Unique blueprint identifier.
    __endpoints (list): List of endpoint definitions loaded from JSON.

  Usage:
    ctx = SuccessBuildContext.from_app('synthetos', '/apps/synthetos')
    loader = SuccessEndpointsLoader(ctx, blueprint, 'main')
    loader.load()
  """

  __blueprint    : Blueprint           = None
  __blueprint_id : str                 = None
  __buildContext : SuccessBuildContext = None
  __endpoints                          = None


  def __init__ ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, blueprint_id : str ) -> None :
    """
    Initialize the endpoint loader.

    Args:
      buildContext: Build context with application configuration.
      blueprint: Flask blueprint to register the endpoints.
      blueprint_id: Blueprint identifier to filter endpoints.
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self.__blueprint    = blueprint
    self.__blueprint_id = blueprint_id
    self.__endpoints    = SuccessFile.loadAppJson ( os.path.join ( self.__buildContext._appPath, "endpoints.json" ) )

    if not isinstance ( self.__endpoints, list ) :
      self._logger.log ( "endpoints.json no existe o no es una lista válida. Se omite carga de endpoints.", "WARNING" )
      self.__endpoints = []


  def load ( self ) :
    """
    Load and register all endpoints for the current blueprint.

    Iterates over endpoints.json definitions, filters by blueprint_id,
    and builds each endpoint using SuccessEndpointBuilder.
    """
    self._logger.log ( "Iniciando carga de endpoints...", "INFO" )

    for epDef in self.__endpoints :

      if epDef.get ( "blueprint_id" ) != self.__blueprint_id :
        continue

      builder = SuccessEndpointBuilder (
        buildContext = self.__buildContext,
        blueprint    = self.__blueprint,
        options      = epDef
      )
      builder.build ()

    self._logger.log ( "Carga de endpoints finalizada.", "INFO" )
