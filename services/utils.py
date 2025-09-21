import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from services.forms import QueryForm
from services.models import Query
from selenium.common.exceptions import TimeoutException


"""Прокручиваем пикселями"""
def scroll_down_by_pixels(driver, pixels=1500):
    driver.execute_script(f"window.scrollBy(0, {pixels});")


""" Подаем домэлемент-поисковик, драйвер, значение, заполняем побуквенно и проверяем, чтобы в итоге получилось наше значение. Полезно когда события (запросы)
 и пр. мешает заполнению и обваливает наше значение в поисковике. Принтит в консоли все что происходит."""
def fill_letter_check_value(driver, search_box, value):
    check = ''
    for i in value:
        check += i
        time.sleep(0.2)  # Небольшая задержка для каждого символа. Если не выносить в отдельную функцию, то и 0,1 прокатит. Эта задержка позволяет появляться кнопке-увеличительное_стекло
        print('check', check)
        try:
            search_box.send_keys(i)
            # WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'searchInput')))
            if not search_box.get_attribute('value') == check:
                driver.execute_script("arguments[0].value = arguments[1];", search_box, check)
                print(f"Fixed: Expected '{check}', Actual '{search_box.get_attribute('value')}'")
                   
        except TimeoutException:
            print(f"Timeout while adding: {i}")
            continue


""""Подаем значение. Возвращаем список с предложенными автоподсказками в поисковике по запросу"""
def pars_search(value):
    print('value', value)
    url = 'https://www.wildberries.ru/catalog'
    service = FirefoxService(executable_path='/snap/bin/geckodriver')
    options = FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)
    parsed_lst = []
    
    try:
        driver.get(url=url)
        wait = WebDriverWait(driver, timeout=60)
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'searchInput')))
        search_box.clear()
        # Очистка поля с помощью JavaScript
        driver.execute_script("arguments[0].value = '';", search_box)

        print("Before sending keys:", search_box.get_attribute('value'))
        fill_letter_check_value(driver, search_box, value)
        print("After sending keys:", search_box.get_attribute('value'))

        wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, '.autocomplete__phrase')) > 0)

        # Ожидание загрузки автоподсказок
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.autocomplete__phrase'))
        )
        apply_search_button = WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.ID, 'applySearchBtn')))
        apply_search_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, 'applySearchBtn')))
        apply_search_button.click()

        # print('apply_search_button', apply_search_button)
        # apply_search_button.click()
        # elements = driver.find_elements(By.CSS_SELECTOR, '.autocomplete__phrase')
        # elements = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.autocomplete__phrase')))
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.autocomplete__phrase')))
            elements = driver.find_elements(By.CSS_SELECTOR, '.autocomplete__phrase')
            for variant in elements:
                parsed_lst.append(variant.text)
        except TimeoutException as e:
            print(e)
            parsed_lst = [value]
            return parsed_lst
       
        search_box.clear()

    finally:
            driver.quit()
    print(parsed_lst)        
    return parsed_lst


"""Возвращает список товаров (параметров в туплах) по категории"""
def pars_wild(category="одежда"):
    url = 'https://www.wildberries.ru/catalog'
    # Настройки Selenium
    service = FirefoxService(executable_path='/snap/bin/geckodriver')
    options = FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)
    parsed_lst = []

    try:
        driver.get(url=url)
        time.sleep(5)  # You can use explicit waits instead
        search_input = driver.find_element(By.ID, 'searchInput')
        search_input.clear()  # Clear field
        driver.execute_script(f"document.getElementById('searchBlock').click();")
        search_input.send_keys(category)  # Enter text
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)
        scroll_down_by_pixels(driver=driver, pixels=1500)
        time.sleep(5)
        scroll_down_by_pixels(driver=driver, pixels=1500)

        wait = WebDriverWait(driver, timeout=20)
        products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
        print('----------------------', type(products), len(products))
        for index, product in enumerate(products):
            title =  WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.product-card__name')))        
            # title = product.find_element(By.CSS_SELECTOR, '.product-card__name').text.strip('/')
            price_basic = product.find_element(By.CSS_SELECTOR, '.price__lower-price').text.strip('₽')
            price_basic= re.sub('[ ]', '', price_basic)
            price_total = product.find_element(By.TAG_NAME, 'del').text.strip('₽')
            price_total = re.sub('[ ]', '', price_total)
            rating = product.find_element(By.CSS_SELECTOR, '.address-rate-mini').text.strip('')
            views = product.find_element(By.CSS_SELECTOR, '.product-card__count').text.strip('оценок')
            views = re.sub('[ ]', '', views)
            print(index, 'title price_basic price_total', title, price_basic, price_total, 'Рейтинг', rating, )
            # article = product class main-page__product data-nm-id
            parsed_lst.append((title, price_basic, price_total, rating, views))
    finally:
        driver.quit()
    print(parsed_lst)
    return parsed_lst


def scroll_down_by_pixels(driver, pixels=1500, num=4):
    driver.execute_script(f"window.scrollBy(0, {pixels});")


def scroll_into_view(driver, element):
    """Scroll the page so that the given element is visible in the viewport."""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


def click_element_with_js(driver, element):
    """Click an element using JavaScript executor."""
    driver.execute_script("arguments[0].click();", element)


def dismiss_cookies(driver):
    try:
        cookies_popup = driver.find_element(By.CLASS_NAME, 'cookies')
        if cookies_popup.is_displayed():
            # You can click the accept button or close the popup using JavaScript
            driver.execute_script("arguments[0].click();", cookies_popup)
    except NoSuchElementException:
        pass  # No cookies popup found


def products_fm_lst(products_lst):
    for index, product in enumerate(products_lst):
        title = product.find_element(By.CSS_SELECTOR, '.product-card__name').text.strip('/')
        price_basic = product.find_element(By.CSS_SELECTOR, '.price__lower-price').text.strip()
        price_total = product.find_element(By.TAG_NAME, 'del').text.strip()
        rating = product.find_element(By.CSS_SELECTOR, '.product-card__rating-wrap').text.strip()
        print(index, 'title price_basic price_total', title, price_basic, price_total, 'Рейтинг', rating, )


"""Подаем домэлемент и номер элемента (он потом так за ним и пойдет), возвращаем тупл со значениями"""
def str_fm_domelement(domelement, id_value):
    # print('domelement', domelement)
    title = domelement.find_element(By.CSS_SELECTOR, '.product-card__name').text.strip('/')
    # print('title', title)
    price_basic = domelement.find_element(By.CSS_SELECTOR, '.price__lower-price').text.strip('₽')
    price_basic= re.sub('[ ]', '', price_basic)
    # print('price_basic', price_basic)
    price_total = domelement.find_element(By.TAG_NAME, 'del').text.strip('₽')
    price_total = re.sub('[ ]', '', price_total)
    # print('price_total', price_total)
    rating = domelement.find_element(By.CSS_SELECTOR, '.address-rate-mini').text.strip('')
    rating = re.sub('[ ]', '', rating)
    rating = re.sub(',', '.', rating)
    views = domelement.find_element(By.CSS_SELECTOR, '.product-card__count').text.strip('оценок')
    views = views.strip('оценки')
    views = views.strip('оценка')
    views = re.sub('[ ]', '', views)
    try:
        views = int(views)
    except ValueError:
        views = str(views)
    
    return (title, price_basic, price_total, rating, views, id_value)


def gather_into_lst(driver, pars_lst_2):
    wait = WebDriverWait(driver, timeout=20)
    products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.j-card-item')))
    id_list = [element.get_attribute('id') for element in elements]
    for i,j in zip(products, id_list):
        if str_fm_domelement(i,j) not in pars_lst_2:
            pars_lst_2.append(str_fm_domelement(i,j))
    return pars_lst_2    


def gather_into_lst_without_pagination(driver, pars_lst_2):
    wait = WebDriverWait(driver, timeout=40)
    # scroll_down_by_pixels(driver=driver)
    driver.implicitly_wait(2) 
    products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.j-card-item')))
    id_list = [element.get_attribute('id') for element in elements]
    for i,j in zip(products, id_list):
        if str_fm_domelement(i,j) not in pars_lst_2:
            pars_lst_2.append(str_fm_domelement(i,j))
    return pars_lst_2

def create_query(pars_lst_2):
    field_names = ['title', 'price_total', 'price_basic', 'rating', 'views', 'article_uniq']
    lst_toinsert_as_dicts = [{field_name: value for field_name, value in zip(field_names, item)} for item in pars_lst_2]
    for i in pars_lst_2:
        if isinstance(i[4], (str)) and i[3]=='':
            Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=0, views=0, article_uniq=i[5])
        else:
            Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=i[3], views=i[4], article_uniq=i[5])

def get_filters(my_model, context):

    qs_rating = my_model.objects.all().order_by('rating')
    qs_rating_desc = my_model.objects.all().order_by('-rating')
    qs_price_total = my_model.objects.all().order_by('price_total')
    qs_views = my_model.objects.all().order_by('views')
    qs_rating_views_price_total = my_model.objects.all().order_by('rating', 'views', 'price_total')
    #  qs_views = Query.objects.all().annotate(views_cast=Cast('views', IntegerField())).order_by('views_cast')
    context['qs_rating']=qs_rating
    context['qs_rating_desc']=qs_rating_desc
    context['qs_price_total']=qs_price_total
    context['qs_views']=qs_views
    context['qs_rating_views_price_total']=qs_rating_views_price_total
    return context
