import unittest

from zeny_plugin.app import processes


class ViewsMethods(unittest.TestCase):
    def test_is_merchantable(self):
        self.assertEqual(processes.is_merchantable(32 + 2), True)
        self.assertEqual(processes.is_merchantable(32), True)
        self.assertEqual(processes.is_merchantable(2), False)
        self.assertEqual(processes.is_merchantable(0), True)

    def test_get_item_ids(self):
        self.assertEqual(processes.get_item_ids([
            '// Sealed Cards',
            '',
        ]), set())
        self.assertEqual(processes.get_item_ids([
            '// Sealed Cards',
            '12520,475,100 //E_B_Def_Potion',
            '12521,475,100 //E_S_Def_Potion',
            '16866,457,100 //Siege_Map_Teleport_Scroll_II_Box_10',
            '12522,475,100 //E_Blessing_10_Scroll',
            '12523,475,100 //E_Inc_Agi_10_Scroll',
            '12523,475,100 //E_Inc_Agi_10_Scroll',
            '16867,457,100 //Siege_Map_Teleport_Scroll_II_Box_30',
            '',
        ]), {12521, 12520, 12522, 12523, })