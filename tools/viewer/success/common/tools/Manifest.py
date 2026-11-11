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

# success/core/creed.py
from random import choice


def creed_lines () -> list [ str ] :
  return [
    "Success is better than failure.",
    "Errors are part of the contract.",
    "Clarity beats flexibility.",
    "If you break it, you bought it.",
    "Outside this framework your failure is success-ful.",
    "Aunque sea un failure, siempre será un Success.",
    "Te doy flexibilidad, pero tú no te gobiernas solo.",
    "Si te sales del contrato, prepárate pa’ reventar.",
    "Dentro del marco hay orden. Fuera, solo caos.",
    "No hay magia, solo contrato.",
    "Or run, or climb. Success te avisó.",
    "Success no se rompe, se expone.",
  ]


def random_creed_line () -> str :
  return choice ( creed_lines () )

def print_success_creed () -> None :
  """Print the sacred manifesto of the Success framework at startup."""

  creed = creed_lines ()

  border = "═" * 60
  print ( "\n" + border )
  print ( "             🧱 SUCCESS FRAMEWORK MANIFIESTO 🧱" )
  print ( border )
  for line in creed :
    print ( f" • {line}" )
  print ( border + "\n" )


def ascii_warning () -> None :
  print ( """
=========================
=========================
   TE LO DIJE, POR AHÍ NO!
=========================
=========================
""" )


def ascii_warning1 () -> None :
  print ( """
┌────────────────────────────┐
│  SUCCESS FRAMEWORK v2.0    │
│   Build apps. With soul.   │
└────────────────────────────┘
""" )


def ascii_warning2 () -> None :
  print ( """
┌───────────────────────────────────────────┐
│        ✅ SUCCESSFUL RESPONSE             │
├───────────────────────────────────────────┤
│  status  : success                        │
│  message : Datos obtenidos correctamente  │
│  data    : {...}                          │
└───────────────────────────────────────────┘
""" )


def ascii_warning3 () -> None :
  print ( """
┌────────────────────────────────────┐
│   ❌ ERROR: VALIDATION             │
├────────────────────────────────────┤
│  message : Campo 'email' inválido  │
└────────────────────────────────────┘
""" )
