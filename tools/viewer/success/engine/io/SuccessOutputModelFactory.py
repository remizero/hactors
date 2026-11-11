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
from flask import current_app
from flask import has_app_context

# Success Libraries / Librerías Success
from success.common.types.SuccessProtocol                import SuccessProtocol
from success.common.reflection.SuccessModuleLoader       import SuccessModuleLoader
from success.engine.io.SuccessDefaultOutputModel         import SuccessDefaultOutputModel
from success.engine.io.SuccessControllerErrorOutputModel import SuccessControllerErrorOutputModel
from success.engine.io.SuccessInputErrorOutputModel      import SuccessInputErrorOutputModel
from success.engine.io.SuccessOutputModelContract        import SuccessOutputModelContract
from success.engine.io.SuccessRichOutputModel            import SuccessRichOutputModel

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessOutputModelFactory () :
  """
  Factory for creating output model instances.

  Creates appropriate output model instances based on the
  output kind (input_error, controller_error, success).
  """


  @staticmethod
  def create ( kind : str, protocol : SuccessProtocol = SuccessProtocol.VIEW ) -> SuccessOutputModelContract :
    """
    Create an output model instance based on kind.

    Args:
      kind: Output kind ('input_error', 'controller_error', 'success').

    Returns:
      SuccessOutputModelContract: Output model instance.
    """

    if kind == "input_error" :
      return SuccessInputErrorOutputModel ()

    if kind == "controller_error":
      return SuccessControllerErrorOutputModel ()

    use_rich_output = False

    if has_app_context () :
      use_rich_output = bool ( current_app.config.get ( "SUCCESS_OUTPUT_MODEL", False ) )

      if ( use_rich_output and ( protocol == SuccessProtocol.RESTFUL ) ) :
        try :
          
          class_path = current_app.config.get ( "SUCCESS_OUTPUT_MODEL_CLASS", "" ).strip ()
          if class_path :
            RichCls = SuccessModuleLoader.loadClassFromString ( class_path )
            richObj = RichCls ()
            if not isinstance ( richObj, SuccessRichOutputModel ) :
              raise TypeError ( "Invalid output model: must inherit from SuccessRichOutputModel" )
            return richObj

        except Exception as e :
          current_app.logger.exception ( "No se pudo cargar SUCCESS_OUTPUT_MODEL_CLASS='%s'. Usando SuccessDefaultOutputModel.", class_path )

    return SuccessDefaultOutputModel ()
