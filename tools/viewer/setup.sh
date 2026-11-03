#!/usr/bin/env bash
set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

for env in success/.env apps/hactors/.env; do
  if [ -f "$env" ]; then
    echo "· $env ya existe, se conserva"
  else
    cp "${env%.env}env.example" "$env"
    echo "· creado $env"
  fi
done

if [ ! -d .venv ]; then
  python3 -m venv .venv
  echo "· creado .venv"
fi

./.venv/bin/pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet -r requirements.txt
./.venv/bin/pip install --quiet -e ../cli
echo "· dependencias instaladas"

cat <<'EOF'

Arrancar el viewer:

  cd tools/viewer && ./.venv/bin/python wsgi.py

Abre http://127.0.0.1:5000/

EOF
