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
from success.core.protocol.SuccessProtocolAdapter        import SuccessProtocolAdapter
from success.core.protocol.SuccessDefaultProtocolAdapter import SuccessDefaultProtocolAdapter
from success.core.protocol.SuccessViewProtocolAdapter    import SuccessViewProtocolAdapter
from success.core.SuccessBuildContext                    import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessProtocolFactory:
  """
  Protocol adapter factory for endpoints.

  Selects and creates the appropriate protocol adapter according to the
  endpoint type (view, restful, default).

  Usage:
      adapter = SuccessProtocolFactory.getProtocolAdapter('view')
      adapter.register(ctx, blueprint, options)
  """


  @staticmethod
  def getProtocolAdapter ( protocol : str ) -> SuccessProtocolAdapter :
    """
    Get a protocol adapter instance according to the requested type.

    Args:
      protocol: Protocol type ('view', 'restful', or any other for default).

    Returns:
      SuccessProtocolAdapter: Instance of the corresponding adapter.

    Example:
      view_adapter = SuccessProtocolFactory.getProtocolAdapter('view')
      rest_adapter = SuccessProtocolFactory.getProtocolAdapter('restful')
      default_adapter = SuccessProtocolFactory.getProtocolAdapter('custom')
    """
    if protocol.lower () == "view" :
      return SuccessViewProtocolAdapter ()

    elif protocol.lower () == "restful" :
      # Se resuelve aquí y no arriba: flask_restful no debe ser requisito de una
      # aplicación que solo sirve vistas.
      from success.core.protocol.SuccessRestProtocolAdapter import SuccessRestProtocolAdapter

      return SuccessRestProtocolAdapter ()
      
    else :
      return SuccessDefaultProtocolAdapter ()
