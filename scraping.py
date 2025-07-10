# 画像をスクレイピングしながら画像URL一覧ファイル作成

#=============================================
# 検索ワード
#=============================================
a='ペンギン 親子 かわいい'
b='子猫 へそ天 いやし'
c='かき氷 フルーツ エモイ'

keywords = [a, b, c]

#=============================================
# 取得する画像数
#=============================================
kazu=5

import datetime
import os
import os.path as osp

#=============================================
# 呼び出す
#=============================================
from icrawler.builtin import BingImageCrawler
from icrawler.builtin import GoogleImageCrawler
from icrawler import ImageDownloader
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger 

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

#=============================================
# Topディレクトリ名は処理開始時間にする
#=============================================
t_delta = datetime.timedelta(hours=9)
JST=datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)
day_foi = format(now, '%Y%m%d9%H%M%S')

#=============================================
# ディレクトリ作成
#=============================================
foi = './image_'+str(day_foi)
os.makedirs(foi) # 

#=============================================
# 画像ファイルと画像を取得したURLのリストファイル名
#=============================================
save_name = '/リスト.csv'

#=============================================
# 画像を保存しながら、URLと画像名をリストファイルに書き込む
#=============================================

class URLDownloader(ImageDownloader):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import logging
        self.logger.setLevel(logging.CRITICAL)    
    
    def save_column(self, folname, filepath, file_url, output_csv_path=None):
        if output_csv_path is None:
            output_csv_path = foi + save_name
        with open(output_csv_path, 'a') as f:
            output_str = f'{folname}, {filepath}, {file_url}\n'
            f.write(output_str)

    def download(self, task, default_ext, timeout=5, max_retry=3, overwrite=False, **kwargs):
        file_url = task['file_url']
        task['success'] = False
        task['filename'] = None
        retry = max_retry

        while retry > 0 and not self.signal.get('reach_max_num'):
            try:
                if not overwrite:
                    with self.lock:
                        self.fetched_num += 1
                        filename = self.get_filename(task, default_ext)
                        if self.storage.exists(filename):
                            self.logger.info('skip downloading file %s', filename)
                            return
                        self.fetched_num -= 1

                response = self.session.get(file_url, timeout=timeout)

                if self.reach_max_num():
                    self.signal['reach_max_num'] = True
                    break

                if response.status_code != 200:
                    self.logger.error('Response status code %d, file %s',
                                      response.status_code, file_url)
                    break

                if not self.keep_file(task, response, **kwargs):
                    break

                with self.lock:
                    self.fetched_num += 1
                    filename = self.get_filename(task, default_ext)

                self.logger.info('image #%s\t%s', self.fetched_num, file_url)
                self.storage.write(filename, response.content)
                task['success'] = True
                task['filename'] = filename
                #folname = task.get('folname', 'unknown')
                self.save_column(folname, filename, file_url)
                break

            except Exception as e:
                self.logger.error('Exception caught when downloading file %s, error: %s, remaining retry times: %d',
                                  file_url, e, retry - 1)
            finally:
                retry -= 1


#=============================================
# 順番に検索します
#=============================================
crawler = BingImageCrawler(storage ={'root_dir' : foi})

for keyword in keywords:
    if keyword == a:
        moji = '1_'
    elif keyword == b:
        moji = '2_'
    elif keyword == c:
        moji = '3_'
    # 検索ワードの頭に連番。VBAで使用するので    
    folname = moji + keyword
    
    crawler = BingImageCrawler(downloader_cls=URLDownloader, storage={'root_dir': foi + '/'+ folname})   
    crawler.crawl(keyword = keyword, max_num = kazu) 

#=============================================
#　Topデレクトリとリストファイルを開く
#=============================================
os.startfile(os.path.realpath(foi))
os.startfile(os.path.realpath(foi) + save_name)
