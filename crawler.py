from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from newspaper import Article
import requests

def search_news(query: str):
    # 設定要搜尋的關鍵字
    print("enter")
    search_keyword = query

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options,executable_path='./chromedriver.exe')


    # 開啟 Chrome 瀏覽器
    # driver = webdriver.Chrome()
    print("here")
    # 前往 Google 新聞網站
    driver.get("https://news.google.com/")

    # 找到搜尋框，輸入關鍵字並按下 Enter 鍵
    # search_box = driver.find_element("name","q")
    search_box = driver.find_element(by = By.XPATH, value = "//input[@type='text']")
    search_box.send_keys(search_keyword)
    search_box.send_keys(Keys.RETURN)

    # 等待搜尋結果頁面載入完成
    driver.implicitly_wait(3)

    # 找到搜尋結果列表中的所有文章標題和連結
    search_results = driver.find_elements(by = By.XPATH, value = "//h3[@class='ipQwMb ekueJc RD0gLb']/a")

    # 存所有url、title
    result_titles = []
    result_urls = []
    for result in search_results:
        result_titles.append(result.text)
        result_urls.append(result.get_attribute("href"))

    # 目前只取第一個搜尋結果
    for title, url in zip(result_titles[:1], result_urls[:1]):
        news = Article(url, language='zh')
        news.download()
        news.parse()
        
        news_example = {
            "body": news.text,
            "headline": title,
            "release_time":"2023-08-10T11:28:50.86",
        }

        # # construct kg
        # url = "http://140.116.245.152:8000/show_kg" # url
        # response = requests.post(url, json = news_example)

        # status = response.json()
        # print(status)
        # print(status['news_id'])
        # # show_kg(status['news_id'])
        # id = status['news_id']

        return news_example