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

# Success Libraries / Librerías Success
from success.common.base.SuccessClass    import SuccessClass
from success.common.tools.SuccessStructs import SuccessStructs

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessOutputModel ( SuccessClass ) :
  """
  Base output model for UI model generation.

  Provides default implementations for action URL and
  UI model schema generation.
  """


  def __init__ ( self ) -> None :
    """
    Initialize the output model.
    """
    super ().__init__ ()


  def action ( self ) -> str :
    """
    Get the action URL.

    Returns:
      str: Default action URL.
    """
    return "http://synthetos.nexaiideon.ai:5000/dashboard"


  def uiModel ( self ) -> list :
    """
    Generate the UI model schema.

    Returns:
      list: List of UI model field schemas.
    """
    _uiModel = list ()
    _uiModel.append ( SuccessStructs.jsonInputSchema ( 'id', 'ID', '', 'input', '', 'False', 1 ) )
    _uiModel.append ( SuccessStructs.jsonSelectBooleanSchema ( 'enabled', 'Enabled', '', 'False', 2 ) )
    _uiModel.append ( SuccessStructs.jsonInputSchema ( 'created_at', 'Created at', '', 'input', 'True', 'datetime-local', 3 ) )
    _uiModel.append ( SuccessStructs.jsonInputSchema ( 'updated_at', 'Updated at', '', 'input', 'False', 'datetime-local', 4 ) )
    _uiModel.append ( SuccessStructs.jsonSelectBooleanSchema ( 'deleted', 'Deleted', '', 'False', 5 ) )

    return _uiModel

