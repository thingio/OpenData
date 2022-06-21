
# encoding = 'utf-8'
from cmath import nan

from numpy import NaN
from opendatatools.common import RestAgent
import pandas as pd
from bs4 import BeautifulSoup as bs
import json
import os

class LabelmeAgent(RestAgent):

    def __init__(self, base_url):
        RestAgent.__init__(self)
        self.base_url = base_url.strip("/")
        self.page_size = 30 # labelme默认30，和浏览器正常访问保持一致，不容易被筛选出来
        self.token = ""

    def login(self, username, password):
        url = self.base_url + "/label_studio/user/login/"

        res =  self.session.get(url)
        token = bs(res.text, 'html.parser').select("#login-form > input[type=hidden]")[0]['value']

        param = {
            'csrfmiddlewaretoken': token,
            'email' : username,
            'password' : password,
        }
        print(param)
        res = self.session.post(url, data=param)
        if res.status_code == 200:
            soup = bs(res.text, 'html.parser')
            if soup.select("#main-content"):
                return True, "登录成功"
            elif soup.select("#login-form"):
                return False, "登录失败"
        return False, "未知失败"
        
    def list_projects(self):
        # TODO：目前只获取第一页，未来可以根据分页进行循环获取，加page/page_size主要还是模仿浏览器访问
        url = self.base_url + "/label_studio/api/projects?page=%d&page_size=%d" % (1, self.page_size)
        res =  self.session.get(url)
        if res.status_code != 200:
            print("获取项目失败：" + res.text)
            return None
        else:
            return pd.DataFrame(res.json()['results'])

    def list_views(self, project_id):
        url = self.base_url + "/label_studio/api/dm/views?project=%d" % project_id
        res =  self.session.get(url)
        if res.status_code != 200:
            print("获取视图失败：" + res.text)
            return None
        else:
            return pd.DataFrame(res.json())
                
    def list_images(self, project_id, view_id, page_end=0):
        # 加page/page_size主要还是模仿浏览器访问
        url = self.base_url + "/label_studio/api/dm/tasks?page=%d&page_size=%d&view=%d&project=%d" % (1, self.page_size, view_id, project_id)
        res =  self.session.get(url)
        if res.status_code != 200:
            print("获取视图失败：" + res.text)
            return None
        
        data = res.json()
        result = pd.DataFrame(data['tasks'])

        # 没有指定page_end，则加载所有图片元信息
        if page_end == 0:
            page_end = (data['total'] + 30) / 30

        # 从第2页开始下载，interaction=scroll也是为了模仿浏览器访问
        for page in range(2, page_end+1):
            url = self.base_url + "/label_studio/api/dm/tasks?page=%d&page_size=%d&view=%d&interaction=scroll&project=%d" % (page, self.page_size, view_id, project_id)
            res =  self.session.get(url)
            data = res.json()
            result = result.append(data['tasks'])
        
        return result
    
    def download_images(self, result, download_dir):
        result['download'] = 0
        dcol = list(result.columns).index('download')

        for i in range(len(result)):
            img_url = result.iloc[i]['data']['image']
            # TODO：加入随机间隔，模拟人下载
            f, s = self._download_file(img_url, download_dir)
            result.iloc[i, dcol] = 1

        return result

    def _download_file(self, url, destfolder):
        filename=url.replace(self.base_url, '').strip('/')
        fileuri = os.path.join(destfolder, filename)

        print("downloading %s to %s" % (url, fileuri))
        if os.path.exists(fileuri):
            return fileuri, False

        filedir = os.path.dirname(fileuri)
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(fileuri, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return fileuri, True