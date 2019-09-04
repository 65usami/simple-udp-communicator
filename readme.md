# simple-udp-communicator

[![CircleCI](https://circleci.com/gh/65usami/simple-udp-communicator/tree/master.svg?style=svg)](https://circleci.com/gh/65usami/simple-udp-communicator/tree/master)

## Feature

Check UDP comminication easily.

![mac_raspberrypi](https://github.com/65usami/simple-udp-communicator/blob/master/imgs/mac_raspberrypi.png)

![demo_simple_udp_communicator](https://github.com/65usami/simple-udp-communicator/blob/master/imgs/demo_simple_udp_communicator.gif)

## Usage

**MacOS, Linux(Ubuntu, CentOS, etc..), Raspberry Pi**

_Server_
```
server.sh PORT

# e.g.
# server.sh 13001
```

_Client_
```
client.sh 'IP ADDRESS' PORT

# e.g.
# client.sh '192.168.1.10' 13001
```

**Windows**

_Server_
```
server.bat PORT

# e.g.
# server.bat 13001
```

_Client_
```
client.bat 'IP ADDRESS' PORT

# e.g.
# client.bat '192.168.1.10' 13001
```

## Options

- Only python enabled

- venv for Windows
    - `venv_windows\Scripts\activate.bat`
    - `venv_windows\Scripts\deactivate.bat`


_Server_
```
source venv/bin/activate
python server.py PORT -l
deactivate
```
- `-l` :Repeat server.py. Close by `Ctrl + c`

_Client_
```
source venv/bin/activate
python client.py 'IP ADDRESS' PORT MAX_MBPS DURATION_SEC_TIME MTU_SIZE
deactivate

# e.g.
# python client.py '192.168.1.10' 13001 2.0 3 1390
```
- `MAX_MBPS` : Maximum upload speeds of per seconds.
- `DURATION_SEC_TIME` : Duration of upload time by seconds.
- `MTU_SIZE` : MTU size.

## License

MIT

##  Author

Kenichi Usami
