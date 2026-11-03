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
from abc  import abstractmethod
from copy import deepcopy

# Success Libraries / Librerías Success
from success.engine.io.SuccessOutputModelContract import SuccessOutputModelContract
from success.common.tools.SuccessStructs          import SuccessStructs

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessRichOutputModel ( SuccessOutputModelContract ) :
  """
  Rich output model with action and UI model support.

  Extends canonical output with action URL, data, and
  UI model schema for rich client interactions.
  """


  def __init__ ( self ) :
    """
    Initialize the rich output model.
    """
    super ().__init__ ()


  def build ( self, canonicalOutput : dict ) -> dict :
    """
    Build rich output from canonical format.

    Args:
      canonicalOutput: Canonical output dictionary.

    Returns:
      dict: Built output with action, data, and UI model.
    """
    output = deepcopy ( canonicalOutput )

    rich = SuccessStructs.successRichSchema ()
    rich [ "action" ]  = self.action ()
    rich [ "data" ]    = deepcopy ( output.get ( "data" ) )
    rich [ "uimodel" ] = deepcopy ( self.uiModel () )

    output [ "data" ]  = rich
    return output


  @abstractmethod
  def action ( self ) -> str :
    """
    Get the action URL.

    Returns:
      str: Action URL.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ()


  @abstractmethod
  def uiModel ( self ) -> list :
    """
    Generate the UI model schema.

    Returns:
      list: List of UI model field schemas.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ()
