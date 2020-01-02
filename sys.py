#!/usr/bin/python
import requests
import datetime
import subprocess
import os
from bs4 import BeautifulSoup
import pymysql

cur = datetime.datetime.now()
year = str(cur.year)
month = str(cur.month)
day = str(cur.day)
time = str(cur.hour)
path = year + month + day + "_" + time
cloth_dict = {'coat':'wc_1', 'padding':'wc_2', 'jackets':'wc_3', 'longpants':'wc_4', 'shortpants':'wc_5', 'cardigan':'wc_6','longsleeve':'wc_7','shortsleeve':'wc_8','knit':'wc_9','sweatshirts':'wc_10','sleeveless':'wc_11'}

headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
url = 'https://www.google.com/search?ei=Su-zXZqmMsCLr7wPxLuLKA&q=%EC%84%9C%EC%9A%B8%EB%82%A0%EC%94%A8&oq=%EC%84%9C%EC%9A%B8%EB%82%A0%EC%94%A8&gs_l=psy-ab.3..0i131i67j0l5j0i67j0j0i67j0.25579.27206..27676...1.4..2.430.1977.0j8j2j0j1......0....1..gws-wiz.......0i71j0i10j0i131j0i7i30j38.OaEgK4bGiw4&ved=0ahUKEwia872wrbnlAhXAxYsBHcTdAgUQ4dUDCAs&uact=5'
res = requests.get(url, headers=headers)
text = res.text
soup = BeautifulSoup(text,'html.parser')
temperature = int(soup.find('span', class_='wob_t').text)
wind_speed = int(soup.find('span', id='wob_ws').text.split('m')[0])


print(datetime.datetime.now())
print("temperature:", temperature, " windspeed:", wind_speed)


def get_insta_img():
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)
    try:
        subprocess.call(["instalooter", "hashtag", "데일리룩코디", path], timeout = 20)
    except:
        print("time expired")


def run_inception():
    from subprocess import check_output
    from os import listdir
    from os.path import isfile, join
    clothes=[]
    images = [f for f in listdir(path) if isfile(join(path, f))]

    for img in images:
        img = str(img).strip()
        out = check_output(["ls", "-alh", img], cwd=path)
        img_month = out.split()[5].decode('utf-8')
        img_day = out.split()[6].decode('utf-8')
        img_hour = out.split()[7].decode('utf-8').split(":")[0]
        if month == img_month and day == img_day and img_hour == time:
            try:
                img_path = path + "/" + str(img)
                res = check_output(["python3","label_image.py",img_path], stderr=None).decode('utf-8')
                temp_cloth = res.split(":")[0]
                predict_score = res.split(":")[2].split()[0]
                if float(predict_score) >= 0.6 :
                    clothes.append(temp_cloth)
                else:
                    continue
            except Exception as e:
                print(e)
    print(clothes)
    return clothes


def fill_database():
    conn = pymysql.connect(host='wcmain.c7dilglxsf9a.ap-northeast-2.rds.amazonaws.com', user='wcmain', password='wcmain1234',
                           db='wcmain', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    try:
        sql = "select * from wc where wc_avg=%s and wc_wind=%s"
        curs.execute(sql, (temperature, wind_speed))
        rows = curs.fetchall()

        if not rows:
            add_key = "insert into wc(wc_avg, wc_wind) values (%s, %s)"
            curs.execute(add_key, (temperature, wind_speed))

        cloth_keys = run_inception()
        for key in cloth_keys:
            selected_cloth = cloth_dict[key]
            sql2 = "UPDATE wc SET " + selected_cloth + " = " + selected_cloth + "+1 WHERE wc_avg = %s and wc_wind= %s"
            curs.execute(sql2, (temperature, wind_speed))
        conn.commit()

    except Exception as e:
        print(e)
    finally:
        conn.close()


if __name__ == '__main__':

    print('--------------get_insta_img start--------------')
    get_insta_img()
    print('--------------get_insta_img end--------------')


    print('--------------run Inception and fill [wc] table start--------------')
    fill_database()
    print('--------------run Inception and fill [wc] table--------------')

    # delete 시간 폴더
