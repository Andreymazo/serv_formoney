import time
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from services.utils import click_element_with_js, pars_search, scroll_down_by_pixels, scroll_into_view, str_fm_domelement
from services.forms import QueryForm  
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
from services.models import Query
from django.db import connection
from django.core.serializers import serialize


def get_category_from_search(request):
   
    print('11111111111111111111111')
    if request.method == 'POST':
        print('22222222222222222222222222')
        form = QueryForm(request.POST)
        if form.is_valid():
            form_category_value = form.cleaned_data['category']
            form_max_number_for_analitic_value = form.cleaned_data['max_number_for_analitic']

            pars_lst = pars_search(form_category_value)
            print('pars_lst', pars_lst)
            context = {
                       'pars_lst':pars_lst,
                       'num':form_max_number_for_analitic_value}
            # for index, i in enumerate(pars_lst):
            #     context[index]=i
            # print(len(context))
            # return HttpResponseRedirect(reverse('wildbberies_dj:home'))# kwargs={'category':form_category_value, 'num':form_max_number_for_analitic_value}))

            return render(request=request, template_name='wildbberies_dj/templates/first.html', context=context)
    else:
        form = QueryForm()

    return render(request=request, template_name='wildbberies_dj/templates/first.html', context={'form': form})


def pars_wildberries(request, **kwargs):
    pars_lst_2=[]
    value=kwargs['category']
    num=kwargs['num']
    print(' ===============num1===========', num, len(pars_lst_2))
    context ={}

    # Mozilla Firefox 140.0.1
    # url = 'https://catalog.wb.ru/catalog/men_clothes3/v2/catalog?ab_testing=false&appType=1&cat=129176&curr=rub&dest=-1257786&hide_dtype=13&lang=ru&page=1&sort=popular&spp=30'
    url = 'https://www.wildberries.ru/catalog'
    # Настройки Selenium
    service = FirefoxService(executable_path='/snap/bin/geckodriver')
    options = FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url=url)
        time.sleep(5)  # You can use explicit waits instead
        search_input = driver.find_element(By.ID, 'searchInput')
        search_input.clear()  # Clear field
        driver.execute_script(f"document.getElementById('searchBlock').click();")  

        search_input.send_keys(value)  # Enter text
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)
        wait = WebDriverWait(driver, timeout=20)
        products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
        #c276781789
        # id_products = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article[@class='product-card '][contains(text(), 'data-nm-id=')]")))#XPATH, "//article[@class='product-card '][contains(text(>
        elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.j-card-item')))
        id_list = [element.get_attribute('id') for element in elements]

        # element = driver.find_element(By.XPATH, "//div[@class='my-class'][contains(text(), 'hello')]")
        # id_products = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'article')))
        # print('id_products[0].text,', id_list[0].text, type(id_list[0]))
        for i,j in zip(products, id_list):
            if str_fm_domelement(i,j) not in pars_lst_2:
                pars_lst_2.append(str_fm_domelement(i,j))
        # pars_lst_2 = [pars_lst_2.append(str_fm_domelement(i)) for i in products if str_fm_domelement(i) not in pars_lst_2]
        print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), pars_lst_2)
        if len(pars_lst_2) > num:
            field_names = ['title', 'price_total', 'price_basic', 'rating', 'views', 'article_uniq']
            lst_toinsert_as_dicts = [
                {field_name: value for field_name, value in zip(field_names, item)} for item in pars_lst_2]
            # try:
                # Query.objects.bulk_create([Query(**item) for item in lst_toinsert_as_dicts])
            for i in pars_lst_2:
                if isinstance(i[4], (str)) and i[3]=='':
                    Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=0, views=0, article_uniq=i[5])
                else:
                        Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=i[3], views=i[4], article_uniq=i[5])

            qs_rating = Query.objects.all().order_by('rating')
            qs_rating_desc = Query.objects.all().order_by('-rating')
            qs_price_total = Query.objects.all().order_by('price_total')
            qs_views = Query.objects.all().order_by('views')
            #  qs_views = Query.objects.all().annotate(views_cast=Cast('views', IntegerField())).order_by('views_cast')
            context['qs_rating']=qs_rating
            context['qs_rating_desc']=qs_rating_desc
            context['qs_price_total']=qs_price_total
            context['qs_views']=qs_views

            return render(request=request, template_name='wildbberies_dj/templates/first.html', context=context)
        
        pars_lst_2.extend(products)
        print('----------------------', type(products), len(products))
        pagination_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagination-item')))
        # driver.find_elements(By.CLASS_NAME, 'pagination-item')

        # if pagination_links:
        print('pagination_links', len(pagination_links))
        print('==============',  type(pagination_links[0]), pagination_links[0].text)
        pagination_links_pages = [i.find_element(By.CLASS_NAME, 'pagination-item') for i in pagination_links]
        index = 0
        #Если мало товаров и нет пагинации   

        for link in range(1,7):#pagination_links[1:]:
            pagination_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagination-item')))
            # driver.find_elements(By.CLASS_NAME, 'pagination-item')

            # if pagination_links:
            print('pagination_links', len(pagination_links))
            print('==============',  type(pagination_links[0]), pagination_links[0].text)
            index += 1
            if len(pars_lst_2) < num:

                # pagination_links_pages = pagination_links[index].find_elements(By.CLASS_NAME, 'pagination-item')
        # print('pagination_links_pages[index]', type(pagination_links_pages), pagination_links_pages[index].text, \
                # pagination_links_pages[index].text, len(pagination_links_pages))#pagination_links_pages <class 'list'> 1 2 7

        # while len(pars_lst_2) < num:
            # index =-1
            # for link in pagination_links_pages:
                # index += 1
                # print(' ===============num2===========', num, len(pars_lst_2))
                # print('link.text', link.text, 'index==' , index)
                if len(pars_lst_2) > num:
                     break

                print('pagination_links[index].text', pagination_links[index].text)
                try:
        # //a[@class='pagination-item pagination__item j-page']
                    next_page_link = pagination_links[index].find_element(By.XPATH, f"//a[text()='{index}']")#wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='pagination-item pagination__item j-pag>
                    # next_page_link.click() # index(0).click()
                    print('next_page_link.text=================', next_page_link.text, 'index =' , index)#next_page_link.text================= 2
                    # a[text()='page={link.text} - совпадение по тексту
                    # next_page_link = link.find_element(By.XPATH, f"//a[@class='pagination-item'][{index}]")# wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@class='pagination-item pagination__item j-p>
                    # print('next_page_link.text', next_page_link.text)
                    # if next_page_link:
                        # scroll_down_by_pixels(driver=driver)
                        # scroll_into_view(driver,next_page_link)

                    scroll_into_view(driver=driver, element=next_page_link)
                    time.sleep(5)
                        # products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
                        # elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.j-card-item')))
                        # id_list = [element.get_attribute('id') for element in elements]
                        # for i,j in zip(products, id_list):
                        #     if str_fm_domelement(i,j) not in pars_lst_2:
                        #         pars_lst_2.append(str_fm_domelement(i,j))
                        # pars_lst_2.extend(products)
                        # pars_lst_2 = [pars_lst_2.extend(str_fm_domelement(i)) for i in products if str_fm_domelement(i) not in pars_lst_2]
                        # print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2), pars_lst_2)

                    print('we here 2222222222222222222222222', len(pars_lst_2))#, link.text)
                        # time.sleep(5)
                        # scroll_down_by_pixels(driver=driver, pixels=1500)
                        # scroll_down_by_pixels(driver=driver, pixels=1500)
                        # Click the element using JavaScript
                    click_element_with_js(driver, next_page_link)
                    time.sleep(5)
                    # scroll_into_view(driver=driver, element=link)
                    products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
                    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.j-card-item')))
                    id_list = [element.get_attribute('id') for element in elements]
                    for i,j in zip(products, id_list):
                        if str_fm_domelement(i,j) not in pars_lst_2:
                            pars_lst_2.append(str_fm_domelement(i,j))
                    # pars_lst_2.extend(products)
                    # pars_lst_2 = [pars_lst_2.extend(str_fm_domelement(i)) for i in products if str_fm_domelement(i) not in pars_lst_2]
                    print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                    time.sleep(5)
                    print('we here 333333333333333333333333333', len(pars_lst_2))

                except NoSuchElementException:
                                print("No more pages available")
                # scroll_down_by_pixels(driver=driver, pixels=1500)
                # products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
                # id_list = [element.get_attribute('id') for element in elements]
                # for i,j in zip(products, id_list):
                #             if str_fm_domelement(i,j) not in pars_lst_2:
                #                 pars_lst_2.append(str_fm_domelement(i,j))

                # pars_lst_2.extend(products)
                # pars_lst_2 = [pars_lst_2.extend(str_fm_domelement(i)) for i in products if str_fm_domelement(i) not in pars_lst_2]
                print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                print('we here 4444444444444444444444444444444index', index, len(pars_lst_2), type(pars_lst_2[0]))
                if index == 7 or len(pars_lst_2) >= num:
                    field_names = ['title', 'price_total', 'price_basic', 'rating', 'views', 'article_uniq']
                    lst_toinsert_as_dicts = [
                        {field_name: value for field_name, value in zip(field_names, item)} for item in pars_lst_2]
                    for i in pars_lst_2:
                        if isinstance(i[4], (str)) and i[3]=='':
                            print('Query saved ===============================================')
                            Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=0, views=0, article_uniq=i[5])
                        else:
                             Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=i[3], views=i[4], article_uniq=i[5])

                    qs_rating = Query.objects.all().order_by('rating')
                    qs_rating_desc = Query.objects.all().order_by('-rating')
                    qs_price_total = Query.objects.all().order_by('price_total')
                    qs_views = Query.objects.all().order_by('views')
                    qs_price_total_views_rating = Query.objects.all().order_by('price_total').order_by('views').order_by('rating')
                    context['qs_rating']=qs_rating
                    context['qs_rating_desc']=qs_rating_desc
                    context['qs_price_total']=qs_price_total
                    context['qs_views']=qs_views
                    context['qs_price_total_views_rating']=qs_price_total_views_rating
                    return render(request=request, template_name='wildbberies_dj/templates/first.html', context=context)

    finally:
        driver.quit()

    return render(request=request, template_name='wildbberies_dj/templates/first.html', context=context)
 
# def delete_query_table(request):
#     Query.objects.all().delete()
#     with connection.cursor() as cursor:
#         table_name = 'wildbberies_dj_query'
#         cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")
#     #  TRUNCATE TABLE table_name RESTART IDENTITY;
#     return HttpResponseRedirect(reverse('wildbberies_dj:home'))


# def filter_qs(request):
#     queryset_query = Query.objects.all()
    
#     print('11111111111111111111111111111111111111111111111')
#     title_contains = request.GET.get('title_contains')
#     print('title_contains', title_contains)
#     view_order = request.GET.get('view_order')
#     rating_order = request.GET.get('rating_order')
#     rating_desc = request.GET.get('rating_desc')
#     price_total = request.GET.get('price_total')
#     price_total_min = request.GET.get('price_total_min')
#     price_total_max = request.GET.get('price_total_max')
#     print('price_total_max', price_total_max)
#     rating_min = request.GET.get('rating_min')
#     rating_max = request.GET.get('rating_max')
#     price_range = request.GET.get('price_range')
    
#     if price_range:
#         print('price_range price_range', price_range)
#         start, end = map(int, price_range.split('-'))
#         queryset_query = Query.objects.filter(price_total__gte=start, price_total__lt=end)

#     if rating_min and rating_max:
#         queryset_query = Query.objects.filter(rating__gte=rating_min, rating__lt=rating_max)
#     if rating_min:
#         queryset_query = Query.objects.filter(rating__gte=rating_min)
#     if rating_max:
#         queryset_query = Query.objects.filter(rating__lte=rating_max)
#     if price_total_min and price_total_max:
#         print('price_total_min', price_total_min)
#         queryset_query = Query.objects.filter(price_total__gte=price_total_min, price_total__lt=price_total_max)
#     if price_total_min:
#         queryset_query = Query.objects.filter(price_total__gte=price_total_min)
#     if price_total_max:
#         queryset_query = Query.objects.filter(price_total__lte=price_total_max)
#     if title_contains:
#         queryset_query = queryset_query.filter(title__icontains=title_contains)
#     if view_order:
#         queryset_query = queryset_query.order_by('view')
#     if rating_order:
#         queryset_query = queryset_query.order_by('rating')
#     if rating_desc:
#         queryset_query = queryset_query.order_by('-rating')
#     if price_total:
#         queryset_query = queryset_query.order_by('price_total')
    
#     price_ranges = [0, 100, 200, 300, 400, 500]
#     queryset_querydraw = sorted([(index, int(next(iter(i.values())))) for index, i in enumerate(Query.objects.all().values('price_total'))])
#     queryset_querydraw_x = [i[0] for i in queryset_querydraw]
#     queryset_querydraw_y = sorted([i[1] for i in queryset_querydraw])
#     context = { 'queryset_query': queryset_query,
#             'queryset_querydraw_x':queryset_querydraw_x,
#             'queryset_querydraw_y':queryset_querydraw_y,
#             'price_ranges': price_ranges[1:],}
#     print('request.headers.__dict__------filter_qs-',  request.headers.get('Referer') )
#     print('request.GET.get(title_contains)', request.GET.__dict__)
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         print('ajaks i s here -------')
#         data = { 
#             'queryset_querydraw_x': list(queryset_query.values_list('x_field', flat=True)),
#             'queryset_querydraw_y': list(queryset_query.values_list('y_field', flat=True))
#         }
#         # Если это AJAX-запрос, возвращаем JSON
#         return JsonResponse(data)

#     return render(request=request, template_name='wildbberies_dj/templates/filter_qs.html', context=context)
