import os

# Success resuelve apps/ y el logger respecto al directorio de arranque, y el
# viewer detecta la raíz de HACTORS subiendo desde ese mismo directorio. Fijarlo
# al de este archivo hace que ambos dependan de dónde está el viewer y no de
# desde dónde se lance.
os.chdir ( os.path.dirname ( os.path.abspath ( __file__ ) ) )

from success.Success import Success

success = Success ()
success.create ()
app = success.getApp ()


if __name__ == "__main__" :
  success.run ()
