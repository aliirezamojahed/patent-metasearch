from django.views.generic import TemplateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from .models import UserQuery, Result

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from itertools import zip_longest
import concurrent.futures
import os


class HomePageView(TemplateView):
    template_name = 'home_page.html'


def search_results(request):
    
    def google_patents():
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
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
                'qid': q,
                'search_engine': 'GOOGLE PATENTS',
                'title': title.strip().capitalize(),
                'description': description.strip(),
                'link': link,
            })

        return {'google_patents': results}

    def lens():
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        driver.get('https://www.lens.org/lens/search/patent/list?preview=true&q=' + query.replace(' ', '+'))
        _ = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'result-snippet'))
        )
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        search_results = soup.find_all('div', class_='div-table-results-row')
        results = list()

        for search_result in search_results:
            title = search_result.find('h3').get_text()
            description = search_result.find('div', class_='result-snippet').get_text()
            link = search_result.select_one('h3 a')['href']
            results.append({
                'qid': q,
                'search_engine': 'LENS',
                'title': title.strip().capitalize(),
                'description': description.strip(),
                'link': link,
            })
        
        return {'lens': results}


    def patentscope():
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        driver.get('https://patentscope.wipo.int/')
        search_input = driver.find_element(
            by=By.NAME, 
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
                'qid': q,
                'search_engine': 'PATENTSCOPE',
                'title': title.strip().capitalize(),
                'description': description.strip(),
                'link': link,
            })

        return {'patentscope': results}


    # Driver configurations
    # CHROMEDRIVER_PATH = 'C:/SeleniumDrivers/chromedriver.exe'
    options = Options()  
    # options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--remote-debugging-port=9222')
    # options.add_argument('--incognito')
    # CHROMEDRIVER_PATH = str(os.environ.get('CHROMEDRIVER_PATH'))

    query = request.GET.get('q')
    saved_queries = UserQuery.objects.filter(query=query)
    temp = dict()

    for q in saved_queries:
        if not q.is_expired() and Result.objects.filter(qid=q.qid).exists():
            results = Result.objects.filter(qid=q.qid)
            temp['google_patents'] = results.filter(search_engine='GOOGLE PATENTS').values()
            temp['lens'] = results.filter(search_engine='LENS').values()
            temp['patentscope'] = results.filter(search_engine='PATENTSCOPE').values()
            break
    else:
        # Save entered query to DB
        q = UserQuery(query=query)
        q.save()
        
        # Apply multi-threading
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [
                executor.submit(google_patents),
                executor.submit(lens),
                executor.submit(patentscope),
            ]

            # Save results of finished threads
            for f in concurrent.futures.as_completed(results):
                temp.update(f.result())

        # Insert all gathered data into database       
        for r in sum(temp.values(), []):
            Result(**r).save()
    
    # Aggregates results to one variable and put them in between each other
    merged_results = zip_longest(temp['google_patents'], temp['lens'], temp['patentscope'])
    # Removing None values
    all_results = [x for x in sum(merged_results, ()) if x is not None]

    # Apply pagination
    paginator = Paginator(all_results, 10)
    page = request.GET.get('page', 1)

    try:
        returned_result = paginator.page(page)
    except PageNotAnInteger:
        returned_result = paginator.page(1)
    except EmptyPage:
        returned_result = paginator.page(paginator.num_pages)

    context = {
        # To show it in the search box
        'query': query,
        # Main results
        'search_results': returned_result,
    }

    return render(request, 'search_results.html', context)
