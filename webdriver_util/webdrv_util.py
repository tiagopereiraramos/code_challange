import difflib
import random
import re
import traceback
from time import sleep
import os
import robocorp.log as logger
from selenium import webdriver
from selenium.common import (ElementClickInterceptedException,
                             ElementNotInteractableException,
                             JavascriptException, NoSuchElementException)
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


from helpers.selector import Selector, TagAttVl

# *This is my personal lib with selenium methods that help me scraper better.

Timeout = 5
RetryAttempts = 4

def is_chromedriver_present(driver_dir):
    # Lista os arquivos no diretório 'driver'
    files = os.listdir(driver_dir)
    
    # Verifica se há algum arquivo com o nome 'chromedriver' no diretório
    return 'chromedriver' in files

def get_chromedriver():
    # Verificar se o diretório 'driver' existe
    driver_dir = 'driver'
    if not os.path.exists(driver_dir) or not is_chromedriver_present(driver_dir):
        logger.warn(f'O arquivo chromedriver não foi encontrado no diretório {driver_dir}. Baixando o Chromedriver...')
        options =webdriver.ChromeOptions()
        options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=options, service=service)
    else:
        # Se o diretório 'driver' existir e o arquivo chromedriver estiver presente, use-o
        chromedriver_path = os.path.join(driver_dir, 'chromedriver')
        driver = webdriver.Chrome(executable_path=chromedriver_path)
    
    return driver

""" def get_driver():
    options =webdriver.ChromeOptions()
    options.add_argument("--headless")
    

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    return driver """

def normalize(t: str) -> str:
    return t.lower().strip()


def center_element(driver, elm):
    """
    Centers an element on the page.
    """
    # Will this ever work? It seems like if the element is off the page, by definition it's
    # not clickable
    # wait = WebDriverWait(driver, 5)
    # and wait.until(EC.element_to_be_clickable(elm))
    if elm:
        driver.execute_script(
            "arguments[0].scrollIntoView({'block':'center','inline':'center'})", elm
        )
    return elm


def slow_send_keys(el, text, unfocus_on_complete=True):
    """
    Sends keys to an element slowly, one character at a time. There will be a random delay between
    each character.
    This is useful to avoid bot detection when inserting a text in a field.
    :param el: Selenium element
    :param text: text to insert
    """
    if el:
        el.click()

        # some fields need validation, wait before inserting text
        sleep(1.5)
        try:
            el.clear()
        except:
            pass
        for c in text:
            el.send_keys(c)
            sleep(0.15 * random.uniform(1, 3))

        if unfocus_on_complete:
            # once the value is set. it need to be validated again. that means switching to a different
            # field to trigger any js checks
            el.send_keys(Keys.TAB)


def js_click(driver, elm):
    """
    Clicks an element with javascript. This is useful for elements that are not clickable or
    displayed.
    :param driver: chrome driver
    :param elm: Selenium element
    :return: the element
    """
    try:
        if elm:
            driver.execute_script("arguments[0].click();", elm)
        return elm
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_with_label(driver, tag, label, timeout=Timeout):
    try:
        return find_with_attribute(driver, tag, "aria-label", label, timeout)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_all_with_attribute(driver, tag, attr, value, timeout=Timeout):
    try:
        target = normalize(value)
        return [
            e
            for e in WebDriverWait(driver, timeout).until(
                EC.visibility_of_any_elements_located(locator=[By.TAG_NAME, tag])
            )
            if e.get_attribute(attr) and (target in normalize(e.get_attribute(attr)))
        ]
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_all_elm_with_attribute(elm: WebElement, tag, attr, value, timeout=Timeout):
    try:
        target = normalize(value)
        return [
            e
            for e in elm.find_elements(By.TAG_NAME, tag)
            if e.get_attribute(attr) and (target in normalize(e.get_attribute(attr)))
        ]
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_elm_with_attribute(
    elm: WebElement, tag_attr_value: TagAttVl | list[TagAttVl], timeout=Timeout
) -> WebElement | None:
    if not isinstance(tag_attr_value, list):
        tag_attr_value = [tag_attr_value]
    for selector in tag_attr_value:
        try:
            target = normalize(selector.vlr)
            logger.debug(
                f"Trying to find:{selector.attr}  - with: {selector.tag} and: {target}"
            )
            sleep(0.2)
            e = elm.find_element(By.TAG_NAME, selector.tag)
            if e.get_attribute(selector.attr) and (
                target in normalize(e.get_attribute(selector.attr))
            ):
                logger.debug(
                    f"Found: {selector.attr} - with: {selector.tag} and: {target}"
                )
                sleep(0.4)
                return e
        except NoSuchElementException:
            logger.debug(
                f"Not Found: {selector.attr} - with: {selector.tag} and: {target}"
            )
            continue


def find_elm_picture(elm: WebElement, selector: Selector, timeout=Timeout):
    try:
        logger.debug(f"Trying to find:{selector.css}")
        sleep(0.2)
        e = WebDriverWait(elm, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector.css))
        )
        if e:
            str_picture = e.get_attribute("src")
            sleep(0.4)
            return str_picture
    except NoSuchElementException:
        logger.debug(f"Not Found: {selector.css}")


def find_with_attribute(driver, tag, attr, value, timeout=Timeout):
    try:
        label = "find_with_attribute %s %s %s" % (tag, attr, value)
        return find_it(
            driver,
            lambda: find_all_with_attribute(driver, tag, attr, value),
            timeout=timeout,
            label=label,
        )
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_with_text(driver, tag, text, timeout=Timeout):
    try:
        target = normalize(text)
        label = "find_with_text %s %s" % (tag, target)

        def get():
            return [
                e
                for e in WebDriverWait(driver, timeout).until(
                    EC.visibility_of_any_elements_located(locator=[By.TAG_NAME, tag])
                )
                if target in normalize(e.text)
            ]

        return find_it(driver, get, timeout=timeout, label=label)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_css_with_text(driver, css_selector, text, timeout=Timeout):
    try:
        target = normalize(text)
        label = f"find_css_with_text {css_selector} {target}"

        def get():
            return [
                e
                for e in WebDriverWait(driver, timeout).until(
                    EC.visibility_of_any_elements_located(
                        locator=[By.CSS_SELECTOR, css_selector]
                    )
                )
                if target in normalize(e.text)
            ]

        return find_it(driver, get, timeout=timeout, label=label)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_css(driver, css_selector, timeout=Timeout):
    try:
        label = "find_css %s" % css_selector

        def get():
            return [
                e
                for e in WebDriverWait(driver, timeout).until(
                    EC.visibility_of_any_elements_located(
                        locator=[By.CSS_SELECTOR, css_selector]
                    )
                )
            ]

        return find_it(driver, elements=get, timeout=timeout, label=label)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_all_css(driver: WebDriver, css_selector, timeout=Timeout):
    try:
        return driver.find_elements(By.CSS_SELECTOR, css_selector)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
    ) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return None


def find_element(
    driver: WebDriver, selectors: Selector | list[Selector], timeout: int = Timeout
) -> WebElement | None:
    """
    Find an element by css, text or xpath. If a list of selectors is provided, it will try to find the
    first one that matches.

    :param driver: chrome driver
    :param selectors: list of Selectors
    :param timeout: timeout in seconds
    :return: the element if found, None otherwise
    """
    if not isinstance(selectors, list):
        selectors = [selectors]

    for selector in selectors:
        elm = None
        logger.debug(f"Trying to find {selector.css}")
        try:
            if selector.xpath:
                elm = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located(locator=[By.XPATH, selector.xpath])
                )
            elif selector.css and selector.attr:
                attr, value = selector.attr
                elm = find_with_attribute(driver, selector.css, attr, value, timeout)
            elif selector.css and selector.text:
                elm = find_css_with_text(
                    driver, selector.css, selector.text, timeout=timeout
                )
            elif selector.css:
                elm = find_css(driver, selector.css, timeout=timeout)
            if elm:
                logger.debug(f"Found element: {elm}")
                return elm
        except NoSuchElementException:
            continue


def find_elements(
    driver: WebDriver, selectors: Selector | list[Selector], timeout: int = Timeout
) -> WebElement | None:
    """
    Find an element by css, text or xpath. If a list of selectors is provided, it will try to find the
    first one that matches.

    :param driver: chrome driver
    :param selectors: list of Selectors
    :param timeout: timeout in seconds
    :return: the element if found, None otherwise
    """
    if not isinstance(selectors, list):
        selectors = [selectors]

    for selector in selectors:
        elm = None
        logger.debug(f"Trying to find {selector.css}")
        try:
            if selector.xpath:
                elm = WebDriverWait(driver, timeout).until(
                    EC.presence_of_all_elements_located_located(
                        locator=[By.XPATH, selector.xpath]
                    )
                )
            elif selector.css and selector.attr:
                attr, value = selector.attr
                elm = find_with_attribute(driver, selector.css, attr, value, timeout)
            elif selector.css and selector.text:
                elm = find_css_with_text(
                    driver, selector.css, selector.text, timeout=timeout
                )
            elif selector.css:
                elm = find_all_css(driver, selector.css, timeout=timeout)
            if elm:
                logger.debug(f"Found element: {elm}")
                return elm
        except NoSuchElementException:
            continue


def select_option(select, option, to_string):
    """
    Selects an option in a select element. If the option is not found, it will try to find the best
    match using fuzzy matching.

    :param select: Selenium element
    :param option: option to select
    :param to_string: function to convert an option to a string (i.e. could be based in the text
        or the value)
    """
    if not select:
        return False
    retry(select.click)
    sleep(0.5)

    possible_options = sorted(
        select.find_elements(By.TAG_NAME, "option"),
        key=lambda op: difflib.SequenceMatcher(
            None, normalize(to_string(op)), normalize(str(option))
        ).ratio(),
        reverse=True,
    )
    if possible_options:
        best = possible_options[0]
        retry(best.click)
        return True


def find_fuzzy(elements, to_string, target):
    return sorted(
        elements,
        key=lambda op: difflib.SequenceMatcher(
            None, normalize(to_string(op)), normalize(target)
        ).ratio(),
    )[-1]


def page_contains(driver, token, timeout=Timeout):
    haystack = (
        WebDriverWait(driver, timeout)
        .until(
            EC.visibility_of_any_elements_located(locator=[By.CSS_SELECTOR, "body"])
        )[0]
        .get_attribute("innerHTML")
    )
    return re.search(token, haystack, re.IGNORECASE) is not None


def select_option_value(select, option):
    select_option(select, option, lambda op: op.get_attribute("value"))


def select_option_text(select, option):
    select_option(select, option, lambda op: op.text)


def find_it(driver, elements, timeout=Timeout, label=None):
    def get():
        results = elements()
        if len(results) > 0:
            return results[0]
        return None

    return wait_for(get, timeout=timeout, label=label)


def wait_for(fun, timeout=Timeout, label=None):
    """
    Waits for a function to return a value

    :param fun: function to be called
    :param timeout: timeout in seconds
    :param label: label to be printed in the log
    """
    t = 0
    while t < timeout:
        if label:
            logger.debug("Waiting for %s" % label)
        res = fun()
        delta = 0.25
        if res:
            logger.info("Found %s" % label)
            return res
        else:
            sleep(delta)
            t = t + delta
    return fun()


def retry(fun, on_fail=lambda: True, sleep_time=1, attempts=RetryAttempts):
    for attempt in range(0, attempts):
        try:
            if attempt > 0:
                logger.info(f"Retrying {fun.__name__}. Attempt #{attempt + 1}")
            return fun()
        except DontRetryException as e:
            raise e
        except Exception as e:
            attempt = attempt + 1
            on_fail()
            if attempt >= attempts:
                raise e
            lines = traceback.format_exception(e, limit=10)
            logger.warning(
                "Retrying fun due to %s\n%s, attempt=%s of %s"
                % (str(e), "\n".join(lines), attempt, attempts)
            )
            sleep(sleep_time)


class DontRetryException(Exception):
    pass


class KickedOutofFunnelException(DontRetryException):
    pass


class Fatal(Exception):
    def __init__(self, e, metadata={}):
        self._e = e
        self._meta = metadata

    def lines(self):
        return traceback.format_exception(self._e, limit=10)

    def metadata(self):
        base = self._meta
        base["retriable"] = not isinstance(self._e, DontRetryException)
        base["exception_name"] = self._e.__class__.__name__
        base["exception_message"] = str(self._e)
        return base
