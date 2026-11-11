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
from flask  import request
from flask  import session
from typing import Any

# Application Libraries / Librerías de la Aplicación
from success.common.SuccessDebug               import SuccessDebug
from success.common.infra.logger.SuccessLogger import SuccessLogger

# Preconditions / Precondiciones


class SuccessSession () :
  """
  Session management utilities for user sessions.

  Provides static methods for creating, managing, and
  destroying user sessions using Flask session storage.
  """


  @staticmethod
  def create ( user, token : str = None ) -> None :
    """
    Create a user session.

    Args:
      user: User object with id, groups, profiles, and roles.
      token (str, optional): Authentication token.
    """
    logger = SuccessLogger ( __name__ )
    session [ 'id' ] = user.id
    session [ 'ipAddress' ] = request.remote_addr
    if ( token is not None ) :
      session [ 'token' ] = token
    groupsUser = user.groups.filter_by ().all ()
    session [ 'group_id' ] = groupsUser [ 0 ].id
    profiles = user.profiles.filter_by ().all ()
    session [ 'profile_id' ] = profiles [ 0 ].id
    roles = user.roles.filter_by ().all ()
    session [ 'role_id' ] = roles [ 0 ].id
    session [ 'loggedin' ] = True


  @staticmethod
  def destroy () -> None :
    """
    Destroy the current session by clearing all session data.
    """
    session.clear ()


  @staticmethod
  def exist ( key : str ) -> bool :
    """
    Check if a session key exists.

    Args:
      key (str): Session key to check.

    Returns:
      bool: True if key does not exist (note: inverted logic).
    """
    return key not in session


  @staticmethod
  def isLogin () -> bool :
    """
    Check if user is logged in.

    Returns:
      bool: True if logged in session exists.
    """
    return ( SuccessSession.exist ( 'loggedin' ) and SuccessSession.get ( 'loggedin' ) is not None )


  @staticmethod
  def get ( key : str ) -> Any :
    """
    Get a session value by key.

    Args:
      key (str): Session key.

    Returns:
      Any: Session value or None.
    """
    return session.get ( key )


  @staticmethod
  def remove ( key : str ) -> None :
    """
    Remove a session key.

    Args:
      key (str): Session key to remove.
    """
    session.pop ( key, None )
    session.modified = True


  @staticmethod
  def set ( key : str, value : Any ) -> None :
    """
    Set a session value.

    Args:
      key (str): Session key.
      value (Any): Value to store.
    """
    session [ key ] = value
    session.modified = True


  @staticmethod
  def sid () -> str :
    """
    Get the session ID.

    Returns:
      str: Session ID.
    """
    return session.sid
