#モジュールをインポート
import tweepy
import requests
import datetime as dt
import pytz
import time
import datas
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
import os

#Twitter API
API_key = datas.API_key
API_key_Secret = datas.API_key_Secret
Access_Token = datas.Access_Token
Access_Token_Secret = datas.Access_Token_Secret
Bearer_Token = datas.Bearer_Token

#LINE Notify
TOKEN = datas.test_server
api_url = datas.api_url

#各変数の定義
search_word = 'from:@Genshin_7 -毎日チャレンジ！'
USER='@Genshin_7'
item_num = 1
user_id = 1070960596357509121
tweet = []
tweet.clear()
tweetcopy = []
tweetcopy.clear()
path = datas.path
pathtxt = datas.pathtxt
tweet_text_file=pathtxt+"\\"+'tweet_text.txt'
tweet_text_now_file=pathtxt+"\\"+'tweet_text_now.txt'
search_url = datas.search_url
query_params = {'query': '(from:Genshin_7 -ご参加ありがとうございます！ -毎日チャレンジ！)','expansions': 'attachments.media_keys', 'media.fields': 'url'}
number_of_trials=20
red='\033[31m'
reset = '\033[0m'
bold= '\033[1m'
sleep_time=15
item_list = ['3', '4', '5','6','7','8','9','10','11','12','13','14','15']
download_failed=0
status_code_is_not_200=0
network_not_found=0
number_of_executions_count=0

image_urls = []

#twitter API
auth = tweepy.OAuthHandler(API_key, API_key_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth)

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {Bearer_Token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def menu_time():
    t2=time.time()
    stop_time=t2-t1
    if stop_time>=86400:
        day=int(stop_time/60/60/24)
        if (((stop_time/60/60/24)-day)*60*60*24)>=3600:
            hour=int(((((stop_time/60/60/24)-day)*60*60*24)/60/60))
            if (((stop_time/60/60/24)-1)*60*60*24)>=60:
                minute=int(((((stop_time/60/60)-(hour+(day*24)))*60*60)/60))
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
            else:
                minute=0
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
        else:
            hour=0
            if (((stop_time/60/60/24)-1)*60*60*24)>=60:
                minute=int(((((stop_time/60/60)-(hour+(day*24)))*60*60)/60))
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
            else:
                minute=0
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
    elif stop_time>=3600:
        day=0
        hour=int((stop_time/60/60))
        if (((stop_time/60/60)-hour)*60)>=1:
            minute=int(((((stop_time/60/60)-(hour+(day*24)))*60*60)/60))
            second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
        else:
            minute=0
            second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
    elif stop_time>=60:
        day=0
        hour=0
        minute=int((stop_time/60))
        second=int(((stop_time/60)-minute)*60)
    elif stop_time<60:
        day=0
        hour=0
        minute=0
        second=int(stop_time)
    time_stop=tk.Toplevel()
    time_stop.geometry("300x30+500+300")
    time_stop.title("経過時間")
    times=tk.Label(time_stop,text=str(day)+"日"+str(hour)+"時間"+str(minute)+"分"+str(second)+"秒", font=("MSゴシック", "15", "bold"))
    times.pack()

def writeToLog(msg):
    numlines=int(log.index('end - 1 line').split('.')[0])
    log['state']='normal'
    #if numlines==24:
    # #log.delete(1.0, 2.0)
    if log.index('end-1c')!='1.0':
        log.insert('end','\n')
    log.insert('end',msg)
    log.see("end")
    log['state']='disabled'

def menu_update():
    def show_selected():
        #更新頻度の更新
        global sleep_time
        writeToLog(time_combobox.get())
        sleep_time=int(time_combobox.get())
        now_sleep['text']="現在の更新頻度　"+str(sleep_time)+"秒"

    sleeptime=tk.Toplevel()
    sleeptime.geometry("250x100+500+300")
    sleeptime.title("SleepTime")
    time_combobox = ttk.Combobox(master=sleeptime,values=item_list,height=5, width=7, justify="center",state="readonly")
    now_sleep = tk.Label(sleeptime,text="現在の更新頻度　"+str(sleep_time)+"秒", font=("MSゴシック", "15", "bold"))
    button = tk.Button(sleeptime,text="decision",command=show_selected)
    time_combobox.pack()
    button.pack()
    now_sleep.pack()
    pass

def announcement():
    def announcement_ok():
        send_announcement1=textBox1.get()
        send_announcement1=str(send_announcement1)
        send_announcement1=send_announcement1.replace('$', "\n")
        send_announcement="アナウンス"+"\n"+send_announcement1
        tokens={'Authorization': 'Bearer'+' '+TOKEN}
        send_data={'message': send_announcement}
        requests.post(api_url, headers=tokens, data=send_data)
        writeToLog("送信完了")
        writeToLog(send_announcement)
    announcements=tk.Toplevel()
    announcements.geometry("705x75+500+300")
    announcements.title("Announcements")
    announcement_label=tk.Label(announcements,text="送信テキスト(改行は $ を入力)", font=("MSゴシック", "13"))
    textBox1=tk.Entry(announcements,width=117)
    textBox1.place(x=0,y=20)
    button=tk.Button(announcements,text='送信',command=announcement_ok)
    button.place(x=670,y=50)
    announcement_label.pack()

#画像ダウンロード関数
def file_download(p,list_len_json,json_response,media_keys,list_len):
    global path,data_presence_or_absence,download_failed
    media_keys2=media_keys[p]
    media_keys2=str(media_keys2)
    media_keys2=media_keys2.lstrip("['")
    media_keys2=media_keys2.removesuffix("']")
    temp=("media_keys:",media_keys)
    writeToLog(temp)
    for h in range(list_len_json):
        json_respomse_check=json_response['includes']['media'][h]['media_key']
        writeToLog(json_respomse_check)
        if json_respomse_check == media_keys2:
            writeToLog("ok")
            json_response_data_media=json_response['includes']['media'][h]
            writeToLog(json_response_data_media)
            if json_response_data_media['type'] == 'photo':
                img_url = json_response_data_media['url']
                file_name=path+"\\"+str(p)+".jpg"
                #画像のダウンロード
                response = requests.get(img_url)
                image = response.content
                with open(file_name, "wb") as aaa:
                    aaa.write(image)
            elif json_response_data_media['type'] == 'video':
                #videoだったらスキップ
                print(red+bold+"This download key is video"+reset)
                writeToLog("This download key is video")
                data_presence_or_absence="no"
                list_len=list_len-1
            break
        elif json_respomse_check != media_keys2:
            writeToLog("Download key is not the same")
            data_presence_or_absence="no"
        else:
            writeToLog("*****Download failed*****")
            download_failed=download_failed+1
            try:
                download_failed_error['text']="download failed "+str(download_failed)+"回"
            except:
                pass
            data_presence_or_absence="no"
    return list_len

#検索エンドポイントに接続してJSONを取得する関数
def connect_to_endpoint(url, params):
    global status_code_is_not_200
    #APIを叩いて結果を取得
    response = requests.get(url, auth=bearer_oauth, params=params)
    #ステータスコードが200以外ならエラー処理
    if response.status_code != 200:
        writeToLog("*****status code is not 200*****")
        status_code_is_not_200=status_code_is_not_200+1
        try:
            status_code_is_not_200_error['text']="status code is not 200 "+str(status_code_is_not_200)+"回"
        except:
            pass
        raise Exception(response.status_code, response.text)

    #responseからJSONを取得してループを回し、URLを追加していく
    json_response = response.json()
    json_response_data1=(json_response['data'][0])
    writeToLog(json_response_data1)
    global tweets_data1
    tweets_data1=json_response_data1
    #画像があるかの判別
    keys="attachments" in json_response_data1
    writeToLog(keys)
    if keys==True:
        data_presence_or_absence="yes"
        media_keys=(json_response_data1['attachments']['media_keys'])
        list_len=(len(media_keys))
        list_len_json=(len(json_response['includes']['media']))
        #media_keysの取得
        list_len_json=list_len_json
        writeToLog(list_len_json)
        writeToLog("keys=yes")
        return data_presence_or_absence,json_response_data1,list_len,list_len_json,json_response,media_keys
    elif keys==False:
        data_presence_or_absence="no"
        list_len_json=0
        media_keys=False
        writeToLog("media_keys=None")
        list_len=0
        return data_presence_or_absence,json_response_data1,list_len,list_len_json,json_response,media_keys
    else:
        writeToLog("*****Media_key is not the same*****")

#日本時間に変更する関数
def change_time_JST(u_time):
    #イギリスのtimezoneを設定するために再定義する
    utc_time = dt.datetime(u_time.year, u_time.month,u_time.day, \
    u_time.hour,u_time.minute,u_time.second, tzinfo=dt.timezone.utc)
    #タイムゾーンを日本時刻に変換
    jst_time = utc_time.astimezone(pytz.timezone("Asia/Tokyo"))
    # 文字列で返す
    str_time = jst_time.strftime("%Y-%m-%d_%H:%M:%S")
    return str_time
#抽出したデータから必要な情報を取り出す

#main関数
def main():
    time.sleep(1)
    global number_of_trials,network_not_found,number_of_executions_count
    while True:
        number_of_executions_count=number_of_executions_count+1
        try:
            number_of_executions['text']="number of executions "+str(number_of_executions_count)+"回"
        except:
            pass
        try:
            #tweetの取得
            data_presence_or_absence,json_response_data1,list_len,list_len_json,json_response,media_keys = connect_to_endpoint(search_url, query_params)
            writeToLog(data_presence_or_absence)
            writeToLog(dt.datetime.now())
            # Response クラスの中身は https://docs.tweepy.org/en/stable/response.html#tweepy.Response
            #検出されたtweetをtxtに入力
            f = open(tweet_text_now_file, 'w', encoding='utf-8')
            f.write(json_response_data1['text'])
            f.close()
            with open(tweet_text_now_file,'r',encoding="utf-8_sig") as f:
                file_read = f.read()
            if os.path.exists(tweet_text_file)==True:
                with open(tweet_text_file,'r',encoding="utf-8_sig") as f:
                    file_read1 = f.read()
            elif os.path.exists(tweet_text_file)==False:
                f=open(tweet_text_file,'w',encoding="utf-8")
                f.write("")
                f.close()
                with open(tweet_text_file,'r',encoding="utf-8_sig") as f:
                    file_read1 = f.read()
            #print(file_read1)
            #print(file_read1)
            #txtの内容の確認
            if file_read == file_read1:
                writeToLog("file:True")
            elif file_read != file_read1:
                number_of_trials=0
                writeToLog("file:False")
                #tweet時刻の取得
                tweets = tweepy.Cursor(api.search_tweets,q=search_word,lang='ja').items(item_num)
                #取得したツイートを一つずつ取り出して必要な情報をtweet_dataに格納する
                tweets_data = []
                for tweets2 in tweets:
                    #ツイート時刻とユーザのアカウント作成時刻を日本時刻にする
                    tweet_time = change_time_JST(tweets2.created_at)
                if list_len==1:
                    for p in range(1):
                        list_len=file_download(p,list_len_json,json_response,media_keys,list_len)
                elif list_len==2:
                    for p in range(2):
                        list_len=file_download(p,list_len_json,json_response,media_keys,list_len)
                elif list_len==3:
                    for p in range(3):
                        list_len=file_download(p,list_len_json,json_response,media_keys,list_len)
                elif list_len==4:
                    for p in range(4):
                        list_len=file_download(p,list_len_json,json_response,media_keys,list_len)
                writeToLog("===================")
                #print("Tweet id:", json_response_data1['id'])
                temp=("Tweet text:", json_response_data1['text'])
                writeToLog(temp)
                temp=("Tweet time:",tweet_time)
                writeToLog(temp)
                f = open(tweet_text_file, 'w', encoding='utf-8')
                f.write(json_response_data1['text'])
                f.close()
                #LINE Notifyに送信する準備
                tweet_text=json_response_data1['text']
                send_contents0 = f'@Genshin_7の最新ツイートのお知らせ\nツイートされた時刻 {tweet_time}\n{tweet_text}\n'
                send_contents = f'@Genshin_7の最新ツイートのお知らせ\nツイートされた時刻 {tweet_time}\n{tweet_text}\n1枚目\n'
                TOKEN_dic = {'Authorization': 'Bearer'+' '+TOKEN}
                send_dic0 = {'message': send_contents0}
                send_dic={'message': send_contents}
                send_contents1 = f'2枚目'
                send_contents2 = f'3枚目'
                send_contents3 = f'4枚目'
                send_dic1= {'message':send_contents1}
                send_dic2= {'message':send_contents2}
                send_dic3= {'message':send_contents3}
                image_file=path+"\\"+'0.jpg'
                image_file1=path+"\\"+'1.jpg'
                image_file2=path+"\\"+'2.jpg'
                image_file3=path+"\\"+'3.jpg'
                #画像数の判別
                if data_presence_or_absence=="yes":
                    if list_len==1:
                        binary=open(image_file,mode='rb')
                        image_dic = {'imageFile':binary}
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                        writeToLog("送信完了")
                    elif list_len==2:
                        binary=open(image_file,mode='rb')
                        image_dic = {'imageFile':binary}
                        binary1=open(image_file1,mode='rb')
                        image_dic1={'imageFile':binary1}
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                        requests.post(api_url,headers=TOKEN_dic,data=send_dic1,files=image_dic1)
                        writeToLog("送信完了")
                    elif list_len==3:
                        print("3")
                        binary=open(image_file,mode='rb')
                        image_dic = {'imageFile':binary}
                        binary1=open(image_file1,mode='rb')
                        image_dic1={'imageFile':binary1}
                        binary2=open(image_file2,mode='rb')
                        image_dic2={'imageFile':binary2}
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic1,files=image_dic1)
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic2,files=image_dic2)
                        writeToLog("送信完了")
                    elif list_len==4:
                        binary=open(image_file,mode='rb')
                        image_dic = {'imageFile':binary}
                        binary1=open(image_file1,mode='rb')
                        image_dic1={'imageFile':binary1}
                        binary2=open(image_file2,mode='rb')
                        image_dic2={'imageFile':binary2}
                        binary3=open(image_file3,mode='rb')
                        image_dic3={'imageFile':binary3}
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                        requests.post(api_url,headers=TOKEN_dic,data=send_dic1,files=image_dic1)
                        requests.post(api_url,headers=TOKEN_dic,data=send_dic2,files=image_dic2)
                        requests.post(api_url,headers=TOKEN_dic,data=send_dic3,files=image_dic3)
                        writeToLog("送信完了")
                    else:
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic0)
                        writeToLog("送信完了")
                elif data_presence_or_absence=="no":
                    requests.post(api_url, headers=TOKEN_dic, data=send_dic0)
                    writeToLog("送信完了")
                files_error=False
            #待機秒数
            if number_of_trials<=11:
                time.sleep(3)
                number_of_trials=number_of_trials+1
            else:
                time.sleep(sleep_time)
        #networkエラーの処理
        except Exception as e:
            writeToLog("*****Error*****")
            writeToLog("*****network not found*****")
            writeToLog(e)
            network_not_found=network_not_found+1
            try:
                network_not_found_error['text']="network not found "+str(network_not_found)+"回"
            except:
                pass
            time.sleep(sleep_time)
            pass


if __name__=='__main__':
    t1=time.time()
    try:
        thread_1=threading.Thread(target=main)
        thread_1.setDaemon(True)
        #関数の起動
        thread_1.start()
    except:
        pass
    try:
        #TkinterのGUIの表示
        command=tk.Tk()
        command.geometry("1000x580+700+0")
        command.title("Command")
        error=tk.Toplevel()
        error.geometry("300x100+500+400")
        error.title("Errors")
        count=tk.Toplevel()
        count.geometry("290x30+500+500")
        count.title("Count")
        download_failed_error = tk.Label(error,text="download failed "+str(download_failed)+"回", font=("MSゴシック", "15", "bold"))
        status_code_is_not_200_error = tk.Label(error,text="status code is not 200 "+str(status_code_is_not_200)+"回", font=("MSゴシック", "15", "bold"))
        network_not_found_error = tk.Label(error,text="network not found "+str(network_not_found)+"回", font=("MSゴシック", "15", "bold"))
        download_failed_error.pack()
        status_code_is_not_200_error.pack()
        network_not_found_error.pack()
        number_of_executions=tk.Label(count,text="number of executions "+str(number_of_executions_count)+"回", font=("MSゴシック", "15", "bold"))
        number_of_executions.pack()
        frame1=ttk.Frame(command,padding=10)
        frame1.grid()
        log=Text(command,state='disabled',borderwidth=6,width=136,height=43,wrap='none',padx=10,pady=10)
        ys= tk.Scrollbar(command,orient ='vertical',command=log.yview)
        log['yscrollcommand']=ys.set
        log.insert('end',"Lorem ipsum...\n...\n...")
        log.see("end")
        log.grid(row=4,column=0)
        ys.grid(column=1,row=4,sticky='ns')
        men=tk.Menu(command)
        command.config(menu=men)
        menu=tk.Menu(command)
        men.add_cascade(label="メニュー",menu=menu)
        menu.add_command(label="更新頻度変更",command=menu_update)
        menu.add_command(label="稼働時間",command=menu_time)
        menu.add_command(label="アナウンス",command=announcement)
        menu.add_separator()
        menu.add_command(label="Exit",command=lambda:command.destroy())
        command.mainloop()
    except:
        pass
