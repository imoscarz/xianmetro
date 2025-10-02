import unittest
from xianmetro.core.load_graph import parse_stations
from xianmetro.station import Station

class TestStation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.stations = parse_stations()

    def test_stations_is_dict(self):
        self.assertIsInstance(self.stations, dict)

    def test_non_transfer_station(self):
        s1 = self.stations["136 338"]
        self.assertIsInstance(s1, Station)
        self.assertEqual(s1.name, "咸阳西站")
        self.assertEqual(s1.id, "136 338")
        self.assertEqual(len(s1.line), 1)
        self.assertEqual(s1.line[0].line_name, "1号线")
        self.assertIsInstance(s1.coords, tuple)

    def test_transfer_station_xiaozhai(self):
        s_xiaozhai = self.stations["1422 1052|1422 1052"]
        self.assertIsInstance(s_xiaozhai, Station)
        line_names = [l.line_name for l in s_xiaozhai.line]
        self.assertIn("2号线", line_names)
        self.assertIn("3号线", line_names)

    def test_loop_line_station(self):
        # 环线首尾相接
        s_jingshangcun = self.stations["1621 582|1621 582"]
        s_yujiazhai = self.stations["1521 583|1521 583"]
        jing_line = next(l for l in s_jingshangcun.line if l.line_name == "8号(环)线")
        yu_line = next(l for l in s_yujiazhai.line if l.line_name == "8号(环)线")
        self.assertEqual(jing_line.prev_station_id, "1521 583|1521 583")  # 首的前是尾
        self.assertEqual(yu_line.next_station_id, "1621 582|1621 582")    # 尾的后是首

if __name__ == "__main__":
    unittest.main()