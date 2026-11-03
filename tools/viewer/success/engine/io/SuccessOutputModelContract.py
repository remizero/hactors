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
from abc import abstractmethod

# Success Libraries / Librerías Success
from success.common.base.SuccessClass    import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessOutputModelContract ( SuccessClass ) :
  """
  Abstract contract for output models.

  Defines the interface that all output models must implement
  for building output from canonical format.

  Attributes:
    _outputModel (dict): Output model data.
  """

  _outputModel : dict = None


  def __init__ ( self ) :
    """
    Initialize the output model contract.
    """
    super ().__init__ ()


  @abstractmethod
  def build ( self, canonicalOutput : dict ) -> dict :
    """
    Build output from canonical format.

    Args:
      canonicalOutput: Canonical output dictionary.

    Returns:
      dict: Built output.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError
