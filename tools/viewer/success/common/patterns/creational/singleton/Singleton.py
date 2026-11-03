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
from abc   import ABC
from abc   import abstractmethod
from flask import Flask

# Application Libraries / Librerías de la Aplicación
from success.common.patterns.creational.singleton.SingletonMetaclass import SingletonMetaclass

# Preconditions / Precondiciones


class Singleton ( ABC, metaclass = SingletonMetaclass ) :

  _initialized : bool = False


  @abstractmethod
  def customInit ( self, app : Flask = None, *args, **kwargs ) :
    raise NotImplementedError ( "customInit() must be implemented by subclass." )
