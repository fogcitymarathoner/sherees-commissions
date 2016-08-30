import sys


def pytest_configure(config):
    sys._called_from_test = True

# http://doc.pytest.org/en/latest/example/simple.html
def pytest_addoption(parser):
    parser.addoption("--database", action="store", default="rrg_test",
        help="database name")

@pytest.fixture
def database(request):
    return request.config.getoption("--database")