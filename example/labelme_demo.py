from opendatatools import labelme

if __name__ == '__main__':
    agent = labelme.LabelmeAgent("http://labelme:address")
    print(agent.login('email', 'password'))
    print(agent.list_projects())
    print(agent.list_views(16))
    r = agent.list_images(16,97,3)
    print(r)
    print(agent.download_images(r, '/tmp/myimage'))

