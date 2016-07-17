import os
import unittest

from fsttrpgattributes.models import Attribute, Complication, Perk, AttributeManager


class TestModels(unittest.TestCase):
    '''def test_attribute_list_initalization(self):
        als = AttributeLists('skill')
        alt = AttributeLists('talent')
        alp = AttributeLists('perk')
        alc = AttributeLists('complication')
        self.assertTrue(True)'''

    def assertReallyEqual(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        self.assertEqual(0, cmp(a, b))
        self.assertEqual(0, cmp(b, a))

    def assertReallyNotEqual(self, a, b):
        # assertNotEqual first, because it will have a good message if the
        # assertion fails.
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        self.assertNotEqual(0, cmp(a, b))
        self.assertNotEqual(0, cmp(b, a))

    def test_attribute_creation(self):
        attr = Attribute('skill', 'handgun', lvl=1, field="")
        self.assertIsInstance(attr, Attribute)

    def test_attribute_difference_with_type(self):
        attr_1 = Attribute('skill', 'handgun', lvl=1, field="")
        attr_2 = Attribute('talent', 'handgun', lvl=1, field="")

        self.assertReallyNotEqual(attr_1, attr_2)

    def test_attribute_difference_with_name(self):
        attr_1 = Attribute('skill', 'awarness', lvl=1, field="")
        attr_2 = Attribute('skill', 'handgun', lvl=1, field="")

        self.assertReallyNotEqual(attr_1, attr_2)

    def test_attribute_difference_with_field(self):
        attr_1 = Attribute('skill', 'history', lvl=1, field="greek")
        attr_2 = Attribute('skill', 'history', lvl=1, field="rome")

        self.assertReallyNotEqual(attr_1, attr_2)

    def test_attribute_is_same(self):
        attr_1 = Attribute('skill', 'history', lvl=1, field="greek")
        attr_2 = Attribute('skill', 'history', lvl=1, field="greek")

        self.assertReallyEqual(attr_1, attr_2)

    def test_complication_difference_with_name(self):
        a = Complication('unlucky', 15, 15, 5, 'towns')
        b = Complication('supersticious', 15, 15, 5, 'towns')
        self.assertReallyNotEqual(a, b)

    def test_complication_difference_with_field(self):
        a = Complication('supersticious', 15, 15, 5, 'forests')
        b = Complication('supersticious', 15, 15, 5, 'towns')
        self.assertReallyNotEqual(a, b)

    def test_complication_is_same(self):
        a = Complication('supersticious', 15, 15, 5, 'forests')
        b = Complication('supersticious', 15, 15, 5, 'forests')
        self.assertReallyEqual(a, b)

    def test_perks_difference_with_name(self):
        a = Perk('favor', 0, 'downtown', 'toni')
        b = Perk('renown', 0, 'downtown', 'toni')
        self.assertReallyNotEqual(a, b)

    def test_perks_difference_with_field(self):
        a = Perk('favor', 0, 'chinatown', 'toni')
        b = Perk('favor', 0, 'downtown', 'toni')
        self.assertReallyNotEqual(a, b)

    def test_perks_difference_with_person(self):
        a = Perk('favor', 0, 'downtown', 'teemu')
        b = Perk('favor', 0, 'downtown', 'toni')
        self.assertReallyNotEqual(a, b)

    def test_perk_is_same(self):
        a = Perk('favor', 0, 'downtown', 'toni')
        b = Perk('favor', 0, 'downtown', 'toni')
        self.assertReallyEqual(a, b)

    def test_attribute_manager_add_attribute(self):
        am = AttributeManager()
        am.add_attribute('skill', 'handgun', lvl=1, field="")
        self.assertEqual(len(am.attributes), 1)

    def test_attribute_manager_get_attribute(self):
        am = AttributeManager()
        am.add_attribute('skill', 'history', lvl=1, field='greek')
        atr = am.get_attribute('skill', 'history', 'greek')
        self.assertEqual(atr.attr_type, 'skill')
        self.assertEqual(atr.name, 'history')
        self.assertEqual(atr.lvl, 1)
        self.assertEqual(atr.field, 'greek')

    def test_attribute_manager_get_attribute_when_same_skill_and_different_field(self):
        am = AttributeManager()
        am.add_attribute('skill', 'history', lvl=2, field='greek')
        am.add_attribute('skill', 'history', lvl=2, field='rome')
        am.add_attribute('skill', 'history', lvl=2, field='italy')

        s1 = am.get_attribute('skill', 'history', field='italy')
        s2 = am.get_attribute('skill', 'history', field='rome')
        s3 = am.get_attribute('skill', 'history', field='greek')

        self.assertEqual(s1.field, 'italy')
        self.assertEqual(s2.field, 'rome')
        self.assertEqual(s3.field, 'greek')

    def tearDown(self):
        try:
            os.remove('actors.db')
            os.remove('filepaths.db')
            os.remove('attributes.db')
        except WindowsError as e:
            print('failed to delete: ' + str(e))
