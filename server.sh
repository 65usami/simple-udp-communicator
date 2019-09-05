#!/bin/sh

uname_m==`uname -m`
processor=${uname_m:0:3}
platform="$OSTYPE"

if [ processor = 'arm' ]; then
 # Raspberry Pi
 source venvs/venv_raspberry_pi/bin/activate
 python server.py $1
 deactivate
else
 function termination() {
   deactivate
 }
 trap 'termination'  {1,2,3,15}

 if [[ platform == "darwin"* ]]; then
  # Mac
  source venvs/venv_mac/bin/activate
  python server.py $1
  deactivate
 else
  # Linux
  source venvs/venv_linux/bin/activate
  python server.py $1
  deactivate
 fi

fi