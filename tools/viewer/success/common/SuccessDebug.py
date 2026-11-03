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
from datetime  import datetime
from functools import wraps
from typing    import Any
from typing    import Callable
from typing    import TypeVar
import os
import time
import inspect

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessDebug () :

  __file_path      : str  = './log/debug.txt'
  __log_to_console : bool = os.getenv ( 'SUCCESS_DEBUG_CONSOLE', 'true' ).lower () in [ 'True', 'true', '1', 'yes' ]
  __is_debug       : bool = os.getenv ( 'DEBUG', 'False' ).lower () in [ 'True', 'true', '1', 'yes' ]


  @classmethod
  def _print ( cls, message : str ) -> None :
    if cls.__log_to_console :
      print ( message )


  @classmethod
  def _write ( cls, message : str ) -> None :
    os.makedirs ( os.path.dirname ( cls.__file_path ), exist_ok = True )
    with open ( cls.__file_path, 'a', encoding = 'utf-8' ) as f :
      f.write ( message + os.linesep )


  @classmethod
  def _log ( cls, message : str ) -> None :
    if not cls.__is_debug :
      return
    timestamp     = datetime.now ().strftime ( '%Y-%m-%d %H:%M:%S' )
    final_message = f"[DEBUG {timestamp}] {message}"
    cls._write ( final_message )
    cls._print ( final_message )


  @classmethod
  def log ( cls, msg : Any ) -> None :
    cls._log ( str ( msg ) )


  @classmethod
  def watch ( cls, var_name : str, value : Any ) -> None :
    caller   = inspect.stack () [ 1 ]
    location = f"{caller.filename}:{caller.lineno}"
    cls._log ( f"WATCH {var_name} = {value!r} at {location}" )


  @classmethod
  def trace ( cls, label : str = "" ) -> None :
    caller   = inspect.stack () [ 1 ]
    location = f"{caller.filename}:{caller.function}:{caller.lineno}"
    cls._log ( f"TRACE {label} at {location}" )


  @classmethod
  def profile ( cls, fn : Callable ) -> Callable :
    @wraps ( fn )
    def wrapper ( *args, **kwargs ) :
      if not cls.__is_debug :
        return fn ( *args, **kwargs )

      start    = time.time ()
      result   = fn ( *args, **kwargs )
      duration = time.time () - start
      cls._log ( f"PROFILE {fn.__name__} took {duration:.4f}s" )
      return result

    return wrapper


  @classmethod
  def only_debug ( cls, fn : Callable ) -> Callable :
    @wraps ( fn )
    def wrapper ( *args, **kwargs ) :
      if cls.__is_debug :
        return fn ( *args, **kwargs )
        
    return wrapper



# === EJEMPLO DE USO ===
# if __name__ == "__main__":
#   SuccessDebug.log ( "Iniciando debug..." )
#   SuccessDebug.watch ( "valor_inicial", {"x": 10, "y": [1, 2, 3]} )
#   SuccessDebug.trace ( "Comienzo del bloque crítico" )

#   @SuccessDebug.profile
#   def test_function () :
#     time.sleep ( 0.1 )
#     return "done"

#   result = test_function ()
#   SuccessDebug.log ( f"Resultado de test_function: {result}" )
