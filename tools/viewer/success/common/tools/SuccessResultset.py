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
from flask_sqlalchemy.model import Model
from typing                 import Any

# Success Libraries / Librerías Success
from success.common.SuccessDebug import SuccessDebug

# Preconditions / Precondiciones


class SuccessResultset () :
  """
  Resultset utilities for converting database results to JSON.

  Provides static methods for converting SQLAlchemy models and
  resultsets to JSON format.
  """

  # @staticmethod
  # def dictToJson ( resultSet ) :
  #   myJsonList = []
  #   if resultSet is dict :
  #     for result in resultSet :
  #       myJsonList.append ( result [ 0 ] )
  #   return myJsonList

  @staticmethod
  def toJson ( resultSet : Any ) -> list :
    """
    Convert a resultset to JSON format.

    Args:
      resultSet: SQLAlchemy model or list of models to convert.

    Returns:
      list: List of JSON-serialized models.
    """

    myJsonList = list ()
    if isinstance ( resultSet, list ) :
      for result in resultSet :
        if issubclass ( result, Model ) :
          myJsonList.append ( result.toJson () )

    elif isinstance ( resultSet, Model ) :
      myJsonList.append ( resultSet.toJson () )

    else :
      # TODO COMO PROCESAR ESTE TIPO DE DATO
      myJsonList.append ( resultSet.toJson () )

    return myJsonList
  
  # @staticmethod
  # def toJson ( resultSet ) :
  #   return resultSet.fetchone () [ 0 ]
