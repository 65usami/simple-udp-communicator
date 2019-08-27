import unittest
import client


class TestClient(unittest.TestCase):
    def test_udp_sender_execute(self):
        ip = '127.0.0.1'
        port = 13002
        duration_sec_time = 2
        udp_sender = client.UdpSender(ip=ip,
                                      port=port,
                                      duration_sec_time=duration_sec_time)
        sent_data_total_count, sent_data_total_bps = udp_sender.execute()
        self.assertGreater(sent_data_total_count, 0)
        self.assertGreater(sent_data_total_bps, 0)


if __name__ == '__main__':
    unittest.main()
