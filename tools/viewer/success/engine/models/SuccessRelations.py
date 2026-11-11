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
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

# Application Libraries / Librerías de la Aplicación
from success.common.tools.SuccessStrings import SuccessStrings

# Preconditions / Precondiciones


class SuccessRelations () :
  """
  Relationship builder for SQLAlchemy model relations.

  Provides methods for defining various types of relationships
  between models (hasOne, hasMany, manyToMany, etc.).

  Attributes:
    modelName (str): Name of the model.
    snakeName (str): Snake_case version of model name.
    pluralName (str): Pluralized snake_case model name.
  """

  modelName  : str = ''
  snakeName  : str = ''
  pluralName : str = ''


  def __init__ ( self, modelName : str ) :
    """
    Initialize the relationship builder.

    Args:
      modelName (str): Name of the model to build relations for.
    """
    self.modelName  = modelName
    self.snakeName  = SuccessStrings.snakeCase ( self.modelName )
    self.pluralName = SuccessStrings.toPlural ( self.snakeName )


  def hasOne ( self, modelNameToRelate : str ) :
    """
    Define a has-one relationship.

    Args:
      modelNameToRelate (str): Name of the related model.

    Returns:
      relationship: SQLAlchemy relationship.
    """
    return relationship (
      modelNameToRelate,
      back_populates = self.pluralName
    )


  def hasMany ( self, modelNameToRelate : str ):
    """
    Define a has-many relationship.

    Args:
      modelNameToRelate (str): Name of the related model.

    Returns:
      relationship: SQLAlchemy relationship with dynamic loading.
    """
    return relationship (
      modelNameToRelate,
      back_populates = self.pluralName,
      lazy           = 'dynamic'
    )


  def manyToMany ( self, modelNameToRelate: str, secondaryTable : str ) :
    """
    Define a many-to-many relationship.

    Args:
      modelNameToRelate (str): Name of the related model.
      secondaryTable (str): Name of the association table.

    Returns:
      relationship: SQLAlchemy many-to-many relationship.
    """
    return relationship (
      modelNameToRelate,
      secondary      = SuccessStrings.toPlural ( SuccessStrings.snakeCase ( secondaryTable ) ),
      back_populates = self.pluralName,
      lazy           = 'dynamic'
    )


  def manyToManyAssociation ( self, modelNameToRelate: str, backPopulates : str ) :
    """
    Define a many-to-many association relationship.

    Args:
      modelNameToRelate (str): Name of the related model.
      backPopulates (str): Name of the back reference.

    Returns:
      relationship: SQLAlchemy association relationship.
    """
    return relationship (
      modelNameToRelate,
      back_populates = backPopulates
    )


  def manyToManySimple ( self, modelNameToRelate: str, secondaryTable : str ) :
    """
    Define a simple many-to-many relationship.

    Args:
      modelNameToRelate (str): Name of the related model.
      secondaryTable (str): Name of the association table.

    Returns:
      relationship: SQLAlchemy many-to-many relationship.
    """
    return relationship (
      modelNameToRelate,
      secondary      = SuccessStrings.toPlural ( SuccessStrings.snakeCase ( secondaryTable ) ),
      back_populates = self.pluralName,
      lazy           = 'dynamic'
    )


  def oneToOne ( self, modelNameToRelate : str ) :
    """
    Define a one-to-one relationship.

    Args:
      modelNameToRelate (str): Name of the related model.

    Returns:
      relationship: SQLAlchemy one-to-one relationship.
    """
    return relationship (
      modelNameToRelate,
      back_populates = self.pluralName,
      uselist        = False
    )


  def oneToMany ( self, modelNameToRelate : str ) :
    """
    Define a one-to-many relationship.

    Args:
      modelNameToRelate (str): Name of the related model.

    Returns:
      relationship: SQLAlchemy one-to-many relationship.
    """
    return relationship (
      modelNameToRelate,
      back_populates = self.pluralName,
      lazy           = 'dynamic'
    )


  def relationalTable ( self, modelNameToRelate : str ) :
    """
    Define a relational table with cascade delete.

    Args:
      modelNameToRelate (str): Name of the related model.

    Returns:
      relationship: SQLAlchemy relationship with backref.
    """
    return relationship (
      modelNameToRelate,
      backref = backref ( self.pluralName, cascade = 'all, delete-orphan' )
    )


  def relationalTable_2 ( self, modelNameToRelate : str, backPopulates : str ) :
    """
    Define a relational table with custom back_populates.

    Args:
      modelNameToRelate (str): Name of the related model.
      backPopulates (str): Name of the back reference.

    Returns:
      relationship: SQLAlchemy relationship.
    """
    return relationship (
      modelNameToRelate,
      back_populates = backPopulates
    )
