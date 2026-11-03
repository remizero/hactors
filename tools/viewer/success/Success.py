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
# from werkzeug.wsgi import WSGIApplication
import uuid

# Success Libraries / Librerías Success
from success.common.base.SuccessClass             import SuccessClass
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv
from success.core.SuccessSystemState              import SuccessSystemState
from success.common.tools.SuccessStructs          import SuccessStructs
from success.core.SuccessContext                  import SuccessContext
from success.core.SuccessWSGIFactory              import SuccessWSGIFactory
from success.common.types.WSGIApplication         import WSGIApplication

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
session_id = str ( uuid.uuid4 () )


class Success ( SuccessClass ) :
  """Clase principal para inicializar y gestionar el sistema Success.
  
  Esta clase es el punto de entrada principal para crear y configurar
  una aplicación WSGI utilizando el framework Success.
  
  Attributes:
    __success: Instancia de la aplicación WSGI creada.
  """

  __success : WSGIApplication = None


  def __init__ ( self ) -> None :
    """Inicializa el sistema Success configurando el entorno y contexto.
    
    Configura las variables de entorno del sistema, inicializa el logger,
    establece el contexto del framework y genera un ID de sesión único.
    """
    SuccessSystemEnv.loadEnv ()
    super ().__init__ ()
    self._logger.log ( "Iniciando la carga del sistema Success.", "INFO" )
    SuccessContext ().setContext ( SuccessStructs.successContextFramework () )
    SuccessContext ().setSuccessValue ( "SESSION_ID", session_id )
    SuccessContext ().setSuccessValue ( "LOGGER", self._logger )


  def create ( self ) -> None :
    """Crea y configura la aplicación Flask del sistema Success.
    
    Inicializa el estado del sistema, configura el entorno y logger,
    construye la aplicación WSGI y genera un reporte del estado.
    """
    try :
      SuccessSystemState.startTimer ()
      SuccessSystemState.setEnv ( SuccessSystemEnv.get ( "FLASK_ENV", "development" ) )
      SuccessSystemState.setLoggerFile ( SuccessSystemEnv.isTrue ( "LOGGER_FILE" ) )

      self._logger.log ( "Iniciando la creación de la aplicación Flask.", "INFO" )

      factory = SuccessWSGIFactory ()
      self.__success = factory.build ()

      self._logger.log ( "Finalizando la creación de la aplicación Flask.", "INFO" )
      SuccessSystemState.report ( self._logger )
      # if SuccessSystemEnv.isTrue ( "SUCCESS_SHOW_SUMMARY" ) and not isTestingEnv () :
      #   level = SuccessSystemEnv.get ( "SUCCESS_SUMMARY_LEVEL", "FULL" ).upper ()
      # SuccessSummary ().show ( level = level )

      # if ( SuccessSystemEnv.isTrue ( "SUCCESS_HUMOR_ENABLED" ) ) :
      #   BootCommentator.show ( apps )

    except :
      self._logger.uncatchErrorException ()


  def getApp ( self ) -> WSGIApplication :
    """Obtiene la instancia de la aplicación WSGI creada.
    
    Returns:
        La instancia de la aplicación WSGI configurada.
    """
    self._logger.log ( "Carga exitosa del sistema Success.", "INFO" )
    return self.__success


  def run ( self ) -> None :
    """Ejecuta la aplicación WSGI en el servidor de desarrollo.
    
    Dependiendo del modo configurado (singleapp o multiapp), ejecuta
    la aplicación utilizando el servidor integrado de Flask o Werkzeug.
    """
    self._logger.log ( "Carga exitosa del sistema Success.", "INFO" )
    # como ejecutar o uno u otro
    # self.__success.run ()
    # --- [OLD IMPLEMENTATION - NO USAR EN PRODUCCION] ---
    # run_simple ( '0.0.0.0', 5000, self.__success, use_reloader = True, use_debugger = True, use_evalex = True )
    # --- [OLD IMPLEMENTATION - FIN] ---
    if ( SuccessSystemEnv.get ( "SUCCESS_APP_MODE", "singleapp" ).lower () == "singleapp" ) :
      # NO existe run() en un WSGI callable. Solo Flask tiene app.run()
      # Aquí deberías hacer algo como:
      from flask import Flask
      if isinstance ( self.__success, Flask ) :
        # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION START] ---
        appEnv = str ( SuccessSystemEnv.get ( "APP_ENV", "development" ) ).lower ()
        isDevLike = appEnv in [ "development", "local", "testing" ]
        isDebugRequested = SuccessSystemEnv.isTrue ( "DEBUG" ) or SuccessSystemEnv.isTrue ( "FLASK_DEBUG" )
        enableDebugger = isDevLike and isDebugRequested
        enableEvalex = enableDebugger and SuccessSystemEnv.isTrue ( "SUCCESS_ENABLE_EVALEX" )

        host = SuccessSystemEnv.get ( "APP_HOST", "127.0.0.1" ) or "127.0.0.1"
        if enableDebugger and host == "0.0.0.0" :
          host = "127.0.0.1"

        try :
          port = SuccessSystemEnv.toInt ( "APP_PORT" )
        except Exception :
          port = 5000

        self.__success.run (
          host         = host,
          port         = port,
          debug        = enableDebugger,
          use_reloader = enableDebugger,
          use_evalex   = enableEvalex
        )
        # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION END] ---

      else :
        # fallback o advertencia
        self._logger.log ( "SingleApp no es un Flask instance", "WARN" )
    else :
      # multiapp -> dev server
      from werkzeug.serving import run_simple
      # --- [OLD IMPLEMENTATION - NO USAR EN PRODUCCION] ---
      # run_simple ( '0.0.0.0', 5000, self.__success, use_reloader = True, use_debugger = True, use_evalex = True )
      # --- [OLD IMPLEMENTATION - FIN] ---

      # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION START] ---
      appEnv = str ( SuccessSystemEnv.get ( "APP_ENV", "development" ) ).lower ()
      isDevLike = appEnv in [ "development", "local", "testing" ]
      isDebugRequested = SuccessSystemEnv.isTrue ( "DEBUG" ) or SuccessSystemEnv.isTrue ( "FLASK_DEBUG" )
      enableDebugger = isDevLike and isDebugRequested
      enableEvalex = enableDebugger and SuccessSystemEnv.isTrue ( "SUCCESS_ENABLE_EVALEX" )

      host = SuccessSystemEnv.get ( "APP_HOST", "127.0.0.1" ) or "127.0.0.1"
      if enableDebugger and host == "0.0.0.0" :
        host = "127.0.0.1"

      try :
        port = SuccessSystemEnv.toInt ( "APP_PORT" )
      except Exception :
        port = 5000

      run_simple (
        host,
        port,
        self.__success,
        use_reloader = enableDebugger,
        use_debugger = enableDebugger,
        use_evalex   = enableEvalex
      )
      # --- [SECURITY REQUIREMENT - NEW IMPLEMENTATION END] ---
