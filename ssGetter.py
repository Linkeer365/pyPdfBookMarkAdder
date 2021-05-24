import requests
from bs4 import BeautifulSoup
from lxml import etree

import json

root_url="http://book.ucdrs.superlib.net/"
base_url_name1="http://book.ucdrs.superlib.net/search?sw="
base_url_name2="&allsw=&bCon=&ecode=utf-8&channel=search&Field=all"
base_url_isbn="http://book.ucdrs.superlib.net/search?sw="

query_input=input("输入 书名 或 ISBN号:\n{书名开头请标注name,isbn开头请标注isbn，用::当分隔符}\t")
input=query_input.split("::")[-1]
headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}


def fetch_num_from_page(url,file_name):
    print(url)
    resp=requests.get(url,headers=headers)
    resp.encoding="utf-8"
    text=resp.text
    # print("Headers:{}".format(resp.headers))
    # soup=BeautifulSoup(text,"html.parser")
    # print(soup.prettify())
    html=etree.HTML(text)



    # https://www.jianshu.com/p/1575db75670f
    ss_vals=html.xpath("//input[contains(@id,'ssid') and contains(@name,'.ssid')]/@value")

    links=html.xpath("//a[@class='px14' and @target='_blank']/@href")
    # 相同的网站会有重复的情况，所以用奇偶数把他们分开
    links=[root_url+link for idx,link in enumerate(links) if idx%2==0]


    # print(links)
    # print(ss_vals)
    intros=[]
    for each_link in links:
        resp=requests.get(each_link,headers=headers)
        resp.encoding="utf-8"
        text=resp.text
        html=etree.HTML(text)
        intro: [str]
        intro=html.xpath("//input[@name='content' and @type='hidden']/@value")
        titles=html.xpath("//input[@name='title' and @type='hidden']/@value")

        print(intro)
        print(titles)



        if not intro==[] and not titles==[]:
            piece_str="".join([titles[0],"\r\n",intro[0]])
            pieces=piece_str[0].split("\n")
            print(piece_str)
        else:
            print("kaka")
    print("done.")
        # soup=BeautifulSoup(text,"lxml")
        # print(soup.prettify())

    # soup=BeautifulSoup(text,"lxml")
    # finds=soup.find_all(attrs={"id":"ssid0","name":"f[0].ssid"})
    #
    # vals=[find["value"] for find in finds]

    # print(soup.prettify())

if query_input.startswith("name"):
    book_input=input
    print("nana")
    url=base_url_name1+book_input+base_url_name2
    fetch_num_from_page(url,book_input)
elif query_input.startswith("isbn"):
    isbn_input=input
    print("isis")
    url=base_url_isbn+isbn_input
    fetch_num_from_page(url,isbn_input)




