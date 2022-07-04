import unittest
import ray
import os
from .test_utils import *

os.environ["hivebaseurl"] = "http://www.farts.com"

from .satelite import *


class StandaloneSateliteTests(unittest.TestCase):
    def test_login_fails(self):
        s = SateliteClientBase(0, 1)
        self.assertRaises(Exception, s._login)

@ray.remote
class SateliteClientForTesting(SateliteClientBase):
    def __init__(self, idx, poolsize):
        SateliteClientBase.__init__(self, idx, poolsize)
        self.user_pool = FakeLazyNamedPool("user", 1)

class RaySateliteTests(unittest.TestCase):
    """
    Test for the satelite magic.
    """
    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=4, num_gpus=0)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_satelite_client_test_construct(self):
        satelite = SateliteClientForTesting.remote(0, 1)

    def test_satelite_client_test_construct(self):
        satelite = SateliteClientForTesting.remote(0, 1)
