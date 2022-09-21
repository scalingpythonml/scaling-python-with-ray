import os
import uuid

# Configure some env variables for django testing.
os.environ["DJANGO_CONFIGURATION"] = "UnitTest"
os.environ["__ENV__"] = "UnitTest"
os.environ["SECRET_KEY"] = "d7b24a10f65b4cae8549d79991ebaf2b"
os.environ["STRIPE_TEST_SECRET_KEY"] = "sk_test_very_secret"
os.environ["DJSTRIPE_WEBHOOK_SECRET"] = "very_secret2"
test_id = str(uuid.uuid1()).replace("-", "")
os.environ["TEST_ID"] = test_id
