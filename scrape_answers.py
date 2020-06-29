import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


def send_question(value):
    # create a chrome web driver
    driver = webdriver.Chrome()
    # load a web page with the given url
    driver.get('https://stackoverflow.com')

    # find the 'search input' web element by xpath
    searchbutton = driver.find_element_by_xpath('//*[@id="search"]/div/input')

    url = ''
    if searchbutton.is_displayed():
        # simulate typing into the element
        searchbutton.send_keys(value)
        # press enter on the input field
        searchbutton.send_keys(Keys.RETURN)
        url = driver.current_url

    driver.quit()

    return url


def get_results_page(content):
    soup = BeautifulSoup(content.text, features='lxml')
    results_content = soup.select('div.question-summary')
    return results_content


def get_answer_links(search_results):
    answer_links = []
    count_answers = 0
    accepted_results = 0
    for n, result in enumerate(search_results):
        result_str = str(result)
        result_soup = BeautifulSoup(result_str, features='lxml')

        status_elements = result_soup.select('div.statscontainer div.status.answered-accepted strong')
        answers = int(status_elements[0].get_text()) if status_elements else 0
        if answers > 0:
            answer_link = result_soup.select('div.summary h3 a')[0].get('href')
            answer_url = 'https://stackoverflow.com' + answer_link
            answer_links.append(answer_url)
            count_answers += answers
            accepted_results += 1

        if count_answers >= 10 or accepted_results >= 5:
            break

    return answer_links


def get_answers(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        print('\nFailed to establish connection.\n')
    else:
        answer_soup = BeautifulSoup(response.text, features='lxml')
        user_question = answer_soup.select(
            'div#question div.post-layout div.postcell.post-layout--right div.post-text')[0].get_text()
        qtn = '#' * 100 + '\n' + 'Question'.center(100, '-') + '\n' + '#' * 100 + '\n' + \
              user_question + '#' * 100 + '\n\n'

        answer_elements = answer_soup.select('div#answers div.answer div.answercell.post-layout--right div.post-text')
        answers = []
        for n, answer_element in enumerate(answer_elements):
            answer_text = answer_element.get_text()
            ans = '#' * 100 + '\n' + f'Answer {n+1}'.center(100, '-') + '\n' + '#' * 100 + '\n'\
                  + answer_text + '#'*100 + '\n\n\n'
            answers.append(ans)

        with open('results.txt', 'w') as f:
            file_content = qtn
            for answer in answers:
                file_content += answer
            file_content += ('\n'*5)
            f.write(file_content)


question = input('Please, forward your question: ')

current_url = send_question(question)

try:
    res = requests.get(current_url)
except requests.exceptions.RequestException:
    print('\nFailed to establish connection.\n')
else:
    results = get_results_page(res)
    if results:
        result_links = get_answer_links(results)
        if result_links:
            for result_link in result_links:
                get_answers(result_link)
            print('Answer saved in results.txt ...')
    else:
        print('Sorry, no results.')

print('Finished!!!')
