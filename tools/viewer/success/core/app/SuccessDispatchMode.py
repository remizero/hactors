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
from enum import Enum

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessDispatchMode ( str, Enum ) :
  """
  Dispatch mode enumeration for multiApp applications.

  Defines available modes for application routing
  in the Success system.

  Available modes:
  ------------------
  - SUBDOMAIN: Dispatch based on subdomains (app1.domain.com)
  - PATH: Dispatch based on route prefixes (/app1, /app2)
  - STANDARD: Standard dispatch with DispatcherMiddleware

  Usage:
  ------
  # Check mode
  if mode == SuccessDispatchMode.SUBDOMAIN:
      # Configure subdomain dispatch
      pass

  # Compare with string
  mode = SuccessDispatchMode("subdomain")
  mode == "subdomain"  # True

  Note:
    - Mode is configured via SUCCESS_APP_MODE
    - Each mode requires specific Flask configuration
  """
  SUBDOMAIN = "subdomain"
  PATH      = "path"
  STANDARD  = "standard"
