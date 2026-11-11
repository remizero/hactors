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
from pathlib import Path
from types import ModuleType
from typing import Type
from typing import Optional
import importlib
import sys

# Success Libraries / Librerías Success
from success.common.infra.logger.SuccessLogger import SuccessLogger

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessSemanticResolver () :
  """
  Semantic resolution for the Success framework.

  Provides utilities for resolving semantic names of blueprints,
  subdomains, endpoints, and actions based on the Success directory
  structure.

  This class can depend on common without violating architecture.
  """


  def __init__ ( self, root : Path ) -> None :
    """
    Initialize the semantic resolver.

    Args:
      root: Root path to start resolution from.
    """
    self.root = Path ( root ).resolve ()


  # =====================================================
  # MÉTODOS DE CLASE PARA BACKWARD COMPATIBILITY
  # =====================================================


  def resolveBlueprintName ( self, fsPath : Path ) -> str :
    """
    Return the semantic blueprint name based on directory structure.

    Args:
      fsPath: Filesystem path of the file.

    Returns:
      str: Blueprint name (e.g., 'apps_synthetos_services_view_chromadb').

    Example:
      >>> resolver.resolveBlueprintName(Path('/apps/synthetos/services/view/chromadb/Action.py'))
      'apps_synthetos_services_view_chromadb'
    """
    parts = fsPath.relative_to ( self.root ).parts
    return "_".join ( parts [ : -1 ] )  # Excluir nombre de archivo


  def resolveSubdomain ( self, fsPath : Path, fallbackEnv : str = "SUCCESS_SUBDOMAIN" ) -> str :
    """
    Determine the subdomain to use for Flask, with environment fallback.

    Args:
      fsPath: Filesystem path of the file.
      fallbackEnv: Environment variable for fallback.

    Returns:
      str: Subdomain name.
    """
    from os import getenv
    
    # Intentar obtener del entorno primero
    env_subdomain = getenv ( fallbackEnv )
    if env_subdomain :
      return env_subdomain
    
    # Fallback al primer componente después de root
    parts = fsPath.relative_to ( self.root ).parts
    if parts :
      return parts [ 0 ]
    
    return "default"


  def resolveEndpointRule ( self, fsPath : Path, prefix : str = None ) -> str :
    """
    Return the endpoint rule from the action name.

    Args:
      fsPath: Filesystem path of the file.
      prefix: Optional prefix for the rule.

    Returns:
      str: Endpoint rule (e.g., '/users', '/api/products').
    """
    stem = fsPath.stem  # Nombre sin extensión
    
    # Eliminar sufijos comunes
    for suffix in [ 'Action', 'Controller', 'View', 'Resource' ] :
      if stem.endswith ( suffix ) :
        stem = stem [ : -len ( suffix ) ]
        break
    
    rule = f"/{stem}"
    
    if prefix :
      rule = f"{prefix.rstrip('/')}{rule}"
    
    return rule


  def resolveActionClass ( appPath : str, actionPath : str ) -> Type :
    """
    Resolve and load the Action class from its path.

    Args:
      appPath: Base application path.
      actionPath: Action path relative to appPath.

    Returns:
      Type: The resolved Action class.

    Raises:
      ImportError: If the action cannot be loaded.
    """
    module_path = SuccessSemanticResolver.normalizeActionModule ( appPath, actionPath )
    
    if module_path is None :
      raise ImportError ( f"Ruta de módulo inválida: actionPath={actionPath}" )
    
    module_name, class_name = module_path.rsplit ( ".", 1 )

    try :
      module = importlib.import_module ( module_path )

    except ModuleNotFoundError as exc :
      # Fallback legacy: apps.<app>.services...
      # Solo procede cuando lo que falta es el propio módulo buscado. Si lo que
      # falta es una dependencia suya, anteponer apps. no la resuelve y
      # reintentar convierte la causa real en un 'apps.apps' inexistente.
      missing = exc.name or ""
      if module_path.startswith ( "apps." ) or not (
        module_path == missing or module_path.startswith ( f"{missing}." )
      ) :
        raise

      module = importlib.import_module ( f"apps.{module_path}" )

    if not hasattr ( module, class_name ) :
      raise ImportError ( f"No se encontró la clase '{class_name}' en el módulo '{module_name}'" )

    return getattr ( module, class_name )


  def normalizeActionModule ( appPath : str, actionPath : str ) -> str :
    """
    Normalize an action path to Python module notation.

    Args:
      appPath: Base application path.
      actionPath: Action path.

    Returns:
      str: Normalized module path (e.g., '<app>.services.view.Action').
    """
    normalized_action_path = str ( actionPath or "" ).replace ( "\\", "/" ).strip ()

    # MultiApp-safe:
    # Si la ruta de acción ya viene en formato app-scope (apps/<app>/...),
    # usamos módulo canónico "<app>.services..." para evitar colisiones
    if normalized_action_path.startswith ( "apps/" ) :
      # apps/<app>/services/view/... -> <app>.services.view...
      scoped = normalized_action_path.strip ( "/" ).split ( "/" )
      module = ".".join ( scoped [ 0 : ] )

    else :
      # Construir desde appPath
      from success.common.reflection.SuccessModuleMetadata import SuccessModuleMetadata
      app_name = SuccessModuleMetadata.getAppNameFromPath ( appPath )
      module   = f"{app_name}.{normalized_action_path.replace('/', '.')}"

    # Asegurar que termina en .Action
    if not module.endswith ( ".Action" ) :
      module += ".Action"

    return module


  def resolveViewFunc ( appPath : str, actionPath : str, endpointName : str = None ) :
    """
    Resolve a view function from its action.

    Args:
      appPath: Base application path.
      actionPath: Action path.
      endpointName: Optional endpoint name.

    Returns:
      The resolved view function (as_view).
    """
    action_cls = SuccessSemanticResolver.resolveActionClass ( Path ( appPath ).parent, actionPath )
    name       = endpointName or action_cls.__name__
    return action_cls.as_view ( name )


  def resolveRestResource ( appPath : str, actionPath : str ) -> Type :
    """
    Resolve a REST resource from its action.

    Args:
      appPath: Base application path.
      actionPath: Action path.

    Returns:
      Type: The REST resource class.
    """
    
    return SuccessSemanticResolver.resolveActionClass ( Path ( appPath ).parent, actionPath )


  def resolveController ( self, appPath : str, controllerName : str,
                          logger : SuccessLogger = None ) -> Type :
    """
    Resolve a controller from its name.

    Args:
      appPath: Base application path.
      controllerName: Controller name.
      logger: Optional logger for debugging.

    Returns:
      Type: The controller class.
    """
    from success.common.reflection.SuccessModuleMetadata import SuccessModuleMetadata
    
    app_name = SuccessModuleMetadata.getAppNameFromPath ( appPath )
    module_path = f"{app_name}.controllers.{controllerName}"
    
    if logger :
      logger.log ( f"Resolviendo controlador: {module_path}", "DEBUG" )
    
    return importlib.import_module ( module_path )


  def resolveService ( self, appPath : str, serviceName : str,
                       logger : SuccessLogger = None ) -> Type :
    """
    Resolve a service from its name.

    Args:
      appPath: Base application path.
      serviceName: Service name.
      logger: Optional logger for debugging.

    Returns:
      Type: The service class.
    """
    from success.common.reflection.SuccessModuleMetadata import SuccessModuleMetadata
    
    app_name = SuccessModuleMetadata.getAppNameFromPath ( appPath )
    module_path = f"{app_name}.services.{serviceName}"
    
    if logger :
      logger.log ( f"Resolviendo servicio: {module_path}", "DEBUG" )
    
    return importlib.import_module ( module_path )


  def buildEndpointName ( self, blueprintName : str, actionName : str ) -> str :
    """
    Build a unique endpoint name.

    Args:
      blueprintName: Blueprint name.
      actionName: Action name.

    Returns:
      str: Endpoint name (e.g., 'apps_synthetos_users_list').
    """
    return f"{blueprintName}_{actionName}"


  def parseEndpointName ( self, endpointName : str ) -> dict :
    """
    Parse an endpoint name into its components.

    Args:
      endpointName: Endpoint name to parse.

    Returns:
      dict: Endpoint components (app, protocol, action).
    """
    parts = endpointName.split ( "_" )
    
    if len ( parts ) < 3 :
      return {
        "raw" : endpointName,
        "app" : None,
        "protocol" : None,
        "action" : endpointName
      }
    
    return {
      "raw"      : endpointName,
      "app"      : parts [ 1 ] if len ( parts ) > 1 else None,
      "protocol" : parts [ 3 ] if len ( parts ) > 3 else None,
      "action"   : parts [ -1 ]
    }
