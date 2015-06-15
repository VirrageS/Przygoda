import os.path
import unittest


def get_tests():
	return full_suite()

def full_suite():
	from .test_database import DatabaseTestCase
	from .test_model_adventure import AdventureTestCase
	from .test_model_user import UserTestCase

	database_suite = unittest.TestLoader().loadTestsFromTestCase(DatabaseTestCase)
	model_adventure_suite = unittest.TestLoader().loadTestsFromTestCase(AdventureTestCase)
	model_user_suite = unittest.TestLoader().loadTestsFromTestCase(UserTestCase)

	return unittest.TestSuite([database_suite, model_adventure_suite, model_user_suite])
