import csv
import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

import robocorp.log as logger
from openpyxl import Workbook
from robocorp import storage, workitems

from helpers.article import Article
from helpers.payload import Payload
from helpers.selector import Selector
from webdriver_util.webdrv_util import *
from selenium.webdriver.chrome.options import Options

class ProducerMethods:
    @staticmethod
    def read_csv_create_work_item():
        csv_file_path = os.path.join("devdata", "csv_input.csv")

        if os.path.exists(csv_file_path):
            with open(csv_file_path, mode="r", newline="") as file:
                reader = csv.reader(file)
                header = next(reader)
                for row in reader:
                    payload = Payload(
                        phrase_test=row[0],
                        section=row[1],
                        data_range=int(row[2]),
                        sort_by=int(row[3]),
                    )
                    workitems.outputs.create(
                        payload={
                            "phrase_test": payload.phrase_test,
                            "section": payload.section,
                            "data_range": payload.data_range,
                            "sort_by": payload.sort_by,
                        }
                    )
        else:
            logger.critical(f"The CSV file: {csv_file_path} was not found.")


class ScraperMethods:
    @staticmethod
    def get_work_item() -> Payload | None:
        item = workitems.inputs.current
        if item:
            logger.info("Received payload:", item.payload)
            pay = Payload(
                phrase_test=item.payload["phrase_test"],
                section=item.payload["section"],
                data_range=int(item.payload["data_range"]),
                sort_by=int(item.payload["sort_by"]),
            )
            return pay
        else:
            logger.critical(f"Some error on process occurred!")

    @staticmethod
    def inicial_search(driver: Selenium, phrase: str):
        logger.info("Starting Scraper")
        logger.info("Getting a url site to the scraper")
        site_url = storage.get_text("site_url")
        if site_url:
            logger.info(f"URL received: {site_url}")
        try:
            if driver:
                logger.info(f"Open URL: {site_url}")
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--no-sandbox") 
                options.add_argument("--disable-blink-features=AutomationControlled")
                # Exclude the collection of enable-automation switches 
                options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
                # Turn-off userAutomationExtension 
                options.add_experimental_option("useAutomationExtension", False) 
                driver.open_browser(
                    url=site_url,
                    browser='chrome',
                    options=options,
                    executable_path= get_chromedriver_path()  
                )
                driver.delete_all_cookies()
                # driver.set_window_size(1920, 1080)
                driver.driver.execute_script(
                    'Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
                search = find_element(
                    driver.driver, Selector(css='button[aria-label="Open search bar"]')
                )
                if search:
                    center_element(driver.driver, search)
                    search.click()
                    search_field = find_element(
                        driver.driver,
                        Selector(css="input[aria-labelledby*=react-aria]"),
                    )
                    if search_field:
                        if "search" in search_field.get_attribute("type"):
                            slow_send_keys(el=search_field, text=phrase)
                            button_search = find_element(
                                driver.driver,
                                Selector(css="button[aria-label='Search']"),
                            )
                            if button_search:
                                button_search.click()
                                return True
        except Exception as e:
            print(e.with_traceback())
            return False

    @staticmethod
    def fine_search(
        driver: WebDriver,
        phrase: str,
        section: str,
        sort_by: int = 0,
        data_range: int = 0,
    ):
        try:
            no_results_match = find_with_text(
                driver.driver, "h1", f"No search results match the term “{phrase}”"
            )
            if no_results_match:
                logger.critical(f"Some error occurred: No search match...")
                return False
            label_search = find_element(
                driver.driver, Selector(css="label", text="Search Reuters")
            )
            if label_search:
                if len(section.strip()) > 0:
                    if label_search:
                        combo_section = find_element(
                            driver.driver, Selector(css='button[id="sectionfilter"]')
                        )
                        if combo_section:
                            center_element(driver.driver, combo_section)
                            combo_section.click()
                            find_section = find_element(
                                driver.driver,
                                Selector(css="li", attr=["data-key", f"{section}"]),
                            )
                            if find_section:
                                find_section.click()
                                sleep(3)
                if data_range >= 0:
                    combo_data_range = find_element(
                        driver.driver, Selector(css='button[id="daterangefilter"]')
                    )
                    if combo_data_range:
                        center_element(driver.driver, combo_data_range)
                        combo_data_range.click()
                        #!LEGEND: 0= Past 24 hours 1= Past week 2= Past month 3= Past year
                        if data_range == 0:
                            data_range_str = "Past 24 hours"
                        elif data_range == 1:
                            data_range_str = "Past week"
                        elif data_range == 2:
                            data_range_str = "Past month"
                        elif data_range == 3:
                            data_range_str = "Past year"
                        find_data_range = find_element(
                            driver.driver,
                            Selector(css="li", attr=["data-key", f"{data_range_str}"]),
                        )
                        if find_data_range:
                            find_data_range.click()
                            sleep(3)
                if sort_by >= 0:
                    combo_sort = find_element(
                        driver.driver, Selector(css='button[id="sortby"]')
                    )
                    if combo_sort:
                        center_element(driver.driver, combo_sort)
                        js_click(driver.driver, combo_sort)
                        #!LEGEND: 0= Newest 1= Older 2= Relevance
                        if sort_by == 0:
                            sort_by_str = "Newest"
                        elif sort_by == 1:
                            sort_by_str = "Older"
                        elif sort_by == 2:
                            sort_by_str = "Relevance"
                        else:
                            sort_by_str = "Newest"
                        find_sort_by = find_element(
                            driver.driver,
                            Selector(css="li", attr=["data-key", f"{sort_by_str}"]),
                        )
                        if find_sort_by:
                            find_sort_by.click()
                            sleep(3)
                            return True

        except Exception as e:
            logger.critical(f"Some error occurred: {e.__cause__}.")
            return False

    @staticmethod
    def collect_articles(driver: WebDriver) -> list[Article] | None:
        try:
            list_articles = []
            more_results = True
            while more_results:
                logger.info("Search results was found")
                search_results_section = find_element(
                    driver.driver,
                    Selector(css="div[class*=search-results__sectionContainer]"),
                )
                if search_results_section:
                    logger.info("Search results was found")
                    li_search_results = find_all_css(
                        driver.driver, 'ul[class*="search-results__list"] li'
                    )
                    if li_search_results:
                        sleep(3)
                        lst_title = []
                        lt = TagAttVl(tag="a", attr="data-testid", vlr="Link")
                        l2t = TagAttVl(tag="a", attr="data-testid", vlr="Heading")
                        lst_title.append(lt)
                        lst_title.append(l2t)
                        lst_time = []
                        ltm = TagAttVl(tag="time", attr="data-testid", vlr="Body")
                        l2tm = TagAttVl(tag="time", attr="data-testid", vlr="Text")
                        lst_time.append(ltm)
                        lst_time.append(l2tm)
                        for li in li_search_results:
                            logger.info("Create a article object")
                            article = Article()
                            title = find_elm_with_attribute(li, lst_title)
                            time = find_elm_with_attribute(li, lst_time)
                            try:
                                center_element(driver.driver, li)
                                photo = find_elm_picture(
                                    li, Selector(css='img[src*=".jpg"]')
                                )
                                if photo:
                                    article.picture_filename = photo
                                    logger.info(
                                        f"Picture was found: {article.picture_filename}"
                                    )
                            except:
                                logger.info(
                                    "Information about picture in article was not found."
                                )
                                pass
                            logger.info("Information about article was found.")
                            article.title = title.text.strip()
                            article.date = datetime.strptime(
                                time.get_attribute("datetime"), "%Y-%m-%dT%H:%M:%SZ"
                            )
                            logger.info(
                                f" Title: {article.title} -- Date: {article.date}"
                            )
                            sleep(0.4)
                            list_articles.append(article)
                        try:
                            button_next = find_element(
                                driver.driver,
                                Selector(css='button[aria-label*="Next stories"]'),
                            )
                            if button_next:
                                center_element(driver.driver, button_next)
                                button_next.click()
                        except:
                            button_next = find_element(
                                driver.driver,
                                Selector(css='button[aria-label*="Disabled"]'),
                            )
                            if button_next:
                                more_results = False
            return list_articles
        except Exception as e:
            logger.critical(f"Some error occurred: {e.__cause__}.")
            return False


class ExcelOtherMethods:
    def __extract_filename_from_url(url):
        # Use regex to match a pattern that extracts the filename with extension
        match = re.search(r"[^/]+$", url)
        if match:
            filename_with_extension = match.group(0)
            return filename_with_extension
        else:
            return None

    def __contains_money(text):
        # Regular expression pattern to match monetary amounts
        pattern = r"\$[0-9,.]+|\b\d+\s*(?:dollars|USD)\b"

        # Use regular expression to search for matches in the text
        matches = re.findall(pattern, text)

        # If matches are found, return True; otherwise, return False
        return bool(matches)

    def __download_image(url):
        project_dir = str(os.getcwd())
        full_path = Path(project_dir, "devdata", "downloads")
        if os.path.isdir(full_path):
            full_path = os.path.join(
                full_path, ExcelOtherMethods.__extract_filename_from_url(url)
            )
            logger.info(f"Downloading image: {url}")
            urllib.request.urlretrieve(url, full_path)
            return full_path

    @staticmethod
    def prepare_articles(list_articles: list[Article], phrase: str) -> list[Article]:
        new_list_articles = []
        if list_articles:
            for article in list_articles:
                art = Article()
                art.title = article.title
                art.date = article.date
                art.title_count_phrase = article.title.lower().count(phrase.lower())
                art.description = ""
                art.description_count_phrase = 0
                art.find_money_title_description = ExcelOtherMethods.__contains_money(
                    article.title
                )
                # download image
                if len(article.picture_filename) > 0:
                    art.picture_filename = article.picture_filename
                    art.picture_local_path = ExcelOtherMethods.__download_image(
                        art.picture_filename
                    )
                new_list_articles.append(art)
                logger.info(f"Article created: {art}")
            return new_list_articles

    @staticmethod
    def export_excel(list_articles: list[Article]):
        project_dir = str(os.getcwd())
        full_path = Path(project_dir, "output")
        excel_file_path = os.path.join(full_path, "Articles.xlsx")
        wb = Workbook()
        ws = wb.active
        str_data = Article.articles_to_json(list_articles)
        data = json.loads(str_data)
        headers = list(data[0].keys()) if data else []
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)
        for row_index, row_data in enumerate(data, start=2):
            for col_index, header in enumerate(headers, start=1):
                ws.cell(row=row_index, column=col_index, value=row_data.get(header, ""))
        wb.save(excel_file_path)
        logger.info("Excel created")
        logger.info("Creating Output...")
        workitems.outputs.create(files=[excel_file_path])
