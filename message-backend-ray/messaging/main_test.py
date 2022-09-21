import ray
from .utils import utils
from .main import do_launch
from .users.user_actor_test import UserActorTestBase


class MainTest(UserActorTestBase):
    @classmethod
    def setUpClass(cls):
        super(MainTest, cls).setUpClass()
        do_launch(2)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_actors_created(self):
        self.satellite_actors = utils.LazyNamedPool("satellite", 2, min_size=2)
        self.mailserver_actors = utils.LazyNamedPool("mailserver", 2, min_size=2)
        self.satellite_actors.get_pool()
        self.mailserver_actors.get_pool()
