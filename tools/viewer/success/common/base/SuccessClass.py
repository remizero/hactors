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
from abc import ABC
from abc import abstractmethod

# Success Libraries / Librerías Success
from success.common.infra.logger.SuccessLogger       import SuccessLogger
from success.common.reflection.SuccessModuleMetadata import SuccessModuleMetadata
from success.core.SuccessContext                     import SuccessContext

# Preconditions / Precondiciones


class SuccessClass ( ABC ) :
  """
  Abstract base class for all classes in the Success framework.

  Provides common functionality such as logging and reflection to identify
  the module and scope of each derived class.

  Attributes:
    _logger (SuccessLogger): Instance of SuccessLogger for event logging.
    _module (str): Name of the module where the class is defined.
    _scope (str): Application scope of the class.
  """

  _logger : SuccessLogger = None
  _module : str           = None
  _scope  : str           = None


  def __init__ ( self ) -> None :
    """
    Initialize the SuccessClass configuring logger and reflection.

    Obtains the application name and scope from the module where the class
    is defined, and initializes the corresponding logger.

    Note:
      Logs an informational message about the class initialization.
    """
    module  = SuccessModuleMetadata.getAppName ( self.__class__.__module__ )
    scope   = SuccessModuleMetadata.getScope ( self.__class__.__module__ )
    ctx_app = SuccessContext ().getCurrentAppName ()
    if ctx_app:
      module = ctx_app

    self._module = module
    self._scope  = scope
    self._logger = SuccessLogger ( module = self._module, scope = self._scope )
    self._logger.log ( f"Inicializando clase {self.__class__.__name__}...", "INFO" )
