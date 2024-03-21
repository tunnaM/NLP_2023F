from bs4 import BeautifulSoup
import requests
import os
import re
import json
import time

start_date = '20190316'
end_date = '20190330'
days_list1 = [31,28,31,30,31,30,31,31,30,31,30,31]  # 平年每月的天数列表
days_list2 = [31,29,31,30,31,30,31,31,30,31,30,31]
turn = 0
total_length = 187935

def UAPool():
    global turn  # 用于切换用户代理
    agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 QIHU 360SE',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ServiceUI 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
              'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1 Firefox 4.0.1 – Windows',
              'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
              'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11 Chrome 17.0 – MAC',
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'
              ]
    turn += 1
    return {'User-Agent':agents[turn % 11]}


def CreateDate(start_date, end_date):  # 制作日期列表,避免出现跨月份或者跨年份的日期使得url错误

    print('CreateDate开始')
    date_list = []  # 存放最终日期列表
    days_list = []

    year1 = int(start_date[:4])
    month1 = int(start_date[4:6])
    day1 = int(start_date[6:])

    year2 = int(end_date[:4])
    month2 = int(end_date[4:6])
    day2 = int(end_date[6:])

    for i in range(year1, year2 + 1):
        if (i % 4 == 0 and i % 100 != 0) or i % 400 == 0:  # 闰年
            if year2 > year1 and i == year1:
                days_list.append(days_list2[month1 - 1:])

            elif year2 == year1:
                days_list.append(days_list2[month1 - 1:month2])

            elif year2 > year1 and i == year2:
                days_list.append(days_list2[:month2])

            else:
                days_list.append(days_list2[::])

        else:
            if year2 > year1 and i == year1:
                days_list.append(days_list1[month1 - 1:])

            elif year2 == year1:
                days_list.append(days_list1[month1 - 1:month2])

            elif year2 > year1 and i == year2:
                days_list.append(days_list1[:month2])

            else:
                days_list.append(days_list1[::])

    for i in range(len(days_list)):
        for j in range(len(days_list[i])):
            for k in range(days_list[i][j]):
                if year1 == year2:
                    if month1 == month2:
                        if day1 > day2:
                            break
                        date_list.append('{}{:0>2d}{:0>2d}'.format(year1, month1 + j, day1))
                    else:
                        if day1 > days_list[i][j]:
                            break
                        date_list.append('{}{:0>2d}{:0>2d}'.format(year1, month1 + j, day1))
                else:
                    if day1 > days_list[i][j]:
                        break
                    date_list.append('{}{:0>2d}{:0>2d}'.format(year1, month1 + j, day1))
                day1 += 1

            month1 += 1
            day1 = 1

        year1 += 1
        month1 = 1
        if year1 + i >= year2:
            return date_list


# 网址格式：https://www.haodf.com/sitemap-zx/20200101_1/
def GetUrl(date_list):  # 获取日期所对应的网址

    print('GetUrl开始')
    url_list = []  # 存放最终url链接
    url_list1 = [r'https://www.haodf.com/sitemap-zx/{}'.format(x) for x in date_list]  # 收集链接中到
 
    for i in url_list1:
        url_list2 = []  # 存放某一天的url链接
        try:
            r = requests.get(i+'_1/',headers=UAPool())
            r.raise_for_status()
            r.encoding = 'gbk'
        except:
            time.sleep(10)
            continue

        soup = BeautifulSoup(r.text, parser='html.parser', features='lxml')
        l = soup.find_all('a', attrs={'class':'page_turn_a'})
        page_max = max([int(i.text) for i in l])
        
        for j in range(page_max):
            url_list2.append(i+'_'+str(j+1)+'/')

        url_list.append(url_list2)
        time.sleep(2)
    return url_list


def GetDetailpage(url_list):  # 获取详细咨询页面网址

    print('GetDetailpage开始')
    global total_length
    detailpage_list = []  # 全部url链接(三维列表，第一维：日期，第二维：页面，第三维：详细页面链接)
    for i in url_list:

        url_list1 = []  # 每天的url链接
        for j in i:
            
            url_list2 = []  # 每页的url链接
            try:
                r = requests.get(j,headers=UAPool())
                r.raise_for_status()
                r.encoding = 'gbk'
            except:
                time.sleep(4)
                continue
            soup = BeautifulSoup(r.text, parser='html.parser', features='lxml')
            for k in soup.find_all('a'):
                if r.text != '':
                    href = k.get('href')
                    if str(href).__contains__('doctorteam') or str(href).__contains__('wenda'):
                        url_list2.append('http:'+href)
            total_length += len(url_list2)
            url_list1.append(url_list2)
            time.sleep(5)
        detailpage_list.append(url_list1)

    return detailpage_list


def SaveHtml(detailpage_list, date_list):  # 保存每个日期中的100个问诊页面的html文件

    print('SaveHtml开始')
    path_p = r'E:\0、大四上\2、文本挖掘 项目\项目\0、数据爬取\SaveHtml'
    if not os.path.exists(path_p):
        os.mkdir(path_p)
    for i in range(len(detailpage_list)):
        path_c = path_p + r'\{}'.format(date_list[i])
        if not os.path.exists(path_c):
            os.mkdir(path_c)
        os.chdir(path_c)
        temp_list = detailpage_list[i][0][:]
        num = 0
        for page in temp_list:
            try:
                r = requests.get(page, headers=UAPool())
                r.raise_for_status()
                r.encoding = 'gbk'
            except:
                time.sleep(2)
                continue
            try:
                soup = BeautifulSoup(r.text, parser='html.parser', features='lxml')
                # “ ? *: " < > \ / | ” 敏感字符不可出现在文件名中
                post_title = soup.find_all('div', attrs={'class': 'fl-title ellps'})[0].text.replace('?', ',').replace('*', ',').replace(':', ',').replace('"', ',').replace('<', ',').replace('>', ',').replace('\\', ',').replace('/', ',').replace('|', ',')
                with open(post_title+'.html', 'w', encoding='utf-8') as f:
                    f.write(r.text.replace('<meta charset="gbk">', '<meta charset="utf-8">'))
                num += 1
            except:
                continue
            if num >= 100:
                break
            time.sleep(2)


def AnalysisWeb(detailpage_list, date_list):

    print('AnalysisWeb开始')
    global total_length  # 所需爬取总数
    completion_schedule = 0  # 完成进度
    fail_num = 0
    if not os.path.exists(r'E:\0、大四上\2、文本挖掘 项目\项目\0、数据爬取\detailpageinfo'):
        os.mkdir(r'E:\0、大四上\2、文本挖掘 项目\项目\0、数据爬取\detailpageinfo')
    os.chdir(r'E:\0、大四上\2、文本挖掘 项目\项目\0、数据爬取\detailpageinfo')
    day_num = 0
    for day in detailpage_list:  # 每天
        post_list = []

        for page in day:  # 每页
            for context in page:  # 每页中的咨询链接
                info_list = []
                info_dict = {}
                print("\r已完成:{}  失败:{}  总共需完成:{}  完成进度:{:.2f}%".format(completion_schedule, fail_num, total_length, (completion_schedule / total_length) * 100), end='')
                try:
                    r = requests.get(context,headers=UAPool())
                    r.raise_for_status()
                    r.ecoding = 'gbk'
                except:
                    fail_num += 1
                    time.sleep(5)
                    continue

                soup = BeautifulSoup(r.text, parser='html.parser', features="lxml")

                try:  # 防止因网页反爬机制而导致爬取数据出错使程序崩溃
                    # 医生名字
                    doc_name = soup.find_all('h1', attrs={'class', 'doctor-name'})[0].text
                    info_dict['doc_name'] = doc_name

                    # 职称
                    job_title = soup.find_all('span', attrs={'class': 'positon'})[0].text.replace(' ', '').replace('\n',' ').lstrip(' ')
                    info_dict['job_title'] = job_title

                    # 医生所在单位  所在部门
                    affiliate, department = soup.find_all('p', attrs={'class', 'doctor-faculty'})[0].text.replace(' ','').replace('\n', ' ').lstrip(' ').rstrip(' ').split(' ')
                    info_dict['affiliate'] = affiliate
                    info_dict['department'] = department

                    # 医生对应的url
                    url = soup.find_all('a', attrs={'class', 'tab-item first'})[0].get('href')
                    info_dict['url'] = r'https:' + url

                    # 标题内容存在<div class='fl-title ellps'>标签下
                    post_title = soup.find_all('div', attrs={'class': 'fl-title ellps'})[0].text
                    info_dict['post_title'] = post_title

                    # 回复内容
                    '''
                    由于每个咨询帖子的第一个问题是叙述病人的基本状况，且叙述中包含不定个'p','h2','h4'标签，
                    若与其他的问答一起解析的话不容易将第一个问题的详细信息完全归纳在一起，
                    因此我将描述病人情况的模块与后面问答的模块分开分析，这样就比较容易得到各自的内容。

                    将他们写在循环里是因为每个咨询的问题的页面数不定，
                    通过<a class:'page_turn_a'>这个标签来查看总共有多少页
                    '''
                    # 爬取页面一

                    context1 = soup.find_all('div', attrs={'class': "f-c-r-content"})
                    
                    # 发言对象
                    obj = soup.find_all('div', attrs={'class': re.compile('^f-c-l')})
                    obj_list1 = []
                    for i in obj:
                        if i.attrs == {'class': ['f-c-l-patient']}:
                            obj_list1.append('question')
                        elif i.attrs == {'class': ['f-c-l-doctor']}:
                            obj_list1.append('QA')

                    soup2 = BeautifulSoup(str(context1[0]), parser='html.parser', features="lxml")
                    question = [i.text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                                for i in soup2.find_all(name=('p', 'h2', 'h4'), attrs={'class': re.compile(r'^f-c-r')})
                                if i.attrs != {'class': ['f-c-r-w-title']} and i.attrs != {'class': ['f-c-r-tip']}]
                    
                    firstquestion = []  # 用户病情描述
                    j = 0
                    for i in range(len(question) // 2):
                        firstquestion.append(question[j] + ':' + question[j + 1])
                        j += 2


                    # 对应时间
                    time1 = soup.find_all('div', attrs={'class': 'f-c-l-date'})
                    time_list = [i.text for i in time1]
                    
                    # 咨询内容,未添加日期的对话信息
                    answer_list1 = []
                    for i in context1[1:]:
                        soup3 = BeautifulSoup(str(i), parser='html.parser', features="lxml")
                        answer1 = soup3.find_all(name=('p', 'h2', 'h4'), attrs={'class': re.compile(r'^f-c-r')})
                        if answer1 != []:
                            s = ''
                            for j in answer1:
                                if j.attrs != {'class': ['f-c-r-w-title']}:
                                    s = s + j.text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                            answer_list1.append(s)

                        else:
                            text = i.text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                            s = text
                            try:
                                int(s.strip('″').strip('′'))
                                answer_list1.append("语音:"+text)
                            except:
                                answer_list1.append(text)

                    # 爬取第一页的后面页数
                    max_page = 1
                    page_num_list = soup.find_all('a', attrs={'class': "page_turn_a"})
                    if len(page_num_list):
                        for i in page_num_list:
                            try:
                                max_page = int(i.text)  # 获取最大页面数
                            except:
                                pass

                    page_num = 2
                    while(page_num <= max_page):
                    
                        url_c = context[:len(context)-4]+'_'+str(page_num)+'.htm'
                        page_num += 1
                        try:
                            r_c = requests.get(url_c, headers=UAPool())
                            r_c.raise_for_status()
                            r_c.ecoding = 'gbk'
                        except:
                            fail_num += 1
                            time.sleep(5)
                            continue
                        soup_c = BeautifulSoup(r_c.text, parser='html.parser', features="lxml")
                        
                        # 时间
                        time_list.extend([i.text for i in soup_c.find_all('div', attrs={'class': 'f-c-l-date'})])

                        # 发言对象
                        obj = soup_c.find_all('div', attrs={'class': re.compile('^f-c-l')})
                        for i in obj:
                            if i.attrs == {'class': ['f-c-l-patient']}:
                                obj_list1.append('question')
                            elif i.attrs == {'class': ['f-c-l-doctor']}:
                                obj_list1.append('answer')
                                
                        context1 = soup_c.find_all('div', attrs={'class': "f-c-r-content"})
                        for i in context1:
                            soup1 = BeautifulSoup(str(i), parser='html.parser', features="lxml")
                            answer1 = soup1.find_all( name=('p', 'h2', 'h4'), attrs={'class': re.compile(r'^f-c-r')})
                            if answer1 != []:
                                s = ''
                                for j in answer1:
                                    if j.attrs != {'class': ['f-c-r-w-title']}:
                                        s = s + j.text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                                answer_list1.append(s)

                            else:
                                text = i.text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                                s = text
                                try:
                                    int(s.strip('″').strip('′'))
                                    answer_list1.append("语音:"+text)
                                except:
                                    answer_list1.append(text)

                    num_list = [str(i + 1) for i in range(len(obj_list1))]  # 对应发言次数
                    obj_list = list(map(lambda x, y: x + y, obj_list1, num_list))  # 发言者
                    firstquestion.append('发表时间:' + time_list[0])
                    answer_list = [firstquestion] + list(map(lambda x, y: x + '  发表时间:' + y, answer_list1, time_list[1:]))
                    info_dict['context'] = [dict(zip(obj_list, answer_list))]
                    # info_list.append(info_dict)
                    post_list.append(info_dict)
                    completion_schedule += 1
                    time.sleep(0.2)
                except:
                    fail_num += 1
                    time.sleep(5)
                    continue
                
        with open(date_list[day_num]+'.json', 'w', encoding='utf-8') as f:
            json.dump(post_list, f, ensure_ascii=False, indent=4)
        
        day_num += 1




if __name__ == '__main__':

    date_list = CreateDate(start_date, end_date)
    print('CreateDate完成')

    url_list = GetUrl(date_list)
    print('GetUrl完成')
    
    detailpage_list = GetDetailpage(url_list)
    print('GetDetailpage完成')

        
    SaveHtml(detailpage_list, date_list)
    print('SaveHtml完成')

    AnalysisWeb(detailpage_list, date_list)
    print('AnalysisWeb完成')




















        
        
