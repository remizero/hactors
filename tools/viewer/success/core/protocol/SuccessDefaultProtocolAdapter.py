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
from flask import Blueprint

# Success Libraries / Librerías Success
from success.core.protocol.SuccessProtocolAdapter import SuccessProtocolAdapter
from success.core.SuccessBuildContext             import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessDefaultProtocolAdapter ( SuccessProtocolAdapter ) :
    """
    Default protocol adapter for non-standard endpoints.

    Used when the endpoint protocol is not 'view' or 'restful'.
    Registers the endpoint directly using the provided options
    without additional configuration building.

    Usage:
        adapter = SuccessDefaultProtocolAdapter()
        adapter.register(ctx, blueprint, options)
    """


    def __init__ ( self ) -> None :
        """
        Initialize the default protocol adapter.
        """
        super ().__init__ ()


    def register ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, kwargs : dict ) -> None :
        """
        Register an endpoint using direct configuration.

        This adapter does not perform additional options building.
        Registers the URL rule directly in the blueprint using
        the provided parameters.

        Args:
            buildContext: Build context (not used in this adapter).
            blueprint: Flask blueprint where the endpoint will be registered.
            kwargs: Dictionary with parameters for add_url_rule
                   (rule, endpoint, view_func, methods, etc.).

        Note:
            This adapter is useful for custom endpoint registrations
            or for non-standard protocols.
        """
        blueprint.add_url_rule ( **kwargs )
