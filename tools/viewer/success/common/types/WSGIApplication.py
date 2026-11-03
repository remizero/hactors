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
# from sys import 
from types  import TracebackType
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Protocol
from typing import Text
from typing import Tuple
from typing import Type
from typing import Union

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
_ExcInfo    = Tuple [ Type [ BaseException ], BaseException, TracebackType ]
_OptExcInfo = Union [ _ExcInfo, Tuple [ None, None, None ] ]

class StartResponse ( Protocol ) :
  def __call__ (
    self,
    status   : str,
    headers  : List [ Tuple [ str, str ] ],
    exc_info : Optional [ _OptExcInfo ] = ...
  ) -> Callable [ [ bytes ], Any ] :
    ...

WSGIEnvironment = Dict [ str, Any ]
WSGIApplication = Callable [ [ WSGIEnvironment, StartResponse ], Iterable [ bytes ] ]
