import unittest

from datetime import datetime

from app import app
from app.mine.models import AdventureSearches, AdventureViews, UserReports


class UserTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

    def test_adventure_searches(self):
        """Checks if model AdventureSearches init properly"""

        search_first = AdventureSearches(adventure_id=1, value=1)

        self.assertEqual(search_first.adventure_id, 1)
        self.assertNotEqual(search_first.date, None)
        self.assertGreater(datetime.now(), search_first.date)
        self.assertEqual(search_first.value, 1)

        search_second = AdventureSearches(adventure_id=2, value=10)

        self.assertEqual(search_second.adventure_id, 2)
        self.assertNotEqual(search_second.date, None)
        self.assertGreater(datetime.now(), search_second.date)
        self.assertEqual(search_second.value, 10)

    def test_adventure_views(self):
        """Checks if model AdventureViews init properly"""

        view_first = AdventureViews(adventure_id=1, value=1)

        self.assertEqual(view_first.adventure_id, 1)
        self.assertNotEqual(view_first.date, None)
        self.assertGreater(datetime.now(), view_first.date)
        self.assertEqual(view_first.value, 1)

        view_second = AdventureViews(adventure_id=2, value=10)

        self.assertEqual(view_second.adventure_id, 2)
        self.assertNotEqual(view_second.date, None)
        self.assertGreater(datetime.now(), view_second.date)
        self.assertEqual(view_second.value, 10)

    def test_user_reports(self):
        """Checks if model UserReports init properly"""

        report = UserReports(user_id=1, email="tomek@tomek.com", subject="t", message="t")

        self.assertEqual(report.user_id, 1)
        self.assertEqual(report.email, "tomek@tomek.com")
        self.assertEqual(report.subject, "t")
        self.assertEqual(report.message, "t")
        self.assertNotEqual(report.created_on, None)
        self.assertGreater(datetime.now(), report.created_on)
