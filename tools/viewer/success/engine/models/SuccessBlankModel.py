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
from sqlalchemy.ext.declarative import declared_attr

# Success Libraries / Librerías Success
from success.engine.models.SuccessBaseModel import SuccessBaseModel
from success.core.SuccessContext            import SuccessContext
from success.engine.models.SuccessFields    import SuccessFields
from success.engine.models.SuccessRelations import SuccessRelations
from success.common.tools.SuccessDatetime   import SuccessDatetime

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessBlankModel ( SuccessBaseModel ) :
  """
  Blank model extending SuccessBaseModel.

  Provides an empty model that inherits all base functionality
  for custom model implementations.
  """
  pass
