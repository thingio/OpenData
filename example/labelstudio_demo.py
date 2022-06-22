from opendatatools import labelstudio

if __name__ == '__main__':

    # 地址/端口，用户名/密码
    agent = labelstudio.LabelStudioAgent("http://server:port")
    print(agent.login('email', 'password'))

    # 查询所有项目，获取project_id
    print(agent.list_projects())

    # 项目有多个视图，选择一个视图view_id
    print(agent.list_views(project_id=16))

    # 指定project_id/view_id；可选参数page_end代表下载数据最大页数，labelstudio接口对数据进行分页，填0或者不填会循环下载所有数据，可能耗时较长
    df = agent.list_images(project_id=16, view_id=97, page_end=3)
    print(df)
    # 防止反复访问接口，可以先保存
    df.to_csv('/tmp/myimage.csv',index=False)

    # 下载所有图片到指定目录，如果指定目录下存在图片文件，则跳过下载但依旧认为下载成功
    df = agent.download_images(df, '/tmp/myimage')
    print("未下载成功：", df[df.download != 1])