from robocorp.tasks import task
from tasks_methods.methods import ScrapperMethods
from RPA.Browser.Selenium import Selenium



@task
def search_site():
    driver = Selenium()
    fine_search = ScrapperMethods.fine_search(driver=driver,section='World')
    if fine_search:
        print("ok")
    
