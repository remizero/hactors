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
from colorama import init as colorama_init, Fore, Style

# Success Libraries / Librerías Success

# Preconditions / Precondiciones



class SuccessColor () :

  # Colores base
  PURPLE  = Fore.MAGENTA
  CYAN    = Fore.CYAN
  GREEN   = Fore.GREEN
  YELLOW  = Fore.YELLOW
  RED     = Fore.RED
  BLUE    = Fore.BLUE
  WHITE   = Fore.WHITE
  GRAY    = Fore.LIGHTBLACK_EX

  # Estilos
  BOLD    = Style.BRIGHT
  NORMAL  = Style.NORMAL
  DIM     = Style.DIM
  RESET   = Style.RESET_ALL

  HEADER  = '\033[95m'
  OKBLUE  = '\033[94m'
  OKCYAN  = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL    = '\033[91m'
  WHITE   = '\033[97m'
  GRAY    = '\033[90m'
  ENDC    = '\033[0m'


  @staticmethod
  def decorate ( msg, fg = WHITE, style = NORMAL ) -> str :
    return f"{fg}{style}{msg}{SuccessColor.RESET}"


  @staticmethod
  def methodColor ( method : str ) -> str :
    color = {
      'GET'    : SuccessColor.OKGREEN,
      'POST'   : SuccessColor.WARNING,
      'PUT'    : SuccessColor.OKBLUE,
      'DELETE' : SuccessColor.FAIL
    }.get ( method.upper (), SuccessColor.WHITE )
    return SuccessColor.decorate ( method, color )


  @staticmethod
  def info ( msg : str ) -> str :
    return f"{SuccessColor.CYAN}{SuccessColor.BOLD}{msg}{SuccessColor.RESET}"


  @staticmethod
  def warn ( msg : str ) -> str :
    return f"{SuccessColor.YELLOW}{SuccessColor.BOLD}{msg}{SuccessColor.RESET}"


  @staticmethod
  def error ( msg : str ) -> str :
    return f"{SuccessColor.RED}{SuccessColor.BOLD}{msg}{SuccessColor.RESET}"


  @staticmethod
  def success ( msg : str ) -> str :
    return f"{SuccessColor.GREEN}{SuccessColor.BOLD}{msg}{SuccessColor.RESET}"


  @staticmethod
  def level ( msg : str ) -> str :
    return f"{SuccessColor.WHITE}{msg}{SuccessColor.RESET}"


  @staticmethod
  def tag ( msg : str ) -> str :
    return f"{SuccessColor.WARNING}{msg}{SuccessColor.RESET}"


  @staticmethod
  def title ( msg : str ) -> str :
    return f"{SuccessColor.PURPLE}{SuccessColor.BOLD}{msg}{SuccessColor.RESET}"


  @staticmethod
  def subtle ( msg : str ) -> str :
    return f"{SuccessColor.GRAY}{msg}{SuccessColor.RESET}"
