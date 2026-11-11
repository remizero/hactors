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
from flask   import Flask
from pathlib import Path
import os

# Success Libraries / Librerías Success
from success.common.base.SuccessClass               import SuccessClass
from success.common.tools.SuccessFile               import SuccessFile
from success.core.blueprint.SuccessBlueprintBuilder import SuccessBlueprintBuilder
from success.core.SuccessBuildContext               import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessBlueprintsLoader ( SuccessClass ) :
  """
  Blueprint loader from blueprints.json file.

  Reads blueprint definitions from the application's JSON file
  and builds each blueprint using SuccessBlueprintBuilder.

  Purpose:
  ----------
  SuccessBlueprintsLoader is responsible for:
  - Loading blueprint definitions from blueprints.json
  - Iterating over each definition and building the blueprint
  - Registering blueprints in the Flask application

  Usage:
  ------
  ctx = SuccessBuildContext.from_app('myapp', '/apps/myapp')
  loader = SuccessBlueprintsLoader(ctx)
  loader.load()  # Registers all blueprints in ctx.getApp()

  Attributes:
    __blueprints (list): List of blueprint definitions from JSON.
    __buildContext (SuccessBuildContext): Build context.

  Note:
    - Blueprints are defined in blueprints.json
    - Each blueprint is registered in the Flask application
    - If JSON is invalid, loading is skipped with warning
  """

  __blueprints   : list                = None
  __buildContext : SuccessBuildContext = None


  def __init__ ( self, buildContext : SuccessBuildContext ) -> None :
    """
    Initialize the blueprint loader.

    Args:
        buildContext: Build context with application configuration.

    Note:
        If blueprints.json does not exist or is not a valid list,
        it is initialized with an empty list and a warning is logged.
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self.__blueprints   = SuccessFile.loadAppJson ( os.path.join ( self.__buildContext._appPath, "blueprints.json" ) )

    if not isinstance ( self.__blueprints, list ) :
      self._logger.log ( "blueprints.json no existe o no es una lista válida. Se omite carga de blueprints.", "WARNING" )
      self.__blueprints = []


  def load ( self ) -> None :
    """
    Load and register all application blueprints.

    Iterates over blueprints.json definitions, builds each
    blueprint using SuccessBlueprintBuilder, and registers it
    in the Flask application.
    """
    self._logger.log ( f"Iniciando carga de blueprints para la aplicación {self.__buildContext._appName}.", "INFO" )

    for bpDef in self.__blueprints :
      builder   = SuccessBlueprintBuilder ( self.__buildContext, bpDef )
      blueprint = builder.build ()
      self.__buildContext.getApp ().register_blueprint ( blueprint )

    self._logger.log ( f"Finalizada la carga de blueprints para la aplicación {self.__buildContext._appName}.", "INFO" )
