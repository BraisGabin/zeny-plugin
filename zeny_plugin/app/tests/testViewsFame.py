import json
from django.test.utils import override_settings

from .testcases import MyTestCase


class FameTest(MyTestCase):
    fixtures = ['fame.json']

    smith = [
        {
            "id": 11,
            "name": 'bs1',
            "fame": 100
        },
        {
            "id": 12,
            "name": 'bs2',
            "fame": 90
        },
        {
            "id": 13,
            "name": 'bs3',
            "fame": 80
        },
        {
            "id": 14,
            "name": 'bs4',
            "fame": 70
        },
        {
            "id": 15,
            "name": 'bs5',
            "fame": 60
        },
        {
            "id": 16,
            "name": 'bs6',
            "fame": 50
        },
    ]

    chemist = [
        {
            "id": 1,
            "name": 'alche1',
            "fame": 100
        },
        {
            "id": 2,
            "name": 'alche2',
            "fame": 90
        },
        {
            "id": 3,
            "name": 'alche3',
            "fame": 80
        },
        {
            "id": 4,
            "name": 'alche4',
            "fame": 70
        },
        {
            "id": 5,
            "name": 'alche5',
            "fame": 60
        },
        {
            "id": 6,
            "name": 'alche6',
            "fame": 50
        },
    ]

    def test_hunter_404(self):
        self.login()
        response = self.client.get('/fame/hunter/')
        self.assertEqual(response.status_code, 404)

    def test_blacksmith_all(self):
        self.login()
        response = self.client.get('/fame/blacksmith/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, self.smith)

    @override_settings(MAX_FAME_LIST=3)
    def test_blacksmith_part(self):
        self.login()
        response = self.client.get('/fame/blacksmith/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, self.smith[:3])

    def test_alchemist_all(self):
        self.login()
        response = self.client.get('/fame/alchemist/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, self.chemist)

    @override_settings(MAX_FAME_LIST=3)
    def test_alchemist_part(self):
        self.login()
        response = self.client.get('/fame/alchemist/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, self.chemist[:3])
