#!/bin/sh

function termination() {
  deactivate
}

trap 'termination'  {1,2,3,15}

source venv/bin/activate
python client.py $1 $2
deactivate
