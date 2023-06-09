import pytest
from selenium import webdriver
from pages.start_pages import *
from pages.elk_pages import ELKCodeAuthPage
from pages.key_pages import KeyCodeAuthPage
from pages.onlime_pages import OnlimeCodeAuthPage
from pages.shome_pages import SHomePasswordAuthPage
from functions.help_functions import to_password_auth, to_registration


@pytest.fixture(scope='class')
def web_browser():
    driver = webdriver.Chrome('chromedriver112.exe')
    yield driver
    driver.quit()


@pytest.fixture(scope='class')
def init_start_code_auth_page(request, web_browser):
    request.cls.page = StartCodeAuthPage(web_browser)


@pytest.fixture(scope='class')
def init_start_pass_auth_page(request, web_browser):
    request.cls.page = StartPasswordAuthPage(web_browser)
    to_password_auth(request.cls.page)


@pytest.fixture(scope='class')
def init_start_reg_page(request, web_browser):
    request.cls.page = StartRegPage(web_browser)
    to_registration(request.cls.page)


@pytest.fixture(scope='class')
def init_start_reset_pass_page(request, web_browser):
    request.cls.page = StartResetPasswordPage(web_browser)


@pytest.fixture(scope='function')
def logout_start(web_browser):
    page = StartCodeAuthPage(web_browser)
    yield
    if page.userpic.is_visible():
        page.userpic.click()
        page.btn_logout.click()
        page.wait_page_loaded()


@pytest.fixture(scope='function')
def logout_elk(web_browser):
    page = ELKCodeAuthPage(web_browser)
    yield
    if page.userpic.is_visible():
        page.userpic.click()
        page.btn_logout.click()
        page.wait_page_loaded()


@pytest.fixture(scope='function')
def logout_onlime(web_browser):
    page = OnlimeCodeAuthPage(web_browser)
    yield
    if page.cabinet.is_visible():
        page.btn_logout_onlime.click()
        page.wait_page_loaded()


# "Ключ" вёл себя странно, поэтому выход из личного кабинета пришлось оформлять как сетап-фикстуру
@pytest.fixture(scope='function')
def pre_logout_key(web_browser):
    page = KeyCodeAuthPage(web_browser)
    if page.btn_logout.is_visible():
        page.btn_logout.click()
        page.wait_page_loaded()


@pytest.fixture(scope='function')
def logout_shome(web_browser):
    page = SHomePasswordAuthPage(web_browser)
    yield
    if page.cabinet.is_visible():
        page.userpic.click()
        page.btn_logout.click()
        page.wait_page_loaded()


# Дальше код из библиотеки
@pytest.fixture
def chrome_options(chrome_options):
    # chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--log-level=DEBUG')

    return chrome_options


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # This function helps to detect that some test failed
    # and pass this information to teardown:

    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


def get_test_case_docstring(item):
    """ This function gets doc string from test case and format it
        to show this docstring instead of the test case name in reports.
    """

    full_name = ''

    if item._obj.__doc__:
        # Remove extra whitespaces from the doc string:
        name = str(item._obj.__doc__.split('.')[0]).strip()
        full_name = ' '.join(name.split())

        # Generate the list of parameters for parametrized test cases:
        if hasattr(item, 'callspec'):
            params = item.callspec.params

            res_keys = sorted([k for k in params])
            # Create List based on Dict:
            res = ['{0}_"{1}"'.format(k, params[k]) for k in res_keys]
            # Add dict with all parameters to the name of test case:
            full_name += ' Parameters ' + str(', '.join(res))
            full_name = full_name.replace(':', '')

    return full_name


def pytest_itemcollected(item):
    """ This function modifies names of test cases "on the fly"
        during the execution of test cases.
    """

    if item._obj.__doc__:
        item._nodeid = get_test_case_docstring(item)


def pytest_collection_finish(session):
    """ This function modified names of test cases "on the fly"
        when we are using --collect-only parameter for pytest
        (to get the full list of all existing test cases).
    """

    if session.config.option.collectonly is True:
        for item in session.items:
            # If test case has a doc string we need to modify it's name to
            # it's doc string to show human-readable reports and to
            # automatically import test cases to test management system.
            if item._obj.__doc__:
                full_name = get_test_case_docstring(item)
                print(full_name)

        pytest.exit('Done!')
