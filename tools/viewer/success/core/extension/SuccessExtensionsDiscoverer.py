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
import importlib
import inspect
import json
import os
from typing import Any, Dict, List, Optional

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                 import SuccessClass
from success.core.SuccessContext                      import SuccessContext
from success.common.base.SuccessExtension             import SuccessExtension
from success.common.reflection.SuccessModuleLoader    import SuccessModuleLoader
from success.common.tools.SuccessFile                 import SuccessFile
from success.common.reflection.SuccessModuleMetadata  import SuccessModuleMetadata
from success.core.SuccessBuildContext                 import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessExtensionsDiscoverer ( SuccessClass ) :
  """
  Discoverer of custom application extensions.

  Discovers and loads custom extension classes defined in
  extensions.json, resolving and registering them in the context.

  Purpose:
  ----------
  SuccessExtensionsDiscoverer is responsible for:
  - Reading custom extensions from extensions.json
  - Resolving classes from their module paths
  - Validating they inherit from SuccessExtension
  - Configuring and registering each extension in the context

  Expected structure:
  --------------------
  extensions.json should contain a list of objects with:
  - class: Full class path (e.g., "myapp.extensions.MyExtension")
  - enabled: Boolean to enable/disable
  - config: Dictionary with key-value configuration

  Usage:
  ------
  ctx = SuccessBuildContext.from_app('myapp', '/apps/myapp')
  discoverer = SuccessExtensionsDiscoverer(ctx)
  extensions = discoverer.discover()  # List of loaded extensions

  Attributes:
      _data (dict): Data loaded from extensions.json.
      __buildContext (SuccessBuildContext): Build context.

  Note:
    - Extensions must inherit from SuccessExtension
    - Registered in SuccessContext with multiple aliases
    - Load errors are logged but do not stop the process
  """

  _data          : dict                = None
  __buildContext : SuccessBuildContext = None


  def __init__ ( self, buildContext : SuccessBuildContext ) -> None :
    """
    Initialize the extension discoverer.

    Args:
      buildContext: Build context with application configuration.

    Note:
      If extensions.json does not exist or is invalid, _data will be None.
    """
    super ().__init__ ()
    self.__buildContext = buildContext
    self._data          = SuccessFile.loadAppJson ( os.path.join ( self.__buildContext._appPath, "extensions.json" ) )


  def discover ( self ) -> Optional [ List [ Any ] ] :
    """
    Discover and load custom extensions from extensions.json.

    Iterates over extension definitions, resolves each class,
    validates inheritance from SuccessExtension, applies configuration and
    registers in the context.

    Returns:
        Optional[List[Any]]: List of tuples (name, instance) of
            loaded extensions, or None if no extensions.

    Note:
        - Invalid extensions are logged as ERROR but do not stop
        - Each extension is registered with multiple aliases in the context
    """
    if not self._data :
      self._logger.log ( f"No se registraron extensiones personalizadas para la aplicación {SuccessContext ().getCurrentAppName ()}.", "WARNING" )
      return

    self._logger.log ( f"Iniciando carga de extensiones personalizadas para la aplicación {self.__buildContext._appName}.", "INFO" )

    extensions = []

    for idx, estension in enumerate ( self._data ) :
      _class  = estension.get ( "class", f"unnamed_extension_{idx}" )
      enabled = estension.get ( "enabled" )
      config  = estension.get ( "config", {} )

      if not isinstance ( _class, str ) :
        self._logger.log ( f"[{_class}] La 'extensión' debe ser una cadena tipo 'paquete.Clase'.", "ERROR" )
        continue

      if not config :
        self._logger.log ( f"[{config}] El valor de 'config' debe contener al menos un registro de tipo 'key' : 'value'.", "ERROR" )
        continue

      try :

        instance = self.resolveCallback ( _class )
        instance.userConfig ( **config )
        instance.register ()
        self.__buildContext.setExtension ( instance.__class__.__name__, instance )
        self._logger.log ( f"Se ha registrado la extensiones personalizadas {instance.__class__.__name__, instance} para la aplicación {SuccessContext ().getCurrentAppName ()}.", "INFO" )

      except Exception as e :
        self._logger.log ( f"Error al resolver la clase de extensión '{_class}': {e}", "ERROR" )
        continue

      _tuple = ( instance.__class__.__name__, instance )

      extensions.append ( _tuple )

    self._logger.log ( f"Finalizada la carga de extensiones personalizadas para la aplicación {self.__buildContext._appName}.", "INFO" )

    return extensions


  def resolveCallback ( self, callback : str ) -> callable :
    """
    Resolve and create an extension instance from a class path.

    Internal method that parses the callback in "package.Class" format,
    loads the class using SuccessModuleLoader, validates inheritance from
    SuccessExtension and creates an instance.

    Args:
        callback: Full class path (e.g., "myapp.extensions.MyExtension").

    Returns:
        callable: Configured extension instance.

    Raises:
        ValueError: If callback does not have valid format (less than 3 parts).
        TypeError: If class does not inherit from SuccessExtension.
        RuntimeError: If an error occurs during resolution.

    Example:
        instance = discoverer.resolveCallback('myapp.extensions.RedisExtension')
    """
    try :
      parts = callback.split ( "." )
      if len ( parts ) < 3 :
        raise ValueError ( f"Callback '{callback}' debe tener formato completo: paquete.Clase" )

      *moduleParts, className = parts

      # Nueva implementación con SuccessModuleLoader
      module_path = ".".join ( moduleParts + [ className ] )
      _class = SuccessModuleLoader.loadClassFromString ( module_path )

      if not issubclass ( _class, SuccessExtension ) :
        raise TypeError ( f"La clase '{className}' no hereda de SuccessExtension." )

      instance = _class ( self.__buildContext.getApp () )

      return instance

    except Exception as e :
      raise RuntimeError ( f"Error resolviendo callback '{callback}': {e}" )
