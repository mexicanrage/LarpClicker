#!/bin/bash

place=$(pwd)

echo "Installing"

sudo cat <<EOF >/usr/bin/larpclicker
  #!/bin/bash

  source $place/venv/bin/activate
  python3 $place/main.py
EOF

sudo chmod +x /usr/bin/larpclicker

echo "installed as 'larpclicker'"
