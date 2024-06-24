from django.test import TestCase
from core.models import Manufacturer

class ManufaturerModelTest(TestCase):
    def setUp(self) -> None:
        Manufacturer.objects.create(name="abc Corp", coo="xyz")
    
    def test_string_representation(self):
        manufacturer = Manufacturer.objects.get(name="abc Corp")
        self.assertEqual(str(manufacturer),"abc Corp")

    def test_coo_field(self):
        manufacturer = Manufacturer.objects.get(name="abc Corp")
        self.assertEqual(manufacturer.coo,"xyz")

    def test_coo_field_nullable(self):
        Manufacturer.objects.create(name="null corp")
        manufacturer = Manufacturer.objects.get(name="null corp")
        self.assertIsNone(manufacturer.coo)