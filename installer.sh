#!/bin/bash

place=$(pwd)

echo "Installing"

python3 -m venv venv

source venv/bin/activate
pip install -r requirements.txt

sudo cat <<EOF >/usr/bin/larpclicker
  #!/bin/bash

  source $place/venv/bin/activate
  python3 $place/main.py
EOF

sudo chmod +x /usr/bin/larpclicker

echo "installed as 'larpclicker'"
