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
from flask            import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy       import MetaData
from sqlalchemy.orm   import relationship

# Success Libraries / Librerías Success
from success.common.base.SuccessExtension                   import SuccessExtension
from success.engine.extensions.proxies.SuccessProxyDatabase import db

# Preconditions / Precondiciones


class SuccessDatabaseExtension ( SuccessExtension ) :
  """
  Database extension for the Success framework.

  Integrates Flask-SQLAlchemy for database operations
  and ORM functionality.
  """


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the Database extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    self._extension = db


  def metadata ( self ) -> MetaData :
    """
    Get and reflect database metadata.

    Returns:
      MetaData: Reflected database metadata.
    """
    metadata = MetaData ()
    metadata.reflect ( self._extension.engine )
    return metadata
