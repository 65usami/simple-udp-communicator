# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 bpyamasinn.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import socket
import time
import datetime
import json


class UdpReceiver:
    def __init__(self, port=13001, is_loop=False):
        self.__port = int(port)
        self.__is_loop = is_loop
        self.__udp_socket = None
        self.__sent_data_total_count = 0
        self.__received_data_total_count = 0
        self.__received_data_total_bytes_size = 0
        self.__from_ip = '127.0.0.1'
        self.__from_port = 0

    def execute(self):
        try:
            while True:
                self.__print_header()
                self.__execute_udp_receiver()
                self.__print_end_results()
                if self.__is_loop:
                    time.sleep(1)
                else:
                    break
        except KeyboardInterrupt:
            pass  # kill by SIGINT
        finally:
            self.__close_udp_socket()

        return self.__received_data_total_count, self.__to_bps(
            self.__received_data_total_bytes_size)

    def __print_received_data_info(self, data, received_data_count,
                                   received_data_size):
        datetime_str = data[0:4]
        datetime_str += '-' + data[4:6]
        datetime_str += '-' + data[6:8]
        datetime_str += '-' + data[8:10]
        datetime_str += ':' + data[10:12]
        datetime_str += ':' + data[12:14]
        print(datetime_str, "{:,}".format(received_data_count),
              "{:,}".format(self.__to_bps(received_data_size)))

    def __execute_udp_receiver(self):
        received_data_dict = {}
        self.__udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__udp_socket.settimeout(2.0)
        self.__udp_socket.bind(('', self.__port))

        self.__sent_data_total_count = 0
        self.__received_data_total_count = 0
        self.__received_data_total_bytes_size = 0
        received_data_dict.clear()

        self.__print_header_process()
        while True:
            is_socket_error = False
            is_socket_timeout = False
            try:
                bytes_data, address = self.__udp_socket.recvfrom(1500)
            except socket.timeout:
                is_socket_timeout = True
            except socket.herror as eh:
                is_socket_error = True
                print(eh)
            except socket.gaierror as eg:
                is_socket_error = True
                print(eg)

            if is_socket_error:
                break

            if is_socket_timeout:
                continue

            self.__from_ip = address[0]
            self.__from_port = address[1]

            data = bytes_data.decode('utf-8')
            header_size = int(data[0:4])
            header_str_dict = data[4:4 + header_size]
            header_dict = json.loads(header_str_dict)

            datetime_key = header_dict['DatetimeKey']
            is_first = header_dict['IsFirst']
            is_end = header_dict['IsEnd']

            if is_end:
                self.__sent_data_total_count = header_dict['TotalSentCount']
                break

            if datetime_key in received_data_dict:
                received_data_dict[datetime_key].append(len(bytes_data))
            else:
                received_data_dict[datetime_key] = [len(bytes_data)]

            if len(received_data_dict.keys()) > 2:
                first_key = next(iter(received_data_dict))
                self.__calc_received_data(first_key, received_data_dict)

        for key in list(received_data_dict):
            self.__calc_received_data(key, received_data_dict)

    def __to_bps(self, byte_size):
        return byte_size * 8

    def __extract_received_data_dict(self, key, received_data_dict):
        received_data_sizes = received_data_dict[key]
        sum_received_data_size = sum(received_data_sizes)
        sum_received_data_count = len(received_data_sizes)
        del received_data_dict[key]
        return sum_received_data_count, sum_received_data_size

    def __calc_received_data(self, datetime_key, received_data_dict):
        sum_received_data_count, sum_received_data_size = self.__extract_received_data_dict(
            datetime_key, received_data_dict)
        self.__calc_total_results(sum_received_data_count,
                                  sum_received_data_size)
        self.__print_received_data_info(datetime_key, sum_received_data_count,
                                        sum_received_data_size)

    def __calc_total_results(self, sum_received_data_count,
                             sum_received_data_size):
        self.__received_data_total_count += sum_received_data_count
        self.__received_data_total_bytes_size += sum_received_data_size

    def __close_udp_socket(self):
        if not self.__udp_socket:
            return
        try:
            self.__udp_socket.close()
        except Exception as e:
            pass

    def __print_header(self):
        print()
        print("UDP Server")
        print()
        print("Parameters:")
        print("Receive Port :", self.__port)

    def __print_header_process(self):
        print()
        print("Results:")
        print("datetime", "received count", "received size(bps)")
        print("--------", "----------", "--------------")

    def __print_end_results(self):
        print()
        print("From ip:", self.__from_ip)
        print("Bind port:", self.__port)
        print("Source port:", self.__from_port)
        print(
            "Total received data size(bps):", "{:,}".format(
                self.__to_bps(self.__received_data_total_bytes_size)))
        print("Total received data count:",
              "{:,}".format(self.__received_data_total_count))
        rate = self.__received_data_total_count / self.__sent_data_total_count if self.__sent_data_total_count else 0
        print("Total received data rate:", "{:.2%}".format(rate))
        print("---")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        params_dict = {}
        params_dict.update(port=sys.argv[1])

        if len(sys.argv) > 2:
            is_loop = True if str(sys.argv[2]) == '-l' else False
            params_dict.update(is_loop=is_loop)

        udp_receiver = UdpReceiver(**params_dict)
        udp_receiver.execute()
    else:
        print("Invalid arguments!!")
        print('Usage: python {0} 13001'.format(sys.argv[0]))
