# simple-udp-communicator

[![CircleCI](https://circleci.com/gh/65usami/simple-udp-communicator/tree/master.svg?style=svg)](https://circleci.com/gh/65usami/simple-udp-communicator/tree/master)

## Feature

Check UDP comminication easily.

![mac_raspberrypi](https://github.com/65usami/simple-udp-communicator/blob/master/imgs/mac_raspberrypi.png)

![demo_simple_udp_communicator](https://github.com/65usami/simple-udp-communicator/blob/master/imgs/demo_simple_udp_communicator.gif)

## Requirements

python 3.4.0 more

## Supports

MacOS, Linux, Raspberry Pi, Windows

## Usage

**Server**
```
python server.py PORT

# e.g.
# python server.py 13001
```

**Client**
```
python client.py 'IP ADDRESS' PORT

# e.g.
# python client.py '192.168.1.10' 13001
```
## Options

**Server**
```
python server.py PORT -l
```
- `-l` :Repeat server.py. Close by `Ctrl + c`

**Client**
```
python client.py 'IP ADDRESS' PORT MAX_MBPS DURATION_SEC_TIME MTU_SIZE

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
