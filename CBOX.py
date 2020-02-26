import re, os, requests, json, time
from multi_downloader import Downloader


class cntv():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
        }
        self.list_url = []
        self.vsid = ''
        self.api = 'http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid='
        self.dirname = ''

    def run(self, index_url):
        self.vsid = re.findall('&vsid=([0-9a-zA-Z]+)', index_url)[0]
        self.get_list('')

    def get_list(self, vsid):
        if vsid:
            self.vsid = vsid
        list_api = 'http://api.cntv.cn/video/videolistById?serviceId=cbox&vsid={}&cb='.format(self.vsid)
        try:
            res_list = requests.get(list_api, headers=self.headers)
            res = json.loads(res_list.text)['video']
            dirname = json.loads(res_list.text)['videoset']['0']['name']
        except Exception as e:
            print(e)
            print("Retrying!.....")
            self.get_list(vsid)
        if not os.path.exists('CNTV/{}'.format(dirname)):
            os.mkdir('CNTV/{}'.format(dirname))
        self.dirname = 'CNTV/{}/'.format(dirname)
        if res:
            for li in res:
                vname = li['t'].replace('/', '_')
                vname = vname.replace(" ", "")
                if os.path.exists(self.dirname + vname + '.mp4'):
                    print('File ' + self.dirname + vname + '.mp4' + ' exists!')
                    continue
                vid = li['vid']
                self.get_video(vname, vid)

    def get_video(self, vname, vid):
        req_url = self.api+vid
        try:
            vid_res = json.loads(requests.get(req_url, headers=self.headers).text)
        except Exception as e:
            print(e)
            print("Retrying!.....")
            self.get_video(vname, vid)
        # print(vid_res['video']['chapters4'])
        part = 2
        while 'chapters{}'.format(str(part)) in vid_res['video']:
            ch = vid_res['video']['chapters{}'.format(str(part))]
            part += 1
        c = 1
        f = open('{}.txt'.format(vname), 'w', encoding='UTF-8')
        tmp_file = []
        pwd = os.getcwd()
        for p in ch:
            print('开始下载 ', str(c)+'.mp4')
            vi = Downloader(p['url'], 4, self.dirname+str(c)+'.mp4')
            vi.run()
            t = pwd + '/' + self.dirname + str(c)+".mp4"
            tmp_file.append(t)
            c += 1
        for f1 in tmp_file:
            f.write('file ' + "'" + f1 + "'\n")
        f.close()
        # exit()
        self.merge(vname, tmp_file)

    def merge(self, vname, tmp_file):
        print(vname + ' 开始拼接')
        # cmd = 'ffmpeg -f concat -i concat.txt -c copy {}'.format(self.dirname + vname + '.mp4')
        pwd = os.getcwd()
        cmd = 'ffmpeg -f concat -safe 0 -i {}.txt -c copy {}'.format(vname, pwd + '/' + self.dirname + vname + '.mp4')
        tmp_file.append(vname + '.txt')
        print(cmd)
        os.system(cmd)
        print(vname + ' 拼接结束')
        for m in tmp_file:
            os.remove(m)




if __name__ == '__main__':
    if not os.path.exists('CNTV'):
        os.mkdir('CNTV')
    start = time.time()
    ch = input('1 or 2: ')
    st = cntv()
    if ch == '1':
        list_url = input("page_url: \n")
        st.run(list_url)
    else:
        st.get_list(input('VSID: \n'))


    
    print("全部下载完毕,耗时{}".format(str(time.time()-start)))
