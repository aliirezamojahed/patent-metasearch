from django.views.generic import TemplateView
from django.shortcuts import render

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from itertools import zip_longest
import concurrent.futures


class HomePageView(TemplateView):
    template_name = 'home_page.html'


def search_results(request):
    
    def google_patents():

        def wrapper(link):
            return f'https://patents.google.com/{link}?q={query.replace(" ", "+")}&oq={query.replace(" ", "+")}'

        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        driver.get('https://patents.google.com/?q=' + query.replace(' ', '+'))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        search_results = soup.find_all('article', class_='result')
        results = list()

        for search_result in search_results:
            title = search_result.find('h3').get_text()
            description = search_result.select_one('template + raw-html').get_text()
            link = search_result.find(class_='result-title')['data-result']
            results.append({
                'search_engine': 'GOOGLE PATENTS',
                'title': title.strip().capitalize(),
                'description': description.strip(),
                'link': wrapper(link),
            })

        return {'google_patents': results}

    def lens():
        LINK_PREFIX = 'https://www.lens.org'
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        driver.get('https://www.lens.org/lens/search/patent/list?preview=true&q=' + query.replace(' ', '+'))
        driver.implicitly_wait(10)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        search_results = soup.find_all('div', class_='div-table-results-row')
        results = list()

        for search_result in search_results:
            title = search_result.find('h3').get_text()
            description = search_result.find('div', class_='result-snippet').get_text()
            link = search_result.select_one('h3 a')['href']
            results.append({
                'search_engine': 'LENS',
                'title': title.strip().capitalize(),
                'description': description.strip(),
                'link': LINK_PREFIX + link,
            })
        
        return {'lens': results}


    def patentscope():
        LINK_PREFIX = 'https://patentscope.wipo.int/search/en/'
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        driver.get('https://patentscope.wipo.int/')
        search_input = driver.find_element(
            by=By.ID, 
            value='simpleSearchForm:fpSearch:input',
        )
        search_input.send_keys(query, Keys.ENTER)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        search_results = soup.find_all('div', class_='ps-patent-result')
        results = list()

        for search_result in search_results:
            title = search_result.find(class_='ps-patent-result--title--title').get_text()
            description = search_result.find('div', class_='ps-patent-result--abstract').get_text()
            link = search_result.find('a')['href']
            results.append({
                'search_engine': 'PATENTSCOPE',
                'title': title.strip().capitalize(),
                'description': description.strip(),
                'link': LINK_PREFIX + link,
            })

        return {'patentscope': results}
    

    query = request.GET.get('q')
    
    CHROMEDRIVER_PATH = 'C:/SeleniumDrivers/chromedriver.exe'

    chrome_options = Options()  
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')

    temp = dict()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [
            executor.submit(google_patents),
            executor.submit(lens),
            executor.submit(patentscope),
        ]

        for f in concurrent.futures.as_completed(results):
            temp.update(f.result())
    
    merged_results = zip_longest(temp['google_patents'], temp['lens'], temp['patentscope'])
    all_results = [x for x in sum(merged_results, ()) if x is not None]

    context = {
        'query': query,
        'search_results': all_results,
    }

    return render(request, 'search_results.html', context)
