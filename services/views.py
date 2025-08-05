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
from services.utils import click_element_with_js, create_query, fill_letter_check_value, gather_into_lst_without_pagination, get_filters, pars_search, scroll_down_by_pixels, scroll_into_view, str_fm_domelement
from services.forms import QueryForm  
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
from services.models import Query
from django.db import connection
from django.core.serializers import serialize


def get_category_from_search(request):

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

            return render(request=request, template_name='services/templates/first.html', context=context)
    else:
        form = QueryForm()

    return render(request=request, template_name='services/templates/first.html', context={'form': form})

def pars_wb(request, **kwargs):
    pars_lst_2=[]
    value=kwargs['category']
    num=kwargs['num']
    print(' ===============num1===========, value ', num, len(pars_lst_2), value)
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
        wait = WebDriverWait(driver, timeout=60)
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'searchInput')))
        fill_letter_check_value(driver, search_box, value)
        apply_search_button = WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.ID, 'applySearchBtn')))
        apply_search_button.click()
        pars_lst_2 = gather_into_lst_without_pagination(driver, pars_lst_2)
        print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), pars_lst_2)
        pagination_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagination-item')))
        print('pagination_links', len(pagination_links))
        print('==============',  type(pagination_links[0]), pagination_links[0].text)
        index = 0
        # Если количество товаров достигло требуемого значения
        if len(pars_lst_2) >= num:
            create_query(pars_lst_2)
            get_filters(Query, context)
            return render(request=request, template_name='services/templates/first.html', context=context)

        #Если мало товаров (не достигло требуемого значения) и нет пагинации
        elif len(pars_lst_2) < num and not pagination_links:
            print('Finish ...........')
            gather_into_lst_without_pagination(driver=driver, pars_lst_2=pars_lst_2)
            create_query(pars_lst_2=pars_lst_2)
            context = get_filters(Query,context)
            return render(request=request, template_name='services/templates/first.html', context=context)
        
        # Если товаров меньше значения и есть пагинация все семь страниц
        elif len(pars_lst_2) < num and len(pagination_links)>=7:
            # Запускаем столько раз сколько страниц
            for link in range(0,len(pagination_links)+1):
                index += 1
                try:
                    if len(pars_lst_2) >= num:
                        create_query(pars_lst_2=pars_lst_2)
                        context = get_filters(Query, context=context)
                        return render(request=request, template_name='services/templates/first.html', context=context)
                    
                    elif len(pars_lst_2) < num:
                        scroll_into_view(driver=driver, element=pagination_links[index])
                        print('we here 2222222222222222222222222', len(pars_lst_2))#, link.text)
                        click_element_with_js(driver, pagination_links[index])
                        time.sleep(5)
                        pars_lst_2 = gather_into_lst_without_pagination(driver, pars_lst_2)
                    
                        print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                        time.sleep(5)
                        print('we here 333333333333333333333333333', len(pars_lst_2))
                except NoSuchElementException:
                    print('-----No more pages available--------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                    print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                    print('we here 4444444444444444444444444444444index', index, len(pars_lst_2), type(pars_lst_2[0]))
                    create_query(pars_lst_2=pars_lst_2)
                    context = get_filters(Query, context=context)
                    return render(request=request, template_name='services/templates/first.html', context=context)
       
       
        # Если товаров меньше значения и есть пагинация меньше семь страниц
        elif len(pars_lst_2) < num and len(pagination_links)<7:
            # Запускаем столько раз сколько страниц
            for link in range(0,len(pagination_links)+1):
                index += 1
                try:
                    if len(pars_lst_2) >= num:
                        create_query(pars_lst_2=pars_lst_2)
                        context = get_filters(Query, context=context)
                        return render(request=request, template_name='services/templates/first.html', context=context)
                    elif len(pars_lst_2) < num:
                        try:
                            scroll_into_view(driver=driver, element=pagination_links[index])
                            print('we here 2222222222222222222222222', len(pars_lst_2))#, link.text)
                            click_element_with_js(driver, pagination_links[index])
                            time.sleep(5)
                            pars_lst_2 = gather_into_lst_without_pagination(driver, pars_lst_2)
                        
                            print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                            time.sleep(5)
                            print('we here 333333333333333333333333333', len(pars_lst_2))
                        except IndexError as e:
                            print('Закончились страницы и количество товаров меньше числа для анализа',  e)
                            create_query(pars_lst_2=pars_lst_2)
                            context = get_filters(Query, context=context)
                            return render(request=request, template_name='services/templates/first.html', context=context)
                except NoSuchElementException:
                    print('-----No more pages available--------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                    print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
                    print('we here 4444444444444444444444444444444index', index, len(pars_lst_2), type(pars_lst_2[0]))
                    create_query(pars_lst_2=pars_lst_2)
                    context = get_filters(Query, context=context)
                    return render(request=request, template_name='services/templates/first.html', context=context)

        # Если индекс достиг 7 (число страниц, вайлдбериз требует регистрации, если больше) или число товаров превысило значение
        elif index == 7 or len(pars_lst_2) >= num:
            ('Finish end of pagination ...')
            create_query(pars_lst_2)
            get_filters(Query, context=context)
            return render(request=request, template_name='services/templates/first.html', context=context)

    finally:
        driver.quit()

    return render(request=request, template_name='services/templates/first.html', context=context)

        
    #     for link in range(1,len(pagination_links)):#pagination_links[1:]:
            
    #         # driver.find_elements(By.CLASS_NAME, 'pagination-item')

    #         # if pagination_links:
            
    #         index += 1
    #         if len(pars_lst_2) < num:

    #             # pagination_links_pages = pagination_links[index].find_elements(By.CLASS_NAME, 'pagination-item')
    #     # print('pagination_links_pages[index]', type(pagination_links_pages), pagination_links_pages[index].text, \
    #             # pagination_links_pages[index].text, len(pagination_links_pages))#pagination_links_pages <class 'list'> 1 2 7

    #     # while len(pars_lst_2) < num:
    #         # index =-1
    #         # for link in pagination_links_pages:
    #             # index += 1
    #             # print(' ===============num2===========', num, len(pars_lst_2))
    #             # print('link.text', link.text, 'index==' , index)
    #             if len(pars_lst_2) > num:
    #                  break
    #             # Если мало товаров и нет пагингации, то здесь косяк. Лист индекс аут ов рейндж
    #             print('pagination_links[index].text', pagination_links[index].text)
    #             try:
    #     # //a[@class='pagination-item pagination__item j-page']
    #                 next_page_link = pagination_links[index].find_element(By.XPATH, f"//a[text()='{index}']")#wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='pagination-item pagination__item j-pag>
    #                 # next_page_link.click() # index(0).click()
    #                 print('next_page_link.text=================', next_page_link.text, 'index =' , index)#next_page_link.text================= 2
    #                 # a[text()='page={link.text} - совпадение по тексту
    #                 # next_page_link = link.find_element(By.XPATH, f"//a[@class='pagination-item'][{index}]")# wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@class='pagination-item pagination__item j-p>
    #                 # print('next_page_link.text', next_page_link.text)
    #                 # if next_page_link:
    #                     # scroll_down_by_pixels(driver=driver)
    #                     # scroll_into_view(driver,next_page_link)

    #                 scroll_into_view(driver=driver, element=next_page_link)
    #                 time.sleep(5)


    #                 print('we here 2222222222222222222222222', len(pars_lst_2))#, link.text)
    #                     # time.sleep(5)
    #                     # scroll_down_by_pixels(driver=driver, pixels=1500)
    #                     # scroll_down_by_pixels(driver=driver, pixels=1500)
    #                     # Click the element using JavaScript
    #                 click_element_with_js(driver, next_page_link)
    #                 time.sleep(5)
    #                 # scroll_into_view(driver=driver, element=link)
    #                 products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
    #                 elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.j-card-item')))
    #                 id_list = [element.get_attribute('id') for element in elements]
    #                 for i,j in zip(products, id_list):
    #                     if str_fm_domelement(i,j) not in pars_lst_2:
    #                         pars_lst_2.append(str_fm_domelement(i,j))
    #                 # pars_lst_2.extend(products)
    #                 # pars_lst_2 = [pars_lst_2.extend(str_fm_domelement(i)) for i in products if str_fm_domelement(i) not in pars_lst_2]
    #                 print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
    #                 time.sleep(5)
    #                 print('we here 333333333333333333333333333', len(pars_lst_2))
    #             except NoSuchElementException:
    #                 print("No more pages available")
                    

    #             # scroll_down_by_pixels(driver=driver, pixels=1500)
    #             # products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__wrapper')))
    #             # id_list = [element.get_attribute('id') for element in elements]
    #                 # for i,j in zip(products, id_list):
    #                 #             if str_fm_domelement(i,j) not in pars_lst_2:
    #                 #                 pars_lst_2.append(str_fm_domelement(i,j))

    #             # pars_lst_2.extend(products)
    #             # pars_lst_2 = [pars_lst_2.extend(str_fm_domelement(i)) for i in products if str_fm_domelement(i) not in pars_lst_2]
    #             print('-------------------pars_lst_2-----------------', type(pars_lst_2[0]), len(pars_lst_2))
    #             print('we here 4444444444444444444444444444444index', index, len(pars_lst_2), type(pars_lst_2[0]))

    #             if index == 7 or len(pars_lst_2) >= num:
    #                 field_names = ['title', 'price_total', 'price_basic', 'rating', 'views', 'article_uniq']
    #                 lst_toinsert_as_dicts = [
    #                     {field_name: value for field_name, value in zip(field_names, item)} for item in pars_lst_2]
    #                 for i in pars_lst_2:
    #                     if isinstance(i[4], (str)) and i[3]=='':
    #                         print('Query saved ===============================================')
    #                         Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=0, views=0, article_uniq=i[5])
    #                     else:
    #                          Query.objects.create(title=i[0], price_total=i[1], price_basic=i[2], rating=i[3], views=i[4], article_uniq=i[5])

    #                 qs_rating = Query.objects.all().order_by('rating')
    #                 qs_rating_desc = Query.objects.all().order_by('-rating')
    #                 qs_price_total = Query.objects.all().order_by('price_total')
    #                 qs_views = Query.objects.all().order_by('views')
    #                 qs_price_total_views_rating = Query.objects.all().order_by('price_total').order_by('views').order_by('rating')
    #                 qs_rating_views_price_total = Query.objects.all().order_by('rating').order_by('views').order_by('price_total')
    #                 context['qs_rating']=qs_rating
    #                 context['qs_rating_desc']=qs_rating_desc
    #                 context['qs_price_total']=qs_price_total
    #                 context['qs_views']=qs_views
    #                 context['qs_price_total_views_rating']=qs_price_total_views_rating
    #                 context['qs_rating_views_price_total']=qs_rating_views_price_total
    #                 return render(request=request, template_name='services/templates/first.html', context=context)

    # finally:
    #     driver.quit()

    # return render(request=request, template_name='services/templates/first.html', context=context)

def item_detail(request, item_pk):
     obj = Query.objects.get(id=item_pk)
     artikul = obj.article_uniq[1:]
     context = {'artikul':artikul}
     return render(request=request, template_name='services/templates/item_detail.html', context=context)

 
