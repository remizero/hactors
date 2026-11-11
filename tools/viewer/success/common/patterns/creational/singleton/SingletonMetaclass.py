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
from abc       import ABCMeta
from threading import Lock

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SingletonMetaclass ( ABCMeta ) :

  _instances      = {}
  _lock    : Lock = Lock ()
  _module  : str  = None
  _scope   : str  = None
  _context : str  = None


  def __call__ ( cls, *args, **kwargs ) :
    _scope  = kwargs.pop ( "scope", None )
    _module = kwargs.pop ( "module", None )
    key = ( cls, _module, _scope ) if _scope and _module else cls

    with cls._lock :
      if key not in cls._instances :
        instance = super ().__call__ ( *args, module = _module, scope = _scope, **kwargs )

        if not hasattr ( instance, 'customInit' ) :
          raise TypeError ( f"{cls.__name__} must implement a 'customInit' method" )

        cls._instances [ key ] = instance

    return cls._instances [ key ]
