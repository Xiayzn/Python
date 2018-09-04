#!/usr/bin/python
#coding:utf-8
'''
爬取西安工业大学就业信息网站上的招聘信息
'''
#urllib2 提供url操作方法
import urllib2
#提供json数据格式的操作方法 loads和dumps
import json
#提供mysql数据库的连接和操作方法
import MySQLdb
#base64编码格式 用于消除html响应内容里可能存在的字符串
import base64
#sys Python标准库 提供一系列的系统操作方法
import sys
#爬虫库 提供html解析方法
from bs4 import BeautifulSoup
reload(sys)
#设置此文件全部内容使用utf-8格式
sys.setdefaultencoding("utf-8")

#根据url获取服务器端响应内容
def OpenPage(url):
    #构造请求头
    Myheaders = {}
    #构造request请求
    req = urllib2.Request(url,headers=Myheaders)
    #激活请求，获取服务器端响应
    f = urllib2.urlopen(req)
    #用read()方法读取响应内容
    data = f.read()
    #发现网页内容就是utf-8，无需编码解码操作
    return data

def Test1():
    #url = "http://jy.51uns.com:8022/Pro_StudentEmploy/StudentJobFair/Zhaoping.aspx?WorkType=0"
    url = "http://jy.51uns.com:8022/Frame/Data/jdp.ashx?rnd=1534417983749&fn=GetZhaopinList&StartDate=2000-01-01&SearchKey=&InfoType=-1&CompanyAttr=&CompanyType=&Area=&City=&CompanyProvice=&Post=&Zhuanye=&XLkey=&Age=&start=0&limit=30&DateType=999&InfoState=1&WorkType=0&CompanyKey="
    print OpenPage(url)

#从主页上获取招聘信息id
def ParseMainPage(page):
    #分析数据 提取指定内容(id)
    #解压json数据，转换成python支持的数据类型 dict
    data = json.loads(page)
    IdList = []
    #data[rows] 取到招聘信息的列表
    for item in data["rows"]:
        IdList.append(item["Id"])
    
    return IdList
    #return [item["Id"] for item in data["rows"]]

def Test2():
    url = "http://jy.51uns.com:8022/Frame/Data/jdp.ashx?rnd=1534417983749&fn=GetZhaopinList&StartDate=2000-01-01&SearchKey=&InfoType=-1&CompanyAttr=&CompanyType=&Area=&City=&CompanyProvice=&Post=&Zhuanye=&XLkey=&Age=&start=0&limit=30&DateType=999&InfoState=1&WorkType=0&CompanyKey="
    page = OpenPage(url)
    print ParseMainPage(page)

#解析招聘信息详情页
def ParseDetailPage(page):
    #解析json格式数据
    JsonData = json.loads(page)
    #获取到data字典
    Data = JsonData["Data"]
    #取id
    Id = Data["Id"] 
    #取公司名称
    Title = Data["CompanyTitle"]
    #薪资待遇
    Price = Data["WorkPrice"]
    #招聘岗位
    Position = Data["WorkPositon"]
    #招聘详情
    soup = BeautifulSoup(Data["EmployContent"],"html.parser")
    #提取全部的p标签
    GetP = soup.find_all("p")
    ContentList = []
    for item in GetP:
       ContentList.append(item.get_text())
    #获取到了一个内容列表
    Content = "\n".join(ContentList)
    
    return Id,Title,Price,Position,Content

def Test3():
    url = "http://jy.51uns.com:8022/Frame/Data/jdp.ashx?rnd=1534420814095&fn=GetOneZhaopin&JobId=b7986ae4f3f94e0bb79677c68b871e30&StartDate=2000-01-01"
    page =  OpenPage(url)
    print ParseDetailPage(page)

#把数据写入数据库里
#数据库建表 navicat
# id,company,price,position,content text
def WriteDataToMySQL(data):
    #构造mysql链接
    #import base64
    #host localhost 127.0.0.1 
    #user mysql数据库的登录用户名
    #passwd mysql数据库的登录密码
    #db 我们要连接的数据库名
    #charset 编码格式
    db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="zxy970922",db="ClawerSchool",charset="utf8")
    #mysqldb 构造的python可以操作的数据库游标
    
    cursor = db.cursor()
    content = base64.b64encode(data[4])
    sql = "insert into Job values('%s','%s','%s','%s','%s')" % (data[0],data[1],data[2],data[3],content)
    #执行sql语句
    
    cursor.execute(sql)
    try:
        #提交
        db.commit()
        #提交成功 提交失败
    except Exception,e:
        #回滚操作 用于提交失败时,保证这次提交不对数据库产生影响
        db.rollback()
        print e
    db.close()

    return "Success"

def Test4():
    data = ("10086","杭州公司","8-15k","小明","性格开朗")
    WriteDataToMySQL(data)

if __name__ == "__main__":
    url = "http://jy.51uns.com:8022/Frame/Data/jdp.ashx?rnd=1534423698846&fn=GetZhaopinList&StartDate=2000-01-01&SearchKey=&InfoType=-1&CompanyAttr=&CompanyType=&Area=&City=&CompanyProvice=&Post=&Zhuanye=&XLkey=&Age=&start=0&limit=825&DateType=999&InfoState=1&WorkType=0&CompanyKey="
    #获取到主页招聘信息的数据响应
    page = OpenPage(url)
    #解析主页服务器端响应，获取各个招聘信息的id
    IdList = ParseMainPage(page)
    #构造招聘信息详情页的数据获取公共前缀
    prefix = "http://jy.51uns.com:8022/Frame/Data/jdp.ashx?rnd=1534423818472&fn=GetOneZhaopin&StartDate=2000-01-01&JobId="
    print "Clone Begin"
    #遍历id列表,循环获取每一个招聘信息的内容
    for item in IdList:
        #用公共前缀和id构造数据获取url
        DetailUrl = prefix + item
        #访问url获取服务器端数据响应
        Detail = OpenPage(DetailUrl)
        #(id,公司名,薪资,岗位,招聘详情)
        #解析数据，得到招聘信息相关内容
        data = ParseDetailPage(Detail)
        print "Clone:"+data[1]
        #写入数据库
        WriteDataToMySQL(data)
    print "Clone done"
