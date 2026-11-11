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
from inspect import getmro
from types  import ModuleType
from typing import Any
from typing import Type
import importlib


# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessIntrospector () :
  """
  Introspection and reflection utilities for classes/objects.

  Provides utilities for inspecting classes, objects, and modules
  without depending on upper layers (core/engine).
  """


  @staticmethod
  def hasMethod ( instance : object, methodName : str ) -> bool :
    """
    Check if an object has a specific method.

    Args:
      instance: Object to inspect.
      methodName: Name of the method to check.

    Returns:
      bool: True if the method exists, False otherwise.
    """
    return hasattr ( instance, methodName )


  @staticmethod
  def hasAttribute ( instance : object, attributeName : str ) -> bool :
    """
    Check if an object has a specific attribute.

    Args:
      instance: Object to inspect.
      attributeName: Name of the attribute to check.

    Returns:
      bool: True if the attribute exists, False otherwise.
    """
    return hasattr ( instance, attributeName )


  @staticmethod
  def getMethodFromClass ( instance : object, methodName : str ) -> Any :
    """
    Get a method from a class instance.

    Args:
      instance: Class instance.
      methodName: Name of the method to get.

    Returns:
      The requested method.

    Raises:
      AttributeError: If the method does not exist in the class.
    """
    if not SuccessIntrospector.hasMethod ( instance, methodName ) :
      raise AttributeError ( f"El método '{methodName}' no existe en la clase '{instance.__class__.__name__}'" )

    return getattr ( instance, methodName )


  @staticmethod
  def getClassFromModule ( module : ModuleType, className : str ) -> Any :
    """
    Get a class from a module.

    Args:
      module: Module where the class is located.
      className: Name of the class to get.

    Returns:
      The requested class.

    Raises:
      ImportError: If the class does not exist in the module.
    """
    if not hasattr ( module, className ) :
      raise ImportError ( f"No se encontró la clase '{className}' en el módulo '{module.__file__}'" )

    return getattr ( module, className )


  @staticmethod
  def getInstanceFromString ( className : str, moduleName : str = None, params : dict = None ) -> Any :
    """
    Create a class instance from its name as a string.

    Args:
      className: Name of the class to instantiate.
      moduleName: Name of the module where the class is located (optional).
      params: Dictionary of parameters for the constructor.

    Returns:
      Instance of the requested class.

    Raises:
      ImportError: If the module or class is not found.
      AttributeError: If the class does not exist.
    """
    params = params or {}
    
    if moduleName :
      module = importlib.import_module ( moduleName )
      cls = getattr ( module, className )
    
    else :
      # Búsqueda en módulos ya importados
      for mod_name, mod in list ( globals ().items () ) :
        if isinstance ( mod, ModuleType ) and hasattr ( mod, className ) :
          cls = getattr ( mod, className )
          break
      else :
        raise ImportError ( f"No se encontró la clase '{className}' en ningún módulo importado" )
    
    return cls ( **params )


  @staticmethod
  def getMethods ( instance : object, includePrivate : bool = False, includeDunders : bool = False ) -> list :
    """
    Get all methods of an instance.

    Args:
      instance: Object to inspect.
      includePrivate: Include private methods (with underscore).
      includeDunders: Include dunder methods (__method__).

    Returns:
      List of method names.
    """
    methods = []
    for name in dir ( instance ) :
      if name.startswith ( "__" ) and not includeDunders :
        continue
      if name.startswith ( "_" ) and not includePrivate :
        continue
      if callable ( getattr ( instance, name ) ) :
        methods.append ( name )
    return methods


  @staticmethod
  def getAttributes ( instance : object, includePrivate : bool = False ) -> dict :
    """
    Get all attributes of an instance.

    Args:
      instance: Object to inspect.
      includePrivate: Include private attributes.

    Returns:
      Dictionary with attribute names and values.
    """
    attrs = {}
    for name in dir ( instance ) :
      if name.startswith ( "_" ) and not includePrivate :
        continue
      value = getattr ( instance, name )
      if not callable ( value ) :
        attrs [ name ] = value
    return attrs


  @staticmethod
  def getParentClasses ( cls : Type, includeSelf : bool = False ) -> list :
    """
    Get all parent classes of a given class.

    Args:
      cls: Class to inspect.
      includeSelf: Include the class itself in the list.

    Returns:
      List of parent classes in MRO order.
    """
    mro = getmro ( cls )
    if includeSelf :
      return list ( mro )
    return list ( mro [ 1 : ] )


  @staticmethod
  def isSubclassOf ( cls : Type, parentCls : Type ) -> bool :
    """
    Check if a class is a subclass of another.

    Args:
      cls: Class to check.
      parentCls: Potential parent class.

    Returns:
      bool: True if cls is a subclass of parentCls.
    """
    return issubclass ( cls, parentCls )