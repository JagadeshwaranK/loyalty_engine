import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loyalty_engine'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loyalty_engine.settings")
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['rewards'])
    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests()
