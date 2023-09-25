import robocorp.log as logger
from webdriver_util.webdrv_util import *
from helpers.article import Article
from helpers.selector import Selector



class ScrapperMethods():
    @staticmethod 
    def fine_search(driver: WebDriver, phrase: str, section: str, sort_by: int = 0, data_range:int = 0):
        logger.info('Starting Scrapper')
        try:
            if driver:
                logger.info(f'Open URL: ')
                driver.open_available_browser("https://www.reuters.com/")
                search =find_element(
                    driver.driver,
                    Selector(css='button[aria-label="Open search bar"]')
                    )
                if search:
                    search.click()
                    search_field = find_element(
                        driver.driver,
                        Selector(css='input[aria-labelledby*=react-aria]')
                    )
                    if search_field:
                        if 'search' in search_field.get_attribute('type'):
                            slow_send_keys(el=search_field, text='games')
                            button_search = find_element(
                                driver.driver,
                                Selector(css="button[aria-label='Search']")
                            )
                            if button_search:
                                button_search.click()
                                label_search = find_element(
                                    driver.driver, 
                                    Selector(css='label', text='Search Reuters')
                                )
                                if len(section.strip())>0:
                                    if label_search:
                                        combo_section = find_element(
                                            driver.driver,
                                            Selector(css='button[id="sectionfilter"]')
                                        )
                                        if combo_section:
                                            center_element(driver.driver, combo_section)
                                            combo_section.click()
                                            find_section = find_element(
                                                driver.driver,
                                                Selector(css='li', attr=['data-key',f'{section}'])
                                            )
                                            if find_section:
                                                find_section.click()
                                                sleep(3)
                                if data_range >=0:
                                    combo_data_range = find_element(
                                        driver.driver,
                                        Selector(css='button[id="daterangefilter"]')
                                    )
                                    if combo_data_range:
                                        center_element(driver.driver, combo_data_range)
                                        combo_data_range.click()
                                        #!LEGEND: 0= Past 24 hours 1= Past week 2= Past month 3= Past year
                                        if data_range == 0:
                                            data_range_str = 'Past 24 hours'
                                        elif data_range == 1:
                                            data_range_str = 'Past week'
                                        elif data_range == 2:
                                            data_range_str = 'Past month'
                                        elif data_range == 3:
                                            data_range_str = 'Past year'
                                        find_data_range = find_element(
                                            driver.driver,
                                            Selector(css='li', attr=['data-key',f'{data_range_str}'])
                                        )
                                        if find_data_range:
                                            find_data_range.click()
                                            sleep(3)
                                if sort_by >= 0:
                                    combo_sort = find_element(
                                        driver.driver,
                                        Selector(css='button[id="sortby"]')
                                    )
                                    if combo_sort:
                                        center_element(driver.driver, combo_sort)
                                        combo_sort.click()
                                        #!LEGEND: 0= Newest 1= Older 2= Relevance
                                        if sort_by ==0:
                                            sort_by_str = 'Newest'
                                        elif sort_by ==1:
                                            sort_by_str = 'Older'
                                        elif sort_by ==2:
                                            sort_by_str = 'Relevance'
                                        else:
                                            sort_by_str = 'Newest'
                                        combo_sort.click()
                                        find_sort_by = find_element(
                                            driver.driver,
                                            Selector(css='li', attr=['data-key',f'{sort_by_str}'])
                                        )
                                        if find_sort_by:
                                            find_sort_by.click()
                                            sleep(3)
        except Exception as e:
            print(e.with_traceback())
            return False