import requests
import os
import re
from urllib import parse
from threading import Thread
imgtype=['.gif','.jpg','.jpeg','.png','.webp']
skiphref=['.css']
existurl=[]
existimg=[]
currentdepth=1
nextdepthhref=[]
layerover=True
def main(url,depth,path):
    global nextdepthhref
    global layerover
    global currentdepth
    print('currentdepth:',currentdepth)
    try:
        r =requests.get(url)
        text=r.content.decode('utf-8','ignore')
    except:
        print('WOW, GG')
        return
    hrefs=re.findall('href=".*?"',text)
    print('url:',url)
    for href in hrefs:
        href=href[6:-1]
        if href[:1]=='/':
            href = parse.urljoin(url,href)
            
#                 while href[0]=='/':
#                     href=href[1:]
#                 try:
#                     href='http://'+href
#                 except:
#                     href='https://'+href
        if href[:4]!='http':
            continue
        skip=False
        print('href:',href)
        for i in imgtype:
            if i in href:
                nextdepthhref.append(href)
                p=Thread(target=imagecrawler(href,path),args=('In thread',))
                p.start()
                p.join()
                skip=True
                break
        if skip:
            print('skip')
            continue
        for i in skiphref:
            if i in href:
                skip=True
                break
        if skip:
            print('skip')
            continue
        if href in existurl:
            print('href has browsed:',href)
            continue
        else:
            path=path.strip()
            path=pathprocess(href)
            if path!='':
                nextdepthhref.append(href)
                existurl.append(href)
                p=Thread(target=imagecrawler(href,path),args=('In thread',))
                p.start() 
                p.join()
    if layerover==True:
        if not nextdepthhref:
            print('No more pages.')
            return
        if currentdepth<depth:
            currentdepth+=1
            currentdepthhref=nextdepthhref.copy()
            print(currentdepthhref)
            nextdepthhref=[]
            for href in currentdepthhref:
                if currentdepthhref[-1]==href:
                    layerover=True
                else:
                    layerover=False
                p=Thread(target=main(href,depth,path),args=('In thread',))
                p.start()
                p.join()
            
    
def imagecrawler(url,path):
    try:
        r =requests.get(url)
        text=r.content.decode('utf-8','ignore')
    except:
        print('request failed')
        return
    imgs=re.findall(r'<img.*?>',text)
    for img in imgs:
        exist=False
        try:
            imgpath=re.search(r"src=.*?[> ]",img).group()
        except:
            continue
        if imgpath[4]=='"':
            try:
                imgpath=re.search(r'".*?"',img).group()
                imgpath=imgpath[1:-1]
            except:
                continue
        elif imgpath[4]=="'":
            try:
                imgpath=re.search(r"'.*?'",img).group()
                imgpath=imgpath[1:-1]
            except:
                continue
        else:
            imgpath=imgpath[4:-1]
        if imgpath not in existimg:
            
            imgname=imgpath.split('/')[-1].lower()
            for element in imgtype:
                if element in imgname:
                    suffix=element
                    index=imgname.find(suffix)
                    imgname=imgname[:index]+element
                    exist=True
            if not exist:
                continue
            if imgpath[:1]=='/':
                imgpath = parse.urljoin(url,imgpath)
                try:
                    content=requests.get(imgpath,verify=False)
                except:
                    continue
#                 while imgpath[0]=='/':
#                     imgpath=imgpath[1:]
#                 try:
#                     imgpath='http://'+imgpath
#                     content = requests.get(imgpath,verify=False)
#                 except:
#                     imgpath='https://'+imgpath
#                     try:
#                         content = requests.get(imgpath,verify=False)
#                     except:
#                         print(2)
#                         continue
            elif imgpath[:1]=='.':
                try:
                    page_url =re.search('<base.*?>',text).group()
                    page_url=re.search('href=".*?"',page_url).group()
                except:
                    continue
                
                page_url=page_url[6:-1]
                new_url = imgpath
                imgpath = parse.urljoin(page_url, new_url)
                try:
                    content=requests.get(imgpath,verify=False)
                except:
                    continue
            else:
                try:
                    content=requests.get(imgpath,verify=False)
                except:
                    print(5)
                    continue
            print('imgpath:',imgpath)
            existimg.append(imgpath)
            with open(os.path.join(path,imgname),'wb') as f:
                f.write(content.content)
                print('have save')
        else:
            continue

def pathprocess(url):
    urlcopy=url
    if 'http://' in urlcopy:
        urlcopy=urlcopy.replace('http://','')
    elif 'https://' in urlcopy:
        urlcopy=urlcopy.replace('https://','')
    urlcopy = urlcopy if '/' in urlcopy else urlcopy + '/'
    urlcopy=re.sub(r'[\*:?"<>|]','',urlcopy)
    if not os.path.exists(r'/'+urlcopy):
        try:
            os.makedirs(r'/'+urlcopy)
        except:
            return ''
    else:
        print('dir has existed')
    return r'/'+urlcopy
        
if __name__ == '__main__':
    #https://sports.163.com/19/1112/09/ETP9JCCO00058780.html
    #https://www.baidu.com
    #http://www.feimax.com/images
    entercorrect=True
    while entercorrect:
        url=input("Please enter the URL (URL should include http(s)):")      
        if 'http://' in url or 'https://' in url:
            entercorrect=False
    path=pathprocess(url)
    if path!='':
        depth=input('Please enter the depth (if you enter character, it will default to 5):')
        try:
            depth=int(depth)
        except:
            depth=5
        print('currentdepth: 0')
        print(url)
        existurl.append(url)
        imagecrawler(url,path)
        main(url,depth,path)
        print(existimg)