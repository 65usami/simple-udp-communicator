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
import math
import json


class UdpSender:
    def __init__(self,
                 ip='127.0.0.1',
                 port=13001,
                 max_mbps=3.0,
                 duration_sec_time=5,
                 mtu_size=1500):
        self.__ip = ip
        self.__port = int(port)
        self.__max_mbps = float(max_mbps)
        self.__max_bps = self.__max_mbps * 1000000
        self.__duration_sec_time = int(duration_sec_time)
        self.__mtu_size = mtu_size

        self.__is_success = True
        self.__udp_socket = None
        self.__sent_data_count = 0
        self.__sent_data_total_bytes_size = 0
        self.__sent_data_total_count = 0

        self.__data = ''.join(['1' for i in range(0, self.__mtu_size)])

    def execute(self):
        try:
            self.__print_header()
            self.__execute_udp_sender()
        except KeyboardInterrupt:
            pass  # kill by SIGINT
        finally:
            self.__close_udp_socket()
            self.__print_end_results()

        return self.__sent_data_total_count, self.__to_bps(
            self.__sent_data_total_bytes_size)

    def __execute_udp_sender(self):
        history_dict = {}
        elapsed_time = 0.0
        last_elapsed_time = 0.0
        last_datetime_key = None
        sent_size = 0
        is_first = True

        self.__udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.__waiting_zero_sec_just(
        )  # Start from zero sec time as possible for easy calc of sent count

        start_time = datetime.datetime.now().timestamp()
        self.__print_header_process()
        now_datetime = datetime.datetime.now()
        while elapsed_time < self.__duration_sec_time:
            if is_first:
                datetime_key, send_data_bytes = self.__create_send_data(
                    now_datetime, is_first=True)
                is_first = False
            else:
                datetime_key, send_data_bytes = self.__create_send_data(
                    now_datetime)
            if self.__is_send_data(send_data_bytes, sent_size):
                sent_result_size = self.__udp_socket.sendto(
                    send_data_bytes, (self.__ip, self.__port))
                sent_size += sent_result_size
                if sent_result_size == len(send_data_bytes):
                    if datetime_key in history_dict:
                        history_dict[datetime_key].append(sent_result_size)
                    else:
                        history_dict[datetime_key] = [sent_result_size]
                else:
                    print("Failed socket.sendto!!")
                    print("Actual size: ", len(send_data_bytes))
                    print("Return size: ", sent_result_size)
                    self.__is_success = False
                    break
            else:
                time.sleep(0.004)

            if last_datetime_key and datetime_key != last_datetime_key:
                sum_sent_result_count, sum_sent_result_size = self.__extract_history_data(
                    last_datetime_key, history_dict)
                self.__calc_total_results(sum_sent_result_count,
                                          sum_sent_result_size)
                self.__print_send_data_info(last_datetime_key,
                                            sum_sent_result_count,
                                            sum_sent_result_size)
            last_datetime_key = datetime_key

            if math.floor(elapsed_time) - math.floor(last_elapsed_time) >= 1:
                sent_size = 0

            now_datetime = datetime.datetime.now()
            last_elapsed_time = elapsed_time
            elapsed_time = self.__calc_elapsed_time(start_time, now_datetime)

        for key in list(history_dict):
            sum_sent_result_count, sum_sent_result_size = self.__extract_history_data(
                key, history_dict)
            self.__calc_total_results(sum_sent_result_count,
                                      sum_sent_result_size)
            self.__print_send_data_info(datetime_key, sum_sent_result_count,
                                        sum_sent_result_size)
        self.__send_end_data(self.__is_success)

    def __is_send_data(self, send_data_bytes, sent_data_size):
        this_send_data_bps = self.__to_bps(len(send_data_bytes))
        if (self.__max_bps -
                this_send_data_bps) > self.__to_bps(sent_data_size):
            return True
        return False

    def __close_udp_socket(self):
        if not self.__udp_socket:
            return
        try:
            self.__udp_socket.close()
        except Exception as e:
            pass

    def __calc_total_results(self, sum_sent_result_count,
                             sum_sent_result_size):
        self.__sent_data_total_count += sum_sent_result_count
        self.__sent_data_total_bytes_size += sum_sent_result_size

    def __extract_history_data(self, key, history_dict):
        sent_result_sizes = history_dict[key]
        sum_sent_result_size = sum(sent_result_sizes)
        sum_sent_result_count = len(sent_result_sizes)
        del history_dict[key]
        return sum_sent_result_count, sum_sent_result_size

    def __send_data(self, now_datetime):
        header = now_datetime.strftime("%Y%m%d%H%M%S")
        send_data_bytes = self.__create_send_data_bytes(header)
        sent_size = self.__udp_socket.sendto(send_data_bytes,
                                             (self.__ip, self.__port))
        return sent_size, header, send_data_bytes

    def __create_send_data(self,
                           now_datetime,
                           is_first=False,
                           is_end=False,
                           total_sent_count=0):
        data_dict = {}
        datetime_key = now_datetime.strftime("%Y%m%d%H%M%S")
        data_dict['DatetimeKey'] = datetime_key
        data_dict['IsFirst'] = is_first
        data_dict['IsEnd'] = is_end
        data_dict['TotalSentCount'] = total_sent_count
        send_header_json_data = json.dumps(data_dict)
        send_header_data = str(
            len(send_header_json_data)).zfill(4) + send_header_json_data
        send_data = (send_header_data + self.__data)[:self.__mtu_size]
        send_data_bytes = send_data.encode('utf-8')
        return datetime_key, send_data_bytes

    def __send_end_data(self, is_success):
        if not is_success:
            return

        now_datetime = datetime.datetime.now()
        datetime_key, send_data_bytes = self.__create_send_data(
            now_datetime,
            is_end=True,
            total_sent_count=self.__sent_data_total_count)
        for i in range(3):
            sent_end_data_result_size = self.__udp_socket.sendto(
                send_data_bytes, (self.__ip, self.__port))
            if sent_end_data_result_size != len(send_data_bytes):
                print("Warning: Failed end data!!")
            time.sleep(0.3)  # interbal udp_socket.sendto

    def __calc_elapsed_time(self, start_time, now_datetime):
        now_time = now_datetime.timestamp()
        elapsed_time = now_time - start_time
        return elapsed_time

    def __create_send_data_bytes(self, header):
        send_data_bytes = ((header +
                            self.__data)[:self.__mtu_size]).encode('utf-8')
        return send_data_bytes

    def __to_bps(self, byte_size):
        return byte_size * 8

    def __waiting_zero_sec_just(self):
        while True:  # Starting zero milliseconds as possible
            start_nsec = int(datetime.datetime.now().strftime("%f"))
            if start_nsec < 50000:  # 50msec
                break
            time.sleep(0.005)

    def __print_header(self):
        print()
        print("UDP Client")
        print()
        print("Parameters:")
        print("IP                 :", self.__ip)
        print("Port               :", self.__port)
        print("Maximum mbps       :", self.__max_mbps)
        print("Duration time(sec) :", self.__duration_sec_time)
        print("MTU                :", self.__mtu_size)

    def __print_header_process(self):
        print()
        print("Results:")
        print("datetime", "sent count", "sent size(bps)")
        print("--------", "----------", "--------------")

    def __print_send_data_info(self, header, sent_data_count,
                               sent_data_bytes_size):
        datetime_str = header[0:4]
        datetime_str += '-' + header[4:6]
        datetime_str += '-' + header[6:8]
        datetime_str += '-' + header[8:10]
        datetime_str += ':' + header[10:12]
        datetime_str += ':' + header[12:14]
        print(datetime_str, "{:,}".format(sent_data_count),
              "{:,}".format(self.__to_bps(sent_data_bytes_size)))

    def __print_end_results(self):
        print()
        print("Total sent data size(bps):",
              "{:,}".format(self.__to_bps(self.__sent_data_total_bytes_size)))
        print("Total sent data count:",
              "{:,}".format(self.__sent_data_total_count))
        print("---")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        params_dict = {}
        params_dict.update(ip=sys.argv[1])
        params_dict.update(port=sys.argv[2])
        if len(sys.argv) > 3:
            params_dict.update(max_mbps=sys.argv[3])
        if len(sys.argv) > 4:
            params_dict.update(duration_sec_time=sys.argv[4])
        if len(sys.argv) > 5:
            params_dict.update(mtu_size=sys.argv[5])

        udp_sender = UdpSender(**params_dict)
        udp_sender.execute()
    else:
        print("Invalid arguments!!")
        print('Usage: python {0} "192.168.5.1" 13001'.format(sys.argv[0]))
