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
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import DECIMAL
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

# Application Libraries / Librerías de la Aplicación
from success.common.tools.SuccessStrings import SuccessStrings

# Preconditions / Precondiciones


class SuccessFields () :
  """
  Factory for creating SQLAlchemy column fields.

  Provides static methods for creating common column types
  with standardized configurations.
  """


  @staticmethod
  def boolean ( nullable : bool = False, default = False ) -> Column :
    """
    Create a boolean column.

    Args:
      nullable (bool): Whether null values are allowed.
      default: Default value.

    Returns:
      Column: Boolean column.
    """
    return Column (
      Boolean,
      nullable = nullable,
      default  = default
    )


  @staticmethod
  def date ( nullable : bool = False, default = False ) -> Column :
    """
    Create a date column.

    Args:
      nullable (bool): Whether null values are allowed.
      default: Default value.

    Returns:
      Column: Date column.
    """
    if default:
      return Column (
        Date,
        nullable = nullable,
        default  = default
      )
    return Column (
      Date,
      nullable = nullable
    )


  @staticmethod
  def datetime ( nullable : bool = False, default = False ) -> Column :
    """
    Create a datetime column with timezone support.

    Args:
      nullable (bool): Whether null values are allowed.
      default: Default value.

    Returns:
      Column: DateTime column.
    """
    if default :
      return Column (
        DateTime ( timezone = True ),
        nullable = nullable,
        default  = default
      )
    return Column (
      DateTime ( timezone = True ),
      nullable = nullable
    )


  @staticmethod
  def decimal ( size : int, decimal_size, nullable : bool = False, default = None ) -> Column :
    """
    Create a decimal column.

    Args:
      size (int): Total number of digits.
      decimal_size: Number of decimal places.
      nullable (bool): Whether null values are allowed.
      default: Default value.

    Returns:
      Column: Decimal column.
    """
    return Column (
      DECIMAL ( size, decimal_size ),
      nullable = nullable,
      default  = default
    )


  @staticmethod
  def float ( size : int, decimal_size, nullable : bool = False, default = None ) -> Column :
    """
    Create a float column.

    Args:
      size (int): Total number of digits.
      decimal_size: Number of decimal places.
      nullable (bool): Whether null values are allowed.
      default: Default value.

    Returns:
      Column: Float column.
    """
    return Column (
      Float ( size, decimal_size ),
      nullable = nullable,
      default  = default
    )


  @staticmethod
  def foreignKey ( modelName : str, nullable : bool = False, primaryKey : bool = False ) -> Column :
    """
    Create a foreign key column.

    Args:
      modelName (str): Name of the referenced model.
      nullable (bool): Whether null values are allowed.
      primaryKey (bool): Whether this is a primary key.

    Returns:
      Column: Foreign key column.
    """
    tableName = SuccessStrings.toPlural ( SuccessStrings.snakeCase ( modelName ) )
    return Column (
      Integer,
      ForeignKey (
        '{}.id'.format ( tableName )
      ),
      nullable    = nullable,
      primary_key = primaryKey,
      comment     = '{} ID'.format ( tableName )
    )


  @staticmethod
  def integer ( nullable : bool = False, default = 0 ) -> Column :
    """
    Create an integer column.

    Args:
      nullable (bool): Whether null values are allowed.
      default: Default value.

    Returns:
      Column: Integer column.
    """
    return Column (
      Integer,
      nullable = nullable,
      default  = default
    )


  @staticmethod
  def primaryKey () -> Column :
    """
    Create a primary key column.

    Returns:
      Column: Auto-incrementing integer primary key.
    """
    return Column (
      Integer,
      primary_key   = True,
      autoincrement = True,
      index         = True
    )


  @staticmethod
  def string ( size : int, nullable : bool = False, unique : bool = False ) -> Column :
    """
    Create a string column.

    Args:
      size (int): Maximum string length.
      nullable (bool): Whether null values are allowed.
      unique (bool): Whether values must be unique.

    Returns:
      Column: String column.
    """
    return Column (
      String ( size ),
      nullable = nullable
    )


  @staticmethod
  def text ( nullable : bool = False ) -> Column :
    """
    Create a text column for large text data.

    Args:
      nullable (bool): Whether null values are allowed.

    Returns:
      Column: Text column.
    """
    return Column (
      Text (),
      nullable = nullable
    )
