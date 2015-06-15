import os.path
import unittest


def get_tests():
    return full_suite()

def full_suite():
    from .test_database import DatabaseTestCase
    from .test_model_adventure import AdventureTestCase
    from .test_model_user import UserTestCase

    resourcesuite = unittest.TestLoader().loadTestsFromTestCase(DatabaseTestCase)
    serializersuite = unittest.TestLoader().loadTestsFromTestCase(AdventureTestCase)
    utilssuite = unittest.TestLoader().loadTestsFromTestCase(UserTestCase)

    return unittest.TestSuite([resourcesuite, serializersuite, utilssuite])
