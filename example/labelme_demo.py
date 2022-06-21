from opendatatools import labelme

if __name__ == '__main__':

    # 地址/端口，用户名/密码
    agent = labelme.LabelmeAgent("http://address:port")
    print(agent.login('email', 'password'))

    # 查询所有项目，获取project_id
    print(agent.list_projects())

    # 项目有多个视图，选择一个视图view_id
    print(agent.list_views(project_id=16))

    # 指定project_id/view_id；可选参数page_end，应对接口对数据进行分页了，填0或者不填会下载所有数据
    df = agent.list_images(project_id=16, view_id=97, page_end=3)
    print(df)

    # 下载所有图片到指定目录，如果指定目录下存在图片文件，则跳过下载但依旧认为下载成功
    df = agent.download_images(df, '/tmp/myimage')
    print("未下载成功：", df[df.download != 1])
