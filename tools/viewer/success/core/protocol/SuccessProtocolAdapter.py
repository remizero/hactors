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
from abc   import abstractmethod
from flask import Blueprint

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass
from success.core.SuccessBuildContext import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessProtocolAdapter ( SuccessClass ) :
    """
    Base adapter for endpoint protocols.

    Defines the common interface for all protocol adapters
    (view, restful, default). Each adapter is responsible for registering
    endpoints in a Flask blueprint according to its specific protocol.

    Usage:
        class CustomProtocolAdapter(SuccessProtocolAdapter):
            def register(self, buildContext, blueprint, options):
                # Custom implementation
                pass
    """


    def __init__ ( self ) -> None :
        """
        Initialize the protocol adapter.

        Note:
            Adapters are stateless and can be reused.
        """
        super ().__init__ ()


    @abstractmethod
    def register ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, options : dict ) -> None :
        """
        Register an endpoint in the blueprint according to the specific protocol.

        Args:
            buildContext: Build context with application configuration.
            blueprint: Flask blueprint where the endpoint will be registered.
            options: Dictionary with specific endpoint configuration.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError ()
