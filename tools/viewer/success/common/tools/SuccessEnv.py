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
from dotenv import dotenv_values
from dotenv import load_dotenv
from flask  import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
import ast
import os

# Success Libraries / Librerías Success

# Preconditions / Precondiciones
RESERVED_VARS = {
  'SUCCESS_APP_PREFIX',
  'SUCCESS_MAIN_APP',
  'SUCCESS_SECONDARY_APPS',
  'SUCCESS_ALLOW_NO_MAIN_APP',
  'SUCCESS_SAVE_MODE',
  'SUCCESS_SHOW_SUMMARY',
  'SUCCESS_SUMMARY_LEVEL',
  'SUCCESS_HUMOR_ENABLED',
  'SUCCESS_MOOD_LANG',
  'SUCCESS_APP_MODE',
  'SUCCESS_APP_DOMAIN',
}


class SuccessEnv () :
  """
  Utilitario de conversión de valores de variables de entorno.
  
  Esta clase proporciona métodos estáticos para convertir y validar
  valores de variables de entorno a tipos específicos (bool, int, list, etc.).
  
  Propósito:
  ----------
  SuccessEnv es una clase utilitaria PURA que NO accede directamente a
  variables de entorno. Su única responsabilidad es transformar valores
  ya obtenidos a tipos utilizables por el framework Success.
  
  Uso típico:
  -----------
  # Conversión de valores
  SuccessEnv.isTrue('true')           # → True
  SuccessEnv.isTrue('FALSE')          # → False
  SuccessEnv.toInt('42')              # → 42
  SuccessEnv.toList('[1, 2, 3]')      # → [1, 2, 3]
  SuccessEnv.getJson('{"key": "val"}') # → {'key': 'val'}
  
  # Validación de valores
  SuccessEnv.isEmpty('')              # → True
  SuccessEnv.isNone('none')           # → True
  
  Arquitectura:
  -------------
  Esta clase es utilizada internamente por:
  - SuccessSystemEnv: Para convertir valores de os.environ
  - SuccessAppEnv: Para convertir valores del diccionario _data
  
  No debe instanciarse. Todos sus métodos son estáticos.
  
  Attributes:
      RESERVED_VARS (set): Conjunto de nombres de variables reservadas
                         que no se cargan desde archivos .env filtrados.
  
  Note:
      - Los métodos de conversión son tolerantes a None y valores vacíos
      - isTrue() solo reconoce 'true' (case-insensitive), no 'yes', '1', etc.
      - toList() soporta tanto formato Python como formato Success
  """


  @staticmethod
  def verify_required_env_vars ( required_vars : list [ str ] ) -> None :
    """
    Verifica que todas las variables de entorno requeridas estén definidas.
    
    Args:
        required_vars: Lista de nombres de variables que deben estar definidas.
    
    Raises:
        EnvironmentError: Si alguna variable requerida no está definida.
    
    Example:
        SuccessEnv.verify_required_env_vars(['DATABASE_URL', 'SECRET_KEY'])
    """
    for var in required_vars :
      if not os.getenv ( var ) :
        raise EnvironmentError ( f"Variable de entorno obligatoria no definida: {var}" )


  @staticmethod
  def load_env_filtered ( path : str ) -> None :
    """
    Carga variables de entorno desde un archivo .env, excluyendo reservadas.
    
    Carga todas las variables del archivo especificado EXCEPTO las listadas
    en RESERVED_VARS, que deben ser manejadas a nivel de framework.
    
    Args:
        path: Ruta al archivo .env a cargar.
    
    Note:
        Las variables se cargan en os.environ globalmente.
    """
    env_vars = dotenv_values ( path )
    for k, v in env_vars.items () :
      if k not in RESERVED_VARS :
        os.environ [ k ] = v


  @staticmethod
  def getCorsResources ( config : dict ) -> dict :
    """
    Builds CORS resources configuration from environment variables.

    Returns:
      dict: Dictionary containing CORS resource configuration.
    """
    corsResources = SuccessEnv.toList ( config.get ( 'CORS_RESOURCES_APP_RESOURCES' ) )
    corsOrigins   = SuccessEnv.toList ( config.get ( 'CORS_RESOURCES_APP_ORIGINS' ) )
    corsMethods   = SuccessEnv.toList ( config.get ( 'CORS_RESOURCES_APP_METHODS' ) )
    corsAllowed   = SuccessEnv.toList ( config.get ( 'CORS_RESOURCES_APP_ALLOW_HEADERS' ) )
    corsExposes   = SuccessEnv.toList ( config.get ( 'CORS_RESOURCES_APP_EXPOSE_HEADERS' ) )

    # --- [OLD IMPLEMENTATION - START] ---
    # resource = '{ '
    # for i in range ( len ( corsResources ) ) :
    #   resource += corsResources [ i ] + ' : { '
    #   resource += '\'origins\' : ' + SuccessEnv.listToString ( corsOrigins, i ) + ', '
    #   resource += '\'methods\' : ' + SuccessEnv.listToString ( corsMethods, i ) + ', '
    #   resource += '\'allow_headers\' : ' + SuccessEnv.listToString ( corsAllowed, i ) + ', '
    #   resource += '\'expose_headers\' : ' + SuccessEnv.listToString ( corsExposes, i )
    #   resource += ' }, '
    #
    # resource = resource [ : -2 ]
    # resource += ' }'
    #
    # return SuccessEnv.toResource ( resource )
    # --- [OLD IMPLEMENTATION - END] ---

    resources = {}
    for i in range ( len ( corsResources ) ) :
      resources [ corsResources [ i ] ] = {
        'origins'         : corsOrigins [ i ],
        'methods'         : corsMethods [ i ],
        'allow_headers'   : corsAllowed [ i ],
        'expose_headers'  : corsExposes [ i ]
      }

    return resources


  @staticmethod
  def getJson ( value : Any ) -> Any :
    """
    Parsea un string como JSON.
    
    Args:
        value: String conteniendo JSON válido.
    
    Returns:
        El objeto JSON parseado (dict, list, etc.).
    
    Raises:
        json.JSONDecodeError: Si el valor no es JSON válido.
    
    Example:
        SuccessEnv.getJson('{"name": "John"}')  # → {'name': 'John'}
    """
    return json.loads ( value )


  @staticmethod
  def isEmpty ( value : str ) -> bool :
    """
    Verifica si un valor está vacío.

    Args:
        value: Valor a verificar.

    Returns:
        True si el valor es string vacío o None, False en caso contrario.

    Example:
        SuccessEnv.isEmpty('')   # → True
        SuccessEnv.isEmpty(' ')  # → False
        SuccessEnv.isEmpty(None) # → True
    """
    if value is None :
      return True
    
    return bool ( value == '' )


  @staticmethod
  def isNone ( value : str ) -> bool :
    """
    Verifica si un valor representa None.

    Args:
        value: Valor a verificar.

    Returns:
        True si el valor es 'none' (case-insensitive), False en caso contrario.
        Retorna False si el valor es None (objeto Python).

    Example:
        SuccessEnv.isNone('none')   # → True
        SuccessEnv.isNone('None')   # → True
        SuccessEnv.isNone('NULL')   # → False
        SuccessEnv.isNone(None)     # → False
    """
    if value is None :
      return False
    
    return bool ( value.lower () == 'none' )


  @staticmethod
  def isTrue ( value : Any ) -> bool :
    """
    Verifica si un valor representa 'true'.

    Compara el valor convertido a string con 'true' (case-insensitive).
    Solo reconoce explícitamente 'true' o 'false', otros valores retornan False.

    Args:
        value: Valor de cualquier tipo a verificar.

    Returns:
        True si el valor es 'true' (case-insensitive), False en caso contrario.
        Retorna False si el valor es None.

    Example:
        SuccessEnv.isTrue('true')   # → True
        SuccessEnv.isTrue('TRUE')   # → True
        SuccessEnv.isTrue('false')  # → False
        SuccessEnv.isTrue(True)     # → True
        SuccessEnv.isTrue(False)    # → False
        SuccessEnv.isTrue('yes')    # → False
        SuccessEnv.isTrue(None)     # → False
    """
    if value is None :
      return False
    
    if isinstance ( value, str ) and not value.lower () in ( 'true', 'false' ) :
      return False

    return bool ( str ( value ).lower () == 'true' )


  @staticmethod
  def listToString ( envVarList : list, index : int = 0 ) -> str :
    """
    Convierte un elemento de lista a su representación string.
    
    Args:
        envVarList: Lista de valores.
        index: Índice del elemento a convertir (default: 0).
    
    Returns:
        Representación string del elemento usando __repr__().
    
    Example:
        SuccessEnv.listToString(['a', 'b'], 0)  # → "'a'"
    """
    return envVarList [ index ].__repr__ ()


  @staticmethod
  def toInt ( value : str ) -> int :
    """
    Convierte un valor a entero.
    
    Args:
        value: Valor numérico en string o número.
    
    Returns:
        El valor convertido a int.
    
    Raises:
        ValueError: Si el valor no es convertible a entero.
    
    Example:
        SuccessEnv.toInt('42')    # → 42
        SuccessEnv.toInt(100)     # → 100
    """
    return int ( value )


  @staticmethod
  def toList ( value : Any ) -> List [ Any ] :
    """
    Convierte un valor a lista.
    
    Soporta múltiples formatos:
    - None → []
    - Lista existente → misma lista
    - String formato Python: "[1, 2, 3]" → [1, 2, 3]
    - String formato Success: "r['a', 'b']" → ['a', 'b']
    
    Args:
        value: Valor a convertir (string, lista, tuple, o None).
    
    Returns:
        Lista convertida. Retorna lista vacía si el valor es None o vacío.
    
    Example:
        SuccessEnv.toList(None)              # → []
        SuccessEnv.toList('[1, 2, 3]')       # → [1, 2, 3]
        SuccessEnv.toList("r['a', 'b']")     # → ['a', 'b']
        SuccessEnv.toList((1, 2))            # → [1, 2]
    """
    if value is None :
      return []

    if isinstance ( value, ( list, tuple ) ) :
      return list ( value )

    text = str ( value ).strip ()
    if text == '' :
      return []

    toReturn = list ()
    if ( SuccessEnv.wellFormedList ( text ) ) :
      toReturn = text.strip ( ' ][ ' ).split ( ', ' )

    else :
      parsed = ast.literal_eval ( text )
      if isinstance ( parsed, ( list, tuple ) ) :
        toReturn = list ( parsed )

      else :
        toReturn = [ parsed ]

    return toReturn


  @staticmethod
  def toResource ( resource : str ) -> Any :
    """
    Parsea un string como literal Python (dict, list, etc.).
    
    Args:
        resource: String conteniendo un literal Python válido.
    
    Returns:
        El objeto parseado.
    
    Raises:
        ValueError: Si el string no es un literal Python válido.
    
    Example:
        SuccessEnv.toResource("{'key': 'val'}")  # → {'key': 'val'}
    """
    return ast.literal_eval ( resource )


  @staticmethod
  def wellFormedList ( value : str ) -> bool :
    """
    Verifica si un string es una lista bien formada en formato Success.
    
    Un lista en formato Success comienza con "r['" y contiene "[" y "]".
    
    Args:
        value: String a verificar.
    
    Returns:
        True si el string tiene formato de lista Success, False en caso contrario.
    
    Example:
        SuccessEnv.wellFormedList("r['a', 'b']")  # → True
        SuccessEnv.wellFormedList("[1, 2, 3]")    # → False
    """
    string = value

    return ( 'r\'' in string ) and ( '[' in string ) and ( ']' in string )
