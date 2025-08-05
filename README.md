 def text_present_in_elements(driver, locator, text):
       elements = driver.find_elements(*locator)
       for element in elements:
           if text in element.text:
               return True
       return False

   wait.until(lambda driver: text_present_in_elements(driver, (By.CSS_SELECTOR, '.autocomplete__phrase'), value))

<div class="search-catalog__btn-wrap"> 
<div class="search-catalog__btn-bg" data-link="class{merge: searchText &amp;&amp; searchText != searchQueryText toggle='search-catalog__btn--active'}"> 
<button id="applySearchBtn" class="search-catalog__btn search-catalog__btn--search j-search-good" type="button" data-link="{on applySearch}" aria-label="Поиск товара" data-jsv="#46^/46^"></button> 
</div>
 <button class="search-catalog__btn search-catalog__btn--clear j-clear-search__btn search-catalog__btn--active" type="button" data-link="class{merge: searchText toggle='search-catalog__btn--active'}{on clearSearch}" aria-label="Очистить поиск" data-jsv="#48^/48^">
 </button> 
 <div id="searchByImageContainer" class="search-catalog__photo hide" data-link="class{merge: searchText || enableSearchInSeller || enableSearchInResale toggle='hide'}class{merge: showImageSearch toggle='search-catalog__photo--active'}"> <div id="searchByImageForm" class="search-catalog__photo-form"> 
 <label id="searchByImageFormAbOld" class="search-catalog__btn search-catalog__btn--ab-old search-catalog__btn--photo j-wba-header-item hide" data-wba-header-name="Search_photo"> <input class="j-photo-search__label" data-link="{on 'change' searchByImage}" type="file" accept="image/*" name="photo" aria-label="Поиск товаров по фото" data-jsv="#51^/51^"> 
 </label> 
 <div id="searchByImageFormAbNew" data-link="{on 'click' searchByImage}" class="search-catalog__btn search-catalog__btn--ab-new search-catalog__btn--photo j-wba-header-item" data-wba-header-name="Search_photo" data-jsv="#52^/52^">
 </div> 
 </div> 
 <div id="searchByImageBtn" class="search-catalog__photo-tooltip tooltip-simple tooltip-search-photo hide-mobile"> 
 <div class="tooltip__content j-photo-search">Поиск товаров по фото
 </div> 
 </div> 
 <div id="uploadImageForSearchByImagePopUpContainer" class="upload-image-for-search-by-image-popup hide">
 </div> 
</div> 
</div>


<button id="applySearchBtn" class="search-catalog__btn search-catalog__btn--search j-search-good" type="button" data-link="{on applySearch}" aria-label="Поиск товара" data-jsv="#46^/46^"></button>


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def send_text_and_verify(driver, search_box, text):
    check = ''
    for i in text:
        try:
            # Send the current character
            search_box.send_keys(i)
            
            # Wait for a short time to allow any scripts to process the input
            time.sleep(0.1)
            
            # Check if the expected value is present in the field
            WebDriverWait(driver, 0.5).until(
                EC.text_to_be_present_in_element_value((By.ID, 'searchInput'), check + i),
                message=f"Failed to add character '{i}'. Expected value: '{check + i}', Actual value: '{search_box.get_attribute('value')}'"
            )
            
            # Update the expected value
            check += i

        except TimeoutException:
            print(f"Timeout while adding: {i}. Retrying...")
            search_box.clear()
            time.sleep(0.5)  # Small delay to ensure the field is cleared
            
            # If the current character was not added correctly, try to fix it
            if check != search_box.get_attribute('value'):
                driver.execute_script("arguments[0].value = arguments[1];", search_box, check)
                print(f"Fixed: Expected '{check}', Actual '{search_box.get_attribute('value')}'")

# Usage example
search_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'searchInput')))
send_text_and_verify(driver, search_box, "лектрический духовой шкаф с функцией свч")

   # # # Теперь wait until applySearchBtn is visible and click on it
        # apply_search_button = WebDriverWait(driver, 40).until(
        #     EC.visibility_of_element_located((By.ID, 'applySearchBtn'))
        # )
        # print('type(apply_search_button)', type(apply_search_button))
        # # # Клик на кнопку для запуска поиска (если необходимо)
        # apply_search_button.click()

        # # Если элемент становится видимым только после удаления последнего символа,
        # # то убедитесь, что он действительно стал доступен перед кликом
        # driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", apply_search_button)

        # # driver.execute_script("arguments[0].value = '';", search_box)
        # wait.until(lambda driver: search_box.get_attribute('value') == value)

        # Ожидание AJAX-запросов
        
        # apply_search_button = WebDriverWait(driver, 40).until(
        # EC.presence_of_element_located((By.ID, 'applySearchBtn')))
        
        # apply_search_button = WebDriverWait(driver, 40).until(
        # EC.visibility_of_element_located((By.ID, 'applySearchBtn')))
        # # Прокрутка элемента в область видимости
        # driver.execute_script("arguments[0].scrollIntoView(true);", apply_search_button)

        # # Клик на кнопку для запуска поиска
        # apply_search_button.click()



 # Очистка поля для следующего использования
        search_box.clear()
        search_box.send_keys(Keys.CONTROL + 'a')
        search_box.send_keys(Keys.SHIFT + Keys.DELETE)
        search_box.send_keys(Keys.RETURN)
        driver.implicitly_wait(5)  # Дайте немного времени на обновление страницы
<a href="https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BC%D0%B0%D1%82%D1%80%D0%B0%D1%81+%D0%BD%D0%B0%D0%B4%D1%83%D0%B2%D0%BD%D0%BE%D0%B9+%D0%B4%D0%BB%D1%8F+%D1%81%D0%BD%D0%B0+%D0%BE%D0%B4%D0%BD%D0%BE%D1%81%D0%BF%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9&amp;page=3" class="pagination-item pagination__item j-page">3</a>
<a href="https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BC%D0%B0%D1%82%D1%80%D0%B0%D1%81+%D0%BD%D0%B0%D0%B4%D1%83%D0%B2%D0%BD%D0%BE%D0%B9+%D0%B4%D0%BB%D1%8F+%D1%81%D0%BD%D0%B0+%D0%BE%D0%B4%D0%BD%D0%BE%D1%81%D0%BF%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9&amp;page=4" class="pagination-item pagination__item j-page">4</a>