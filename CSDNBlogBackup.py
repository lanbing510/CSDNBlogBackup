# -*- coding: utf-8 -*-
"""
Created on Thu Dec 03 15:06:27 2015

@author: 冰蓝
"""
import re
import os
import sys
import chilkat


head_string="""
<html>
<head>
  <title>Evernote Export</title>
  <basefont face="微软雅黑" size="2" />
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <meta name="exporter-version" content="Evernote Windows/276127; Windows/6.3.9600;"/>
  <style>
    body, td {
      font-family: 微软雅黑;
      font-size: 10pt;
    }
  </style>
</head>
<body>
"""
tail_string="""
</body>
</html>
"""

iter_count=0


def extractBlogLists(user_name='lanbing510',loop_times=1000):
    spider=chilkat.CkSpider()
    spider.Initialize("http://blog.csdn.net/lanbing510/")
    pattern=user_name+'/article/details'
    file_path='URList-'+user_name+'.txt'
    f=open(file_path,'w')
    url_count=0
    for i in range(0,loop_times):
        success = spider.CrawlNext()
        if (success == True):
            url=spider.lastUrl()
            m=re.search(pattern,url)
            if not m:
                continue
            url_count+=1
            print url_count
            print url
            title=spider.lastHtmlTitle().split(' -')[0]
            title=title.replace('/',' ') #标题中有特殊符号时的处理
            title=title.replace('_',' ')
            title=title.replace(':',' ')
            title=title.replace('*',' ')
            title=title.replace('?',' ')
            title=title.replace('|',' ')
            title=title.replace('#','sharp')
            f.write(url+","+title+'\n')
            #Print The HTML META title
            #print(spider.lastHtmlTitle().decode('gbk'))
        else:
            #Did we get an error or are there no more URLs to crawl?
            if (spider.get_NumUnspidered() == 0):
                print "No more URLs to spider"
            else:
                print spider.lastErrorText()
        #Sleep 1 second before spidering the next URL.
        spider.SleepMs(1000)
    f.close()
    #对生产的文件进行备份
    open('URList-'+user_name+'-backup.txt', "w").write(open(file_path, "r").read())


def downloadBlogLists(user_name='lanbing510'):
    global iter_count
    mht = chilkat.CkMht()
    success = mht.UnlockComponent("Anything for 30-day trial")
    if (success != True):
        print(mht.lastErrorText())
        sys.exit()

    file_path='URList-'+user_name+'.txt'
    f=open(file_path,'r')
    fout=open('Error.txt','w')
    
    for line in f.readlines():
        m=re.search('(http.+[0-9]{7,}),(.+)',line)
        url=m.group(1)
        title=m.group(2)
        mht_doc = mht.getMHT(url)
        if (mht_doc == None ):
            print(mht.lastErrorText())
            sys.exit()
            
        if not os.path.exists('CSDN-'+user_name):
            os.mkdir('CSDN-'+user_name)
        #Now extract the HTML and embedded objects:
        unpack_dir = "./CSDN-"+user_name+'/'
        html_filename = title+".html"
        parts_subdir = title
        success = mht.UnpackMHTString(mht_doc,unpack_dir,html_filename,parts_subdir)
        if (success != True):
            #print(mht.lastErrorText())
            fout.write(line)
        else:
            print("Successfully Downloaded "+title.decode('gbk'))
    f.close()
    fout.close()
    if iter_count>=5:
        print u"Some Blogs May Not Be Downloaded Successfully, Pleace Make Sure By Checking Error.txt And Index.html."
        os.remove(file_path)
        os.rename('URList-'+user_name+'-backup.txt',file_path)
    if iter_count<10 and os.path.getsize('Error.txt')>0:
        iter_count+=1
        print u"进行第 "+str(iter_count)+u" 次迭代下载"
        os.remove(file_path)
        os.rename('Error.txt',file_path)
        downloadBlogLists(user_name)


def generateIndex(user_name='lanbing510'):
    file_path='URList-'+user_name+'.txt'
    f=open(file_path,'r')
    fout=open('./CSDN-'+user_name+'/Index.html','w')
    fout.write(head_string)
    fout.write("""<h2>"""+user_name+"的博客"+"""</h2>\n""")
    fout.write("""<ol>\n""")
    for line in f.readlines():
        m=re.search('(http.+[0-9]{7,}),(.+)',line)
        title=m.group(2)
        title=title.decode('gbk').encode('utf-8')
        print title
        fout.write("""<li><a href=\""""+title+".html"+"""\">"""+title+"""</a></li>\n""")
    fout.write("""</ol>""")
    fout.write(tail_string)
    f.close()
    fout.close()


if __name__=='__main__':
    print "Please Input The Username Of Your CSDN Blog"
    user_name=raw_input()
    print "Start Extracting  Blog List..."
    extractBlogLists()
    print "Start Downloading Blog List..."
    downloadBlogLists()
    print "Start Generating Index.html..."
    generateIndex()
    print "Done"
