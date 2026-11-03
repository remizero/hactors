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
# from success.core.SuccessContext                    import SuccessContext
from success.engine.models.SuccessFields                    import SuccessFields
from success.engine.models.SuccessRelations                 import SuccessRelations
from success.common.tools.SuccessDatetime                   import SuccessDatetime
from success.engine.extensions.proxies.SuccessProxyDatabase import db as database

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
# database = SuccessContext ().getExtension ( "SuccessDatabaseExtension" )
# if database is None :
#   raise RuntimeError ( "La extensión Sqlalchemy no está cargada" )


# TODO How to perform parameterized searches
class SuccessBaseModel ( database.Model ) :
  """
  Base model for all SQLAlchemy models in the Success framework.

  Provides common CRUD operations, timestamps, and soft delete
  functionality for all derived models.

  Attributes:
    __abstract__ (bool): Marks this class as abstract.
    id: Primary key column.
  """

  __abstract__ = True
  id           = SuccessFields.primaryKey ()


  @declared_attr
  def __tablename__ ( cls ) :
    """
    Generate table name from class name.

    Returns:
      str: Pluralized snake_case table name.
    """
    relatorAux = SuccessRelations ( cls.__name__ )
    return relatorAux.pluralName


  def __init__ ( self, **kwargs ) :
    """
    Initialize the model with keyword arguments.

    Args:
      **kwargs: Attribute values to set.
    """
    self.inputData ( **kwargs )


  def inputData ( self, **kwargs ) :
    """
    Set model attributes from keyword arguments.

    Args:
      **kwargs: Attribute values to set.
    """
    for kwarg in kwargs :
      setattr ( self, kwarg, kwargs [ kwarg ] )


  def insert ( self ) :
    """
    Insert the model instance into the database.

    Sets created_at timestamp and saves the instance.
    """
    self.created_at = SuccessDatetime.getNow ()
    self.__save ()


  def update ( self ) :
    """
    Update the model instance in the database.

    Sets updated_at timestamp and saves the instance.
    """
    self.updated_at = SuccessDatetime.getNow ()
    self.__save ()


  def delete ( self ) :
    """
    Soft delete the model instance.

    Sets updated_at timestamp and deleted flag, then saves.
    """
    self.updated_at = SuccessDatetime.getNow ()
    self.deleted    = False
    self.__save ()


  def findAll ( self ) :
    """
    Find all instances of this model.

    Returns:
      list: All model instances.
    """
    return self.query.all ()


  def findById ( self ) :
    """
    Find instance by its ID.

    Returns:
      The model instance or None.
    """
    return self.query.get ( self.id )


  def findByName ( self ) :
    """
    Find instance by name attribute.

    Returns:
      The model instance or None.
    """
    return self.query.filter_by ( name = self.name ).first ()


  def findByFilters ( self, many : bool = True, **kwargs ) :
    """
    Find instances by filter criteria.

    Args:
      many (bool): If True, return all matches. If False, return first.
      **kwargs: Filter criteria.

    Returns:
      list or object: Matching instances or validation error.
    """
    retorno = self.__validateFilters ( **kwargs )
    if retorno == True :
      kwargs [ 'deleted' ] = False
      if ( many ) :
        return self.query.filter_by ( **kwargs ).all ()

      else :
        return self.query.filter_by ( **kwargs ).first ()

    return retorno


  def scalar ( self, **kwargs ) :
    """
    Get scalar value from query.

    Args:
      **kwargs: Filter criteria.

    Returns:
      Scalar value or validation error.
    """
    retorno = self.__validateFilters ( **kwargs )
    if retorno == True :
      kwargs [ 'deleted' ] = False
      return self.query.filter_by ( **kwargs ).scalar ()

    return retorno


  def rollback ( self ) :
    """
    Rollback the current database session.
    """
    database.extension.session.rollback ()


  def __save ( self ) :
    """
    Save the instance to the database.

    Adds to session and commits the transaction.
    """
    database.extension.session.add ( self )
    database.extension.session.commit ()


  def toJson ( self ) :
    """
    Convert model to JSON-compatible dictionary.

    Returns:
      dict: Dictionary representation without SQLAlchemy state.
    """
    fe_dict = self.__dict__.copy ()
    del fe_dict [ '_sa_instance_state' ]

    return fe_dict


  def as_dict ( self ) :
    """
    Convert model to dictionary of column values.

    Returns:
      dict: Dictionary with column names and values.
    """
    return { c.name: getattr ( self, c.name ) for c in self.__table__.columns }


  def __validateFilters ( self, **kwargs ) :
    """
    Validate filter criteria against model attributes.

    Args:
      **kwargs: Filter criteria to validate.

    Returns:
      bool: True if valid, error description otherwise.
    """
    # Get class attributes,
    # Verify that **kwargs indices match class attributes
    # If at least one **kwargs index doesn't match, emit error and stop method execution
    return True


  @classmethod
  def get_by_id ( cls, id ) :
    """
    Get model instance by ID (class method).

    Args:
      id: Instance ID.

    Returns:
      The model instance or None.
    """
    return cls.query.get ( id )


  @classmethod
  def list_all ( cls ) :
    """
    List all non-deleted instances (class method).

    Returns:
      list: All non-deleted model instances.
    """
    return cls.query.filter_by ( deleted = False ).all ()


  @classmethod
  def query ( cls, filters : dict, many : bool = True ) :
    """
    Query instances with filters (class method).

    Args:
      filters (dict): Filter criteria.
      many (bool): If True, return all. If False, return first.

    Returns:
      list or object: Matching instances.
    """
    filters [ "deleted" ] = False
    q = cls.query.filter_by ( **filters )
    return q.all () if many else q.first ()


  @classmethod
  def create_from_payload ( cls, payload : dict ) :
    """
    Create instance from payload dictionary (class method).

    Args:
      payload (dict): Instance data.

    Returns:
      The created model instance.
    """
    instance = cls ( **payload )
    instance.insert ()
    return instance
