from bs4 import BeautifulSoup
import requests
import chardet
import re

#对网页进行解析
def create_bs(url):
    response=requests.get(url)
    e=chardet.detect(response.content)
    response.encoding=e["encoding"]
    c=response.content
    soup=BeautifulSoup(c,'html.parser')
    return soup

#获取网页的集合
def build_urls(prefix,suffix):
    urls=[]
    for i in suffix:
        url=prefix+i
        urls.append(url)
    return urls

#爬取主题和链接
def find_title_link(soup):
    tittles=[]
    links=[]
    try:
        contanier=soup.find('div',{'class':'container_padd'})

        table=contanier.find('form',{'id':'ajaxtable'})
        page_list=table.find_all('li')
        for page in page_list:
            tittlelink=page.find('a',{'class':'truetit'})
            if tittlelink.text==None:#此处标题被加粗展示
                title=tittlelink.find('b').text
            else:
                title=tittlelink.text
            link=tittlelink.get('href')
            tittles.append(title+"*      *")
            links.append(link)
    except:
        print('have none value')
    return tittles,links
#爬取除主楼外的回复
def find_res(soup):
    try:
        res_num_class = soup.find(attrs={'class': 'browse'})
        num_string = str(res_num_class.span)
        num=int(re.findall('(\d+)',num_string)[0])#获得此篇帖子的回复量
        replies = ['0' for _ in range(num + 1)]#将一篇帖子*第一页*的所有回复放进replies这个列表
        details=soup.find('div',{'class':'hp-wrap details'})
        floors=details.find_all('div',{'class':'floor'})
        for floor in floors:
            floor_num=floor.find('a',{'class':'floornum'})
            num=int(floor_num.get('id'))
            table = floor.find('table', {'class': 'case'})
            if table.find('td').text!=None:
                replies[num]=str(table.find('td').text)
            else:
                replies[num]=str(table.find('p').text)
    except:
        return None
    return replies

url='https://bbs.hupu.com/pubg'
url_suffix=['']#仅爬取虎扑绝地求生区第一页内容
urls=build_urls(url,url_suffix)

tittles_group=[]
links_group=[]
for u in urls:
    all_soup=create_bs(u)#对绝地求生区第一页进行解析
    tittles,links=find_title_link(all_soup)
    for tittle in tittles:
        tittles_group.append(str(tittle))
    for link in links:
        links_group.append(str(link))

replies_group=[]
reply_urls=build_urls('https://bbs.hupu.com',links_group)
print("标题总数",len(tittles_group))
for l in reply_urls:
    soup=create_bs(l)#解析帖子
    replies=find_res(soup)
    if replies!=None:#此帖有回复
        replies_group.append(replies)
        print(replies[0])
    else:#此帖无回复
        print(l)

        replies_group.append(None)

f=open("crawler.txt","wb")
crawler=str()
for tittle in tittles_group:
    crawler+=tittle
for replies in replies_group:
    if replies==None:
        empty="No replies.\n"
        crawler+=empty
    else:
        for reply in replies:
            crawler+=reply
crawler+="the end"
f.write(crawler.encode("utf8"))
f.close()

