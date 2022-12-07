# coding=utf-8
from ast import Try
from lib2to3.pgen2 import driver
import os
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import time
import json
import urllib.request
import requests
import asyncio
import configparser
import platform

if platform.system() == "Windows":
    #file = "D:\\workhome\\pve2600x\\mainjd.ini"
    file = "mainjd.ini"
elif platform.system() == "Linux":
    file = 'mainjd.ini'
options2 = Options()
options2.add_argument("--headless")
options2.add_argument('--no-sandbox')
options2.add_argument('--disable-dev-shm-usage')

# 选定浏览器内核
browser2 = webdriver.Chrome(
    options=options2)  # Chrome # Edge # Safari # Firefox
browser2.set_window_size(5000, 5000)


async def imgdownload(browsers, filename, brand):

    #browser.implicitly_wait(0.5)
    try:
        if filename != 'none':
            filename = filename.replace("'", '')
            file_name = filename.split('/')[-1]
            filenamenohttp = filename.split('.com/')[1]

            if os.path.exists("imagesfile/" + brand) == False:
                os.makedirs("imagesfile/" + brand)

            #f = open(filenamenohttp, 'wb')
            browser2.get(filename)
            with open("imagesfile/" + brand + "/" + file_name, 'wb') as file:
                #identify image to be captured
                try:

                    l = browser2.find_element_by_tag_name('img')
                    #write file
                    file.write(l.screenshot_as_png)
                    #browser.quit()
                    print("imagesfile/" + brand + "/" + file_name)
                except Exception as e:
                    pass

            #f.close()
            #print("download successful")
            #time.sleep(2)
            url = "imagesfile/" + brand + "/" + file_name
            return url
    except Exception as e:
        pass
    #driver = webdriver.Chrome()
    #driver.implicitly_wait(0.5)
    #driver.maximize_window()

    #close browser


def get_item_classes(browser, url):
    browser.get(url)
    time.sleep(2)
    #browser.find_element_by_css_selector(
    #    'a[class="sl-e-more J_extMore"]').click()
    time.sleep(1)
    html_page = browser.page_source
    soup = BeautifulSoup(html_page, "html.parser")
    filenamenohttp = url.split('/list.html')[0]
    classes = []
    for li in soup.select('li[id*=brand-]'):
        classes.append(filenamenohttp + li.a.get('href'))
    return classes


def get_item_urls(browser, url, limit=-1):
    browser.get(url)
    item_urls = []
    pg_cnt = 0
    while True:
        time.sleep(1)

        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(0.5)
        info = browser.find_elements_by_class_name('gl-i-wrap')
        page_urls = []
        for line in info:
            page_urls.append(
                line.find_element_by_class_name('p-img').
                find_element_by_tag_name('a').get_attribute('href'))

        pg_cnt += 1
        print("page:", pg_cnt, "\titem num:", len(page_urls))
        print(page_urls)
        item_urls += page_urls
        if len(browser.find_elements_by_css_selector(
                'a[class="pn-next"]')) == 0:
            break
        else:
            if limit == -1 or pg_cnt < limit:
                buton = browser.find_element_by_css_selector(
                    'a[class="pn-next"]')
                browser.execute_script("arguments[0].click()", buton)
                #time.sleep(1)
                #print("pn-nextid")
            else:
                break
    return item_urls


async def parse_item_pages(browser, urls, limit=-1, brandss="default"):
    pages = []
    if urls is None:
        return pages

    # 爬取类别下的品牌名称
    con = configparser.ConfigParser()
    con.read(file, encoding='utf-8')

    start = con.get("jd", "end")
    for i, url in enumerate(urls):
        #print(i, url)
        indexss = i
        if i < int(start):
            continue
        #print("从" + start +
        #      "开始======================================================")
        if i % 20 == 0:
            print("current url NO.", i, "\ttotal:", len(urls))
        page = {}
        browser.get(url)
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(2)
        #browser.execute_script(
        #    "window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(3)

        if len(browser.find_elements_by_class_name("sku-name")) != 0:
            page["title"] = browser.find_element_by_class_name("sku-name").text
        else:
            page["title"] = ""

        #print(page["title"])
        js = """
        var pid=pageConfig;
        return pid;
        
        """
        try:
            page['pid'] = browser.find_elements_by_class_name(
                'J-follow')[0].get_attribute('data-id')
        except Exception as e:
            pass
        try:
            page['comcount'] = browser.find_elements_by_class_name(
                'J-comm-' + str(page['pid']))[0].text
        except Exception as e:
            pass

        if len(browser.find_elements_by_class_name("p-price")) != 0 and len(
                browser.find_element_by_class_name(
                    "p-price").find_elements_by_xpath("span")) > 1:
            page["price"] = browser.find_element_by_class_name(
                "p-price").find_elements_by_xpath("span")[1].text
        else:
            page["price"] = ""

        spce = []
        if len(browser.find_elements_by_id('comment-count')) != 0:
            if len(
                    browser.find_element_by_id(
                        'spec-list').find_elements_by_tag_name('img')) != 0:
                element = browser.find_element_by_id(
                    'spec-list').find_elements_by_tag_name('img')
                for i in element:
                    imgsr = str(i.get_attribute('src')).replace(
                        'n5', 'n1').replace('s54x54_jfs', 'jfs')
                    imgsrnothtp = await imgdownload(browser, imgsr, brand)
                    spce.append(imgsrnothtp)

            else:
                page["spec-list"] = ""
        else:
            page["spec-list"] = ""
        page["image"] = spce

        bodyspce = []
        try:
            if len(browser.find_elements_by_class_name(
                    'ssd-module-wrap')) != 0:
                if len(browser.find_elements_by_class_name(
                        'ssd-module-wrap')) != 0:
                    element = browser.find_elements_by_class_name('ssd-module')

                    #print(len(element))
                    #print(element)
                    for i in element:
                        #cssid = i.get_attribute('data-id')
                        imgsr = str(i.value_of_css_property(
                            "background-image")).replace('url("',
                                                         '').replace('")', '')
                        imgsrnothtp = await imgdownload(browser, imgsr, brand)
                        bodyspce.append(imgsrnothtp)

                elif len(browser.find_element_by_id('J-detail-content')) != 0:
                    element = browser.find_element_by_id(
                        'J-detail-content').find_elements_by_tag_name('img')
                    for i in element:
                        #cssid = i.get_attribute('data-id')
                        imgsr = str(i.value_of_css_property(
                            "background-image")).replace('url("',
                                                         '').replace('")', '')
                        if imgsr == None:
                            imgsr = str(i.get_attribute('src'))

                        imgsrnothtp = await imgdownload(browser, imgsr, brand)
                        bodyspce.append(imgsrnothtp)

                else:
                    page["bodyimage"] = ""
            elif browser.find_element_by_id('J-detail-content') != None:
                elementab = browser.find_element_by_id(
                    'J-detail-content').find_elements_by_tag_name('img')
                for i in elementab:
                    #cssid = i.get_attribute('data-id')

                    imgsr = str(i.get_attribute('src'))
                    imgsrnothtp = await imgdownload(browser, imgsr, brand)
                    bodyspce.append(imgsrnothtp)
            else:
                page["bodyimage"] = ""
        except Exception as e:
            continue
        bodyspce.reverse()

        page["bodyimage"] = bodyspce
        '''
        if len(browser.find_elements_by_id('comment-count')) != 0:
            if len(
                    browser.find_element_by_id(
                        'comment-count').find_elements_by_tag_name('a')) != 0:
                page["total_comment_num"] = browser.find_element_by_id(
                    'comment-count').find_element_by_tag_name('a').text
            else:
                page["total_comment_num"] = ""
        else:
            page["total_comment_num"] = ""

        if len(browser.find_elements_by_class_name('percent-con')) != 0:
            page["overall_score"] = browser.find_element_by_class_name(
                'percent-con').text
        else:
            page["overall_score"] = ""

        tag_list = []
        tags = browser.find_elements_by_class_name(' tag-1')
        for tag in tags:
            tag_list.append(tag.text)
        page["overall_tag_list"] = tag_list

        if len(browser.find_elements_by_id('comm-curr-sku')) != 0:
            browser.find_element_by_id('comm-curr-sku').send_keys(Keys.SPACE)
            time.sleep(1)

        if len(browser.find_elements_by_class_name('filter-list')) != 0:
            page["current_comment_num"] = browser.find_element_by_class_name(
                'filter-list').find_elements_by_tag_name('em')[0].text
        else:
            page["current_comment_num"] = ""
        current_tag_list = []
        if len(browser.find_elements_by_class_name('filter-list')) != 0:
            single_tags = browser.find_element_by_class_name(
                'filter-list').find_elements_by_tag_name('li')[1:7]
            for each in single_tags:
                current_tag_list.append(
                    each.find_element_by_tag_name('a').text)
        page["current_tag_list"] = current_tag_list

        attr_val = []
        if len(
                browser.find_elements_by_css_selector(
                    'li[data-tab="trigger"][clstag="shangpin|keycount|product|pcanshutab"]'
                )) != 0:
            browser.find_element_by_css_selector(
                'li[data-tab="trigger"][clstag="shangpin|keycount|product|pcanshutab"]'
            ).click()
            time.sleep(2)
            dt = [
                x.text for x in browser.find_element_by_class_name(
                    "Ptable").find_elements_by_tag_name("dt")
                if x.text.strip() != ""
            ]
            dd = [
                x.text for x in browser.find_element_by_class_name(
                    "Ptable").find_elements_by_tag_name("dd")
                if x.text.strip() != ""
            ]
            if len(dt) == len(dd):
                attr_val = [[dt[i], dd[i]] for i in range(len(dt))]
            else:
                print("error in parsing attr_val")
        page["attr_val"] = attr_val

        comments_in_pages = []
        if len(
                browser.find_elements_by_css_selector(
                    'li[data-tab="trigger"][data-anchor="#comment"]')) != 0:
            browser.find_element_by_css_selector(
                'li[data-tab="trigger"][data-anchor="#comment"]').click()
            time.sleep(2)
            pg_cnt = 0
            while True:
                time.sleep(2)
                browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                divs = browser.find_element_by_id(
                    'comment-0').find_elements_by_class_name('comment-item')
                page_comment = []
                for each in divs:
                    single = {}
                    if each.find_element_by_class_name(
                            "user-level").find_elements_by_tag_name('a'):
                        single["membership"] = "PLUS会员"
                    else:
                        single["membership"] = "普通会员"
                    single["star"] = each.find_element_by_class_name(
                        'comment-column').find_element_by_tag_name(
                            'div').get_attribute('class').split(
                                "comment-star star")[1]
                    single["text"] = each.find_element_by_class_name(
                        'comment-column').find_element_by_tag_name('p').text
                    spans = each.find_element_by_class_name(
                        'order-info').find_elements_by_tag_name('span')
                    order_detail = []
                    for index, everyone in enumerate(spans):
                        order_detail.append(spans[index].text)
                    single["order_detail"] = order_detail
                    page_comment.append(single)
                pg_cnt += 1
                print("page:", pg_cnt, "\tcomment num:", len(page_comment))
                comments_in_pages += page_comment

                if len(
                        browser.find_elements_by_css_selector(
                            'a[class="ui-pager-next"][href="#comment"][clstag="shangpin|keycount|product|pinglunfanye-nextpage"]'
                        )) == 0:
                    break
                else:
                    if limit == -1 or pg_cnt < limit:
                        browser.find_elements_by_class_name(
                            'ui-pager-next')[0].send_keys(Keys.ENTER)
                    else:
                        break

        page["comments_in_pages"] = comments_in_pages
        '''
        #print(page)
        with open("data_" + brand + ".txt", "a+") as fw:
            #for d in page:
            fw.write(json.dumps(page) + ",\n")
        con = configparser.ConfigParser()
        con.read(file, encoding='utf-8')
        #sections = con.sections()
        #items = con.items('runcount')
        con.set("jd", "end", str(indexss))
        con.write(open(file, "w"))
        #fw.close()
        pages.append(page)

    return pages


def get_brand(c):
    if c.find("i-list.jd.com") > 0:
        return urllib.parse.unquote(c.split("ev=exbrand")[1].split("品牌_")[1])
    if c.find("list.jd.com") > 0:
        ress = urllib.parse.unquote(c.split("exbrand_")[1].split("%5E&")[0])
        return ress
    elif c.find("brand=") < 0:
        return urllib.parse.unquote(c.split("keyword=")[1])
    else:
        return urllib.parse.unquote(c.split("brand=")[1])


if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 选定浏览器内核
    browser = webdriver.Chrome(
        options=options)  # Chrome # Edge # Safari # Firefox

    # imgdownload(
    #    browser,
    #    "https://img30.360buyimg.com/sku/jfs/t1/196082/1/222/96907/6088c374Ea723f59e/8c04fc141f53f2db.jpg"
    #)

    CLASS_LIMIT = 100  # 爬取的目标类别下的品牌数上限
    PAGE_LIMIT = 20  # 爬取的每一品牌下商品的页数（每页60个商品，-1表示爬取全部商品）
    COMMENT_LIMIT = 1

    con = configparser.RawConfigParser()
    con.read(file, encoding='utf-8')
    # 爬取类别下的品牌名称
    con = configparser.RawConfigParser()
    con.read(file, encoding='utf-8')
    sections = con.sections()
    items = con.items('jd')

    jdurl = con.get("jd", "classurl")
    start = con.get("jd", "end")

    print("读取配置成功 " + jdurl + "开始执行" + start)
    #print(items)
    #exit()
    CLASS_URL = jdurl  # 需制定类别URL
    if os.path.exists("classes.txt"):
        classes = []
        with open("classes.txt", "r") as fr:
            for line in fr:
                classes.append(line.strip())
    else:
        classes = get_item_classes(browser, CLASS_URL)
        with open("classes.txt", "w") as fw:
            for c in classes:
                fw.write(c + "\n")

    print("__Done! classes")

    # 依据品牌列表，爬取每一品牌下的商品
    matches = [f for f in os.listdir() if f.startswith("item_urls")]
    if len(matches) != 0:
        item_urls = []
        for m in matches:
            i_u = []
            with open(m, "r") as fr:
                for line in fr:
                    i_u.append(line.strip())
            item_urls.append(i_u)
    else:
        item_urls = []
        for c in classes[:min(CLASS_LIMIT, len(classes))]:
            print("extract brand:", get_brand(c))
            item_urls.append(get_item_urls(browser, c, limit=PAGE_LIMIT))
        for i in range(len(item_urls)):
            with open("item_urls_" + get_brand(classes[i]) + ".txt",
                      "w") as fw:
                for item in item_urls[i]:
                    fw.write(item + "\n")

    #print(matches)
    print("__Done! item_urls")

    # 依据商品列表，爬去每一商品的信息
    for i, urls in enumerate(item_urls):

        if len(matches) == 0:
            brand = get_brand(c)
        else:
            brand = matches[i].split("urls_")[1][:-4]
        brandss = brand
        stindex = con.get("jd", "index")
        if i < int(stindex):
            continue
        con.set("jd", "index", str(i))
        con.write(open(file, "w"))

        print("开始第" + str(i) + "个文件，共" + str(len(item_urls)) + "个文件" + brandss)
        data = asyncio.run(
            parse_item_pages(browser,
                             urls,
                             limit=COMMENT_LIMIT,
                             brandss=brandss))
        print("进行运行1次")
        start = con.set("jd", "end", "0")
        con.write(open(file, "w"))
        #start = con.set("jd", "end", "0")

    #print("brand:", brand, "\tdata num:", len(data))

    print("__Done! data")

    browser.close()
    browser.quit()
