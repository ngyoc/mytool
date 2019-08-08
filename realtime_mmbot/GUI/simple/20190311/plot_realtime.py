import copy
import datetime
import json
import os
import pprint
import sys
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import traceback
from functools import reduce
from operator import add
from queue import Queue
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pybitflyer
import websocket
from dateutil.parser import parse
from PIL import Image, ImageTk


class accum_trade_volume:

    def __init__(self, path_BASE, API_KEY='', API_SECRET='', flag_realtrade=False):
        #
        self.path_BASE = path_BASE

        self.flag_realtrade = flag_realtrade

        # config
        self.path_config = path_BASE + 'config/bitflyer_params.json'
        self.load_json()

        self.deltatime = self.bitflyer_params['deltaTime']

        [os.makedirs(self.path_BASE + i) for i in ['', 'log/', 'Error/', 'header/'] if not os.path.exists(os.path.join(self.path_BASE, i))]

        # header出力
        self.save_header()

        # self.API_KEY    = API_KEY
        # self.API_SECRET = API_SECRET

        # テスト環境ではpybitflyerにAPIキーをわたさない
        if self.flag_realtrade:
            # self.api = pybitflyer.API(api_key=self.API_KEY, api_secret=self.API_SECRET)
            print('注意 flag_realtrade = 1')
        else:
            self.api = pybitflyer.API()

        # 初期化
        self.volume     = {'buy': 0,
                           'sell': 0,
                           'time': datetime.datetime.now()}
        self.executions = {'BUY': {},
                           'SELL': {}}

        # 取引可能ステータス
        self.ok_status =  ['NORMAL','BUSY','VERY BUSY']

        # 取引通貨ペア
        self.PRODUCT = 'FX_BTC_JPY'

        # websocket通信準備
        self.init_websocket()

        # main
        self.flag_mainloop = True
        self.flag_trademain = True
        self.save_flag     = True

        # 実行開始時刻
        self.start_datetime = '{0:%Y%m%d_%H%M}'.format(datetime.datetime.now())

        self.tick_ask = 0.0
        self.tick_bid = 0.0
        self.tick_mid = 0.0

        self.pnl = 0
        self.position = 0

        self.interval = 1

        self.q = Queue()

        self.trade_amount = 0.1

        self.max_position = 25

        # entry exit条件を設定
        self.def_LS_EnEx(LS_En=1, LS_Ex=1)


        # グラフ初期化機能で使用
        self.flag_plot = True


    def init_websocket(self):
        '''
        websocket通信の準備
        '''

        try:
            print('WebSocket Connection Ready')

            # デバッグ表示はオフ
            websocket.enableTrace(False)

            self.ws = websocket.WebSocketApp('wss://ws.lightstream.bitflyer.com/json-rpc',
                                             on_message = self.on_message,
                                             on_error   = self.on_error,
                                             on_close   = self.on_close)


            self.ws.on_open = self.on_open

        except Exception as e:
            print(e.args)
            if self.ws in locals():
                self.ws.close


    def on_message(self, ws, message):
        '''
        受信した約定履歴からデータを作成
        '''
        # res = 受信した約定データ
        self.res = json.loads(message)

        # print(self.res)

        # (1) store 'side' and 'size' of 'executions'
        if 'method' in self.res and self.res['method'] == 'channelMessage':
            # 受信したデータがチャンネルからのメッセージだった時

            if self.res['params']['channel'] == 'lightning_ticker_FX_BTC_JPY':
                self.tick_ask = self.res['params']['message']['best_ask']
                self.tick_bid = self.res['params']['message']['best_bid']
                self.tick_mid = (self.tick_ask + self.tick_bid) / 2.0

            elif self.res['params']['channel'] == 'lightning_executions_FX_BTC_JPY':
                # test
                executions_onetime = {'BUY': {},   #
                                      'SELL': {}}  #

                for order in self.res['params']['message']:
                    # order には 受信したメッセージをひとつずつ格納

                    # 約定時刻をタイムスタンプに変換
                    timestamp = parse(order['exec_date']).timestamp()

                    try:

                        # orderのtimestampが既に格納されていたら
                        if timestamp in self.executions[order['side']]:
                            # 数量をまとめる
                            self.executions[order['side']][timestamp] += order['size']

                            # onetimeにデータ追加する処理を分ける
                            # executions_onetime[order['side']][timestamp]['size'] += order['size'] #

                        else:
                            # 新しいtimestampだったら新規追加する
                            self.executions[order['side']][timestamp] = order['size']


                        if timestamp in executions_onetime[order['side']]:
                            executions_onetime[order['side']][timestamp]['size'] += order['size'] #

                        else:
                            executions_onetime[order['side']][timestamp]           = {} #
                            executions_onetime[order['side']][timestamp]['size']   = order['size'] #
                            executions_onetime[order['side']][timestamp]['price']  = order['price'] #



                    except Exception as e:
                        # print('--- ERROR ---')
                        # エラーログ出力
                        with open(self.path_BASE + '/Error/Error_log_on_message_{0:%Y%m%d_%H%M%S}.dsv'.format(datetime.datetime.now()), mode=('a')) as f:
                            # np.savetxt(f, e, delimiter='\t', fmt='%s')
                            traceback.print_exc(file=f)

                        # traceback.print_exc()
                        # pprint.pprint(self.executions)
                        # pprint.pprint(executions_onetime)
                        # print(order)
                        # print('-------------')

                executions_arr = np.zeros((0, 4))

                for i_BS in executions_onetime.keys():
                    for i_timestamp in executions_onetime[i_BS].keys():
                        # print(BS, timestamp)
                        exec_arr = np.array(['{0:%Y/%m/%d %H:%M:%S.%f}'.format(datetime.datetime.fromtimestamp(i_timestamp)),
                                            i_BS,
                                            executions_onetime[i_BS][i_timestamp]['price'],
                                            executions_onetime[i_BS][i_timestamp]['size']])

                        executions_arr = np.vstack((executions_arr, exec_arr))

                with open(self.path_BASE + '/log/executions_comp_{{{0:}}}_{1:%Y%m%d}.dsv'.format(self.start_datetime, datetime.datetime.now()), mode=('ab')) as f:
                    np.savetxt(f, executions_arr, delimiter='\t', fmt='%s')

            # bitflyer_params['deltaTime']秒以前のデータを削除する (初期値:15秒)
            # 直近15秒の約定履歴のみを保管する self.deltatime
            self.executions['BUY']  = dict(filter(lambda x: datetime.datetime.now().timestamp() - x[0] < self.deltatime, self.executions['BUY'].items()))
            self.executions['SELL'] = dict(filter(lambda x: datetime.datetime.now().timestamp() - x[0] < self.deltatime, self.executions['SELL'].items()))

            # BUYSELL それぞれの数量の合計をvolumeに格納する
            self.volume = {
                'buy': reduce(add, self.executions['BUY'].values(), 0),
                'sell': reduce(add, self.executions['SELL'].values(), 0),
                'time': datetime.datetime.now()
            }


    def on_close(self, ws):
        # 切断時にデータを初期化しておく
        # buysellの数量が0だと取引しないので0にする
        self.volume = {
            'buy': 0,
            'sell': 0,
            'time': datetime.datetime.now()
        }
        print('### connection close {} ###'.format(self.PRODUCT))
        self.ws.close()
        # sys.exit(1)


    def on_error(self, ws, error):
        # errorでもcloseと同様に0で初期化
        self.volume = {
            'buy': 0,
            'sell': 0,
            'time': datetime.datetime.now()
        }
        print('### ERROR ###')
        print(error)
        with open(self.path_BASE + '/Error/Error_log_on_error_{0:%Y%m%d_%H%M%S}.dsv'.format(datetime.datetime.now()), mode=('a')) as f:
            # np.savetxt(f, e, delimiter='\t', fmt='%s')
            traceback.print_exc(file=f)

        # print(format(error))
        # print(traceback.print_exc())

        self.ws.close()
        # sys.exit(1)


    def on_open(self, ws):
        self.ws.send(json.dumps(
            {
                'method': 'subscribe',
                'params': { 'channel' : 'lightning_executions_{}'.format('FX_BTC_JPY')},
                'id': None
            }
        ))

        self.ws.send(json.dumps(
            {
                'method': 'subscribe',
                'params': { 'channel' : 'lightning_ticker_FX_BTC_JPY'},
                'id': None
            }
        ))


    def run_websocket(self):
        '''run_websocket

        約定履歴取得用のwebsocket通信を別スレッドで開始する

        '''

        self.th_ws = threading.Thread(target=self.ws.run_forever)
        self.ws.keep_running = True
        # self.th_ws.daemon = True
        self.th_ws.start()


    def stop_websocket(self):
        '''stop_websocket

        websocket通信を停止

        '''

        self.ws.keep_running = False
        self.ws.close()


    def load_json(self):
        '''load_json

        config.jsonを再読込
        途中で設定を変えたくなった時用

        '''

        with open(self.path_config, 'r') as f:
            self.bitflyer_params = json.load(f)


    def save_header(self):
        Trade_log_header = [['ordersize',
                             'deltaTime',
                             'L_Entry_filter',
                             'S_Entry_filter',
                             'L_Exit_filter',
                             'S_Exit_filter',
                             'profitspread',
                             'orderbreak',
                             'loopinterval',
                             'sarver_status',
                             'n',
                             'now_datetime',
                             'order_side',
                             'ask_price',
                             'bid_price',
                             'order_price',
                             'maxamount',
                             'Hoyu_size',
                             'BSI',
                             'buy_volume',
                             'sell_volume'
                             ]]

        log_test_header = [['datetime',
                            'buy_volume',
                            'sell_bolume',
                            'BSI',
                            'L_Entry_filter',
                            'S_Entry_filter',
                            'L_Exit_filter',
                            'S_Exit_filter',
                            'Hoyu_size',
                            'maxamount',
                            'ask_price',
                            'bid_price'
                            ]]

        executions_comp_header = [['datetime',
                                   'BuySell',
                                   'price',
                                   'amount'
                                   ]]

        np.savetxt(self.path_BASE + '/header/Trade_log_header.txt'      , Trade_log_header,       delimiter='\t', fmt='%s')
        np.savetxt(self.path_BASE + '/header/log_test_header.txt'       , log_test_header,        delimiter='\t', fmt='%s')
        np.savetxt(self.path_BASE + '/header/executions_comp_header.txt', executions_comp_header, delimiter='\t', fmt='%s')

    # ↑ここまでmmbotとほとんど一緒
    # ↓ここからリアルタイムグラフ


    def plot_main(self):
        '''plot_main

        過去N秒間の取引数量を横向きの棒グラフで表示

        '''

        fig, ax = plt.subplots(1, 1)

        x = [0, 0]
        y = [0, 1]

        lines, = ax.plot(x, y)

        plt.clf()

        while True:
            plt.clf()


            plt.barh([0], [accum_vol.volume['buy']], align='center', color="#FCDA19")
            plt.barh([1], [accum_vol.volume['sell']], align='center', color="#FA9919")

            max_vol = np.ceil(np.max([accum_vol.volume['buy'], accum_vol.volume['sell']]))

            plt.xlim([0, np.max([max_vol + max_vol * 0.05, 250])])

            plt.yticks([0, 1], ['buy', 'sell'])

            plt.pause(0.1)


    def plot_main_2(self, x_range=65):
        '''plot_main_2

        現在の価格(tickのmid)
        過去N秒間の取引数量
        を折れ線グラフで表示

        第1軸:tick mid
        第2軸:buy, sellの取引数量

        パラメーター
        ----------
        x_range : int, optional
            x軸の幅

        '''

        fig, ax1 = plt.subplots(1, 1)

        ax2 = ax1.twinx()

        # 初期値セット
        x = np.arange(0, x_range)
        mid_price = list(np.zeros(x_range))
        sell_vol  = list(np.zeros(x_range))
        buy_vol   = list(np.zeros(x_range))

        # 売買点用のリスト初期化
        L_entry_x  = []
        L_entry_y  = []
        L_exit_x = []
        L_exit_y = []

        S_entry_x  = []
        S_entry_y  = []
        S_exit_x = []
        S_exit_y = []

        # line_test = [[0, 0, 0, 0]]
        line_test = np.zeros((0, 4))
        line_b = np.zeros((0, 4))
        line_r = np.zeros((0, 4))

        # 初期化用に1回プロット
        # 以降のデータ更新にはlines*を使用する
        lines1, = ax1.plot(x, mid_price, color='#18B6F9', label='mid price', linewidth=1.5) # mid価格
        lines2, = ax2.plot(x, sell_vol, color="#FA9919",  label='sell vol',  linewidth=1) # 売り数量
        lines3, = ax2.plot(x, buy_vol,  color="#FCDA19",  label='buy  vol',  linewidth=1) # 買い数量

        # plotを利用した散布図で出力
        lines_L_entry, = ax1.plot(L_entry_x, L_entry_y, color='#FCDA19', markersize=6, marker='^', linestyle='None') # Entry点
        lines_S_entry, = ax1.plot(S_entry_x, S_entry_y, color='#FA9919', markersize=6, marker='v', linestyle='None') # Entry点

        lines_L_exit , = ax1.plot(L_exit_x,  L_exit_y,  color='#FCDA19', markersize=10, marker='v', linestyle='None') # Exit点
        lines_S_exit , = ax1.plot(S_entry_x, S_entry_y, color='#FA9919', markersize=10, marker='^', linestyle='None') # Entry点


        # EntryしたかExitしたかの判定に使用する deepcopy
        old_position = 0

        while self.flag_plot:

            # x軸の値をずらす
            x += 1

            # 価格、数量を追加
            mid_price.append(self.tick_mid)
            sell_vol.append(self.volume['sell'])
            buy_vol.append(self.volume['buy'])

            # x_rangeの長さにする
            mid_price = mid_price[-x_range:]
            sell_vol  =  sell_vol[-x_range:]
            buy_vol   =   buy_vol[-x_range:]


            # Exit, Entry点をLongとShortに分ける
            # Longがオレンジ, Shortがイエロー

            # if old_position is 1 and self.position is -1:
            if 1 <= old_position and self.position <= -1:
                # L_exit & S_entry
                L_exit_x.append(x[-1])
                L_exit_y.append(self.tick_mid)
                S_entry_x.append(x[-1])
                S_entry_y.append(self.tick_mid)



            # elif old_position is -1 and self.position is 1:
            elif -1 >= old_position and 1 <= self.position:
                # S_exit & L_entry
                S_exit_x.append(x[-1])
                S_exit_y.append(self.tick_mid)
                L_entry_x.append(x[-1])
                L_entry_y.append(self.tick_mid)



            # elif old_position is 1 and self.position is 0:
            elif 1 <= old_position and self.position is 0:
                # L_exit
                L_exit_x.append(x[-1])
                L_exit_y.append(self.tick_mid)




            # elif old_position is -1 and self.position is 0:
            elif -1 >= old_position and self.position is 0:
                # S_exit
                S_exit_x.append(x[-1])
                S_exit_y.append(self.tick_mid)


            # elif old_position is 0 and self.position is 1:
            # elif old_position is 0 and 1 <= self.position:
            elif old_position < self.position:
                # L_entry
                L_entry_x.append(x[-1])
                L_entry_y.append(self.tick_mid)

            # elif old_position is 0 and self.position is -1:
            # elif old_position is 0 and -1 >= self.position:
            elif old_position > self.position:
                # S_entry
                S_entry_x.append(x[-1])
                S_entry_y.append(self.tick_mid)


            lines1.set_data(x, mid_price)
            lines2.set_data(x, sell_vol)
            lines3.set_data(x, buy_vol)

            # LS, EntryExitの点をセット
            # メモリに優しくなった
            # [-(x[-1]-x_range):] ←こんなにデータためてたら手遅れなきがする
            # 画面上にそんなに大量にplotされないので30個くらいで決め打ちしちゃっていいかも
            L_entry_x, L_entry_y = L_entry_x[-50:], L_entry_y[-50:]
            L_exit_x,  L_exit_y  = L_exit_x[-30:],  L_exit_y[-30:]
            S_entry_x, S_entry_y = S_entry_x[-50:], S_entry_y[-50:]
            S_exit_x,  S_exit_y  = S_exit_x[-30:],  S_exit_y[-30:]

            # 売買点のデータを更新
            lines_L_entry.set_data(L_entry_x, L_entry_y)
            lines_L_exit.set_data(L_exit_x, L_exit_y)
            lines_S_entry.set_data(S_entry_x, S_entry_y)
            lines_S_exit.set_data(S_exit_x, S_exit_y)


            # 凡例で価格と数量を確認できるようにlabelを更新
            lines1.set_label('mid  {}'.format(mid_price[-1]))
            lines2.set_label('sell {0: >7.2f}'.format(sell_vol[-1]))
            lines3.set_label('buy  {0: >7.2f}'.format(buy_vol[-1]))

            # 第2軸グラフのy軸範囲設定に使う
            # デフォルト値(100)かmax(数量)の大きい方を範囲に指定する
            max_vol = np.ceil(np.max([np.max(sell_vol), np.max(buy_vol)]))

            # 横軸の表示範囲をセット これ必要？ 2019/03/07
            ax2.set_xlim((x.min(), x.max()))

            try:
                # x_range分データが貯まるまで価格がちゃんと表示されなかったので対応
                # 多分基本的にtryの中t使えてる exceptはいらない子
                ax1.set_ylim((np.min(np.array(mid_price)[np.nonzero(mid_price)])*0.99999, max(mid_price)*1.00001))
            except:
                ax1.set_ylim((min(mid_price)*0.99999, max(mid_price)*1.00001))

            # ここで数量に合わせたy軸幅をセット
            ax2.set_ylim((0, max(100, max_vol * 1.05)))

            # 凡例の場所をいい感じに
            # 重ならないようにax2の凡例場所を下にずらしてる
            ax1.legend(bbox_to_anchor=(0, 1), loc='upper left', borderaxespad=0.5, fontsize=10)
            ax2.legend(bbox_to_anchor=(0, 0.9), loc='upper left', borderaxespad=0.5, fontsize=10)

            # なにも設定していないと価格が指数表記になってしまうので
            # 指数表記なし
            ax1.get_yaxis().get_major_formatter().set_useOffset(False)
            # 値がすべて整数になるように
            ax1.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

            # タイトルで仮想トレード状況がわかるようにする

            # 0除算エラー回避
            if self.cnt_trade is not 0:
                self.win_percent = np.round(self.cnt_win / self.cnt_trade * 100, 2)
            else:
                self.win_percent = 0.0


            ax1.title.set_text('pos = {0:}, pnl = {1:.2f}, last pnl ={2:.2f}, prof = {3:.2f}, loss = {4:.2f}\ntrade count = {5:}, win = {6:}, lose = {7:}, draw = {8:}, winrate = {9:}%'.format(
                self.position,
                self.pnl,
                self.last_pnl,
                self.sum_prof,
                self.sum_loss,
                self.cnt_trade,
                self.cnt_win,
                self.cnt_lose,
                self.cnt_draw,
                self.win_percent))

            # 前回のpositionを保存 次のループで比較に使用する
            old_position = copy.deepcopy(self.position)


            # plotの更新頻度

            plt.pause(.05)

        else:
            plt.clf()


    def trade_main(self):
        self.pnl = self.last_pnl = 0
        self.position = 0

        # 利益、損失のみのそれぞれの合計
        self.sum_prof = self.sum_loss = 0
        # 取引回数
        self.cnt_trade = self.cnt_win = self.cnt_lose = self.cnt_draw= 0


        # あんまり早く動かすと価格が取得できてなくてエラーになる self.deltatime
        # time.sleep(self.bitflyer_params['deltaTime'])
        time.sleep(self.deltatime)

        while True:
            next_time = int(time.time()) + self.interval + 0.1

            # print(self.q.qsize())

            if self.flag_trademain:

                # シグナルチェック
                # exit
                if self.position:
                        # sell 決済

                    # Long Exit
                    # if self.position > 0 and (self.volume['sell'] - self.volume['buy']) > 1:
                    if self.L_Exit():
                        self.exit_price = self.tick_ask

                        # self.last_pnl = self.exit_price - self.entry_price
                        pnls = [self.exit_price - self.q.get_nowait()[0] for i in range(self.q.qsize())]
                        self.last_pnl = np.round(np.sum(pnls) * self.trade_amount, 3)


                        self.pnl += self.last_pnl


                        if self.last_pnl > 0:
                            # 利益
                            self.add_win()

                        elif self.last_pnl < 0:
                            # 損失
                            self.add_lose()

                        elif self.last_pnl is 0:
                            self.add_draw()


                        self.cnt_trade += 1


                        # with open(self.path_BASE + '/log/{0:%Y%m%d}.txt'.format(datetime.datetime.now()), 'ab') as f:
                        with open(self.path_BASE + '/log/{{{0:}}}_{1:%Y%m%d}.txt'.format(self.start_datetime, datetime.datetime.now()), 'ab') as f:
                            np.savetxt(f,
                                    [[
                                            '{0:%Y/%m/%d %H:%M:%S}'.format(datetime.datetime.now()),
                                            'L',
                                            self.entry_price,
                                            self.exit_price,
                                            self.last_pnl,
                                            self.pnl
                                    ]],
                                    delimiter='\t',
                                    fmt='%s')

                        self.position = self.entry_price = self.exit_price = 0


                    # ここが売買条件 メソッド化して切り替えやすくする
                    # Short Exit
                    # elif self.position < 0 and (self.volume['buy'] - self.volume['sell']) > 1:
                    elif self.S_Exit():
                        self.exit_price = self.tick_bid

                        # self.last_pnl = self.entry_price - self.exit_price

                        pnls = [self.q.get_nowait()[0] - self.exit_price for i in range(self.q.qsize())]
                        self.last_pnl = np.round(np.sum(pnls) * self.trade_amount, 3)

                        self.pnl += self.last_pnl


                        if self.last_pnl > 0:
                            # 利益
                            self.add_win()

                        elif self.last_pnl < 0:
                            # 損失
                            self.add_lose()

                        elif self.last_pnl is 0:
                            self.add_draw()


                        self.cnt_trade += 1


                        # with open(self.path_BASE + '/log/{0:%Y%m%d}.txt'.format(datetime.datetime.now()), 'ab') as f:
                        with open(self.path_BASE + '/log/{{{0:}}}_{1:%Y%m%d}.txt'.format(self.start_datetime, datetime.datetime.now()), 'ab') as f:
                            np.savetxt(f,
                                    [[
                                            '{0:%Y/%m/%d %H:%M:%S}'.format(datetime.datetime.now()),
                                            'S',
                                            self.entry_price,
                                            self.exit_price,
                                            self.last_pnl,
                                            self.pnl
                                    ]],
                                    delimiter='\t',
                                    fmt='%s')

                        self.position = self.entry_price = self.exit_price = 0

                if self.max_position > abs(self.position):

                    # entry
                    # buy long
                    # if self.volume['buy'] > (self.volume['sell'] * 2) and self.position >= 0:
                    if self.L_Entry():
                        # bid
                        self.position += 1
                        self.entry_price = self.tick_bid
                        self.q.put([self.entry_price, self.trade_amount, time.time(), 'BUY', 'L'])


                    # sell short
                    # 複数ポジに対応するので
                    # elif self.volume['sell'] > (self.volume['buy'] * 2) and self.position <= 0:
                    elif self.S_Entry():
                        # ask
                        self.position += -1
                        self.entry_price = self.tick_ask
                        self.q.put([self.entry_price, self.trade_amount, time.time(), 'SELL', 'S'])

            now_time = time.time()
            if 0 < (next_time - now_time):
                time.sleep(next_time - now_time)


    def run_trade_main(self):
        self.th_trade_main = threading.Thread(target=self.trade_main)
        self.th_trade_main.start()


    def add_win(self):
        self.sum_prof += self.last_pnl
        self.cnt_win  += 1


    def add_lose(self):
        self.sum_loss += self.last_pnl
        self.cnt_lose += 1


    def add_draw(self):
        self.cnt_draw += 1


    def save_trade_log(self, order_type):
        with open(self.path_BASE + '/log/{{{0:}}}_{1:%Y%m%d}.txt'.format(self.start_datetime, datetime.datetime.now()), 'ab') as f:
            np.savetxt(f,
                        [[
                            '{0:%Y/%m/%d %H:%M:%S}'.format(datetime.datetime.now()),
                            order_type,
                            self.cnt_trade,
                            self.cnt_win,
                            self.cnt_lose,
                            self.cnt_draw,
                            self.entry_price,
                            self.exit_price,
                            self.last_pnl,
                            self.pnl
                        ]],
                        delimiter='\t',
                        fmt='%s')


    def test(self):
        # 実行
        root = tk.Tk()
        myapp = Application(master=root)
        myapp.master.title("My Application") # タイトル
        myapp.master.geometry("500x200") # ウィンドウの幅と高さピクセル単位で指定（width x height）

        myapp.mainloop()


    def test_print(self):
        # print('TEST!')
        print(self.pnl)


    def set_deltatime(self, new_deltatime):
        if self.deltatime > new_deltatime:
            # 時間を短くする
            print('delta time {} -> {}'.format(self.deltatime, new_deltatime))

            self.deltatime = new_deltatime

        elif new_deltatime > self.deltatime:
            # 時間を長くする
            # 差分秒分のデータを蓄積ためにtime.sleepする
            self.flag_trademain = False

            print('delta time {} -> {}'.format(self.deltatime, new_deltatime))

            self.deltatime = new_deltatime

            time.sleep(new_deltatime - self.deltatime + 1)

            self.flag_trademain = True

        else:
            # do nothing
            print('delta time {} -> {}'.format(self.deltatime, new_deltatime))


    def set_trade_amount(self, new_trade_amount):
        print('trade amount {} -> {}'.format(self.trade_amount, new_trade_amount))
        self.trade_amount = new_trade_amount


    def set_max_position(self, new_max_position):
        print('max position {} -> {}'.format(self.max_position, new_max_position))
        self.max_position = new_max_position


    # Entry #################################################
    def _L_Entry_1(self):
        # 売り数量の2倍より買い数量が多いときにLong Entry
        return self.volume['buy'] > (self.volume['sell'] * 2) and self.position >= 0


    def _S_Etnry_1(self):
        # 買い数量の2倍より売り数量が多いときにShort Entry
        return self.volume['sell'] > (self.volume['buy'] * 2) and self.position <= 0
    #########################################################


    # Exit ##################################################
    def _L_Exit_1(self, vol=1):
        # 保有数量がプラス(買いポジ) & 売り出来高が買いより多い
        # volが大きくなるとドテン気味になる
        return self.position > 0 and (self.volume['sell'] - self.volume['buy']) > vol


    def _S_Exit_1(self, vol=1):
        # 保有数量がマイナス(売りポジ) & 買い出来高が売りより多い
        # volが大きくなるとドテン気味になる
        return self.position < 0 and (self.volume['buy'] - self.volume['sell']) > vol


    def _L_Exit_2(self, vol=0):
        # 保有数量がプラス(買いポジ) & 売り出来高が買いより多い
        # volが大きくなるとドテン気味になる
        return self.position > 0 and (self.volume['sell'] - self.volume['buy']) > vol


    def _S_Exit_2(self, vol=0):
        # 保有数量がマイナス(売りポジ) & 買い出来高が売りより多い
        # volが大きくなるとドテン気味になる
        return self.position < 0 and (self.volume['buy'] - self.volume['sell']) > vol

    #########################################################

    def def_LS_EnEx(self, LS_En=1, LS_Ex=1):
        # 1番最初の設定を初期値にしてる
        if LS_En is 1:
            self.L_Entry = self._L_Entry_1
            self.S_Entry = self._S_Etnry_1

        elif LS_En is 2:
            pass

        if LS_Ex is 1:
            self.L_Exit = self._L_Exit_1
            self.S_Exit = self._S_Exit_1

        elif LS_Ex is 2:
            self.L_Exit = self._L_Exit_2
            self.S_Exit = self._S_Exit_2

        elif LS_Ex is 3:
            pass


    def plot_clf(self):
        # plt.clf()
        plt.cla()



# アプリケーション（GUI）クラス
class Application(tk.Frame):
    DEBUG_LOG = True
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.accum_vol = accum_trade_volume(path_cd + '/')

        self.create_widgets()
        self.run_accum_vol()


    def create_widgets(self):
        print('DEBUG:----{}----'.format(sys._getframe().f_code.co_name)) if self.DEBUG_LOG else ""

        pw_main = tk.PanedWindow(self.master, orient='horizontal')
        pw_main.pack(expand=True, fill=tk.BOTH, side='left')

        fm_main = tk.Frame(pw_main, bd=2, relief='ridge')
        pw_main.add(fm_main)

        # ラベル3つ
        label_deltatime    = tk.Label(fm_main, text='delta sec (int)', width=20)
        label_trade_amount = tk.Label(fm_main, text='trade amount (float)', width=20)
        label_max_position = tk.Label(fm_main, text='max position (int)', width=20)

        label_deltatime.grid(row=0, column=0 , sticky=tk.W + tk.E, padx=2, pady=2)
        label_trade_amount.grid(row=1, column=0 , sticky=tk.W + tk.E, padx=2, pady=2)
        label_max_position.grid(row=2, column=0 , sticky=tk.W + tk.E, padx=2, pady=2)

        # 入力BOX3つ
        self.entry_deltatime = tk.Entry(fm_main, justify='left', width=20)
        self.entry_trade_amount = tk.Entry(fm_main, justify='left', width=20)
        self.entry_max_position = tk.Entry(fm_main, justify='left', width=20)

        self.entry_deltatime.grid(row=0, column=1, sticky=tk.W + tk.E,padx=2, pady=2)
        self.entry_trade_amount.grid(row=1, column=1, sticky=tk.W + tk.E,padx=2, pady=2)
        self.entry_max_position.grid(row=2, column=1, sticky=tk.W + tk.E,padx=2, pady=2)

        ## 先頭行に値を設定
        self.entry_deltatime.insert( 0, '10' )
        self.entry_trade_amount.insert( 0, '0.01' )
        self.entry_max_position.insert( 0, '25' )


        #
        btn_deltatime = tk.Button(fm_main, text='set deltatime', command=self.set_deltatime)
        btn_trade_amount = tk.Button(fm_main, text='set trade amount', command=self.set_trade_amount)
        btn_max_position = tk.Button(fm_main, text='set max position', command=self.set_max_position)

        btn_deltatime.grid(row=0, column=2, sticky=tk.W + tk.E, padx=2, pady=2)
        btn_trade_amount.grid(row=1, column=2, sticky=tk.W + tk.E, padx=2, pady=2)
        btn_max_position.grid(row=2, column=2, sticky=tk.W + tk.E, padx=2, pady=2)


    def set_deltatime(self):
        # ボタンイベント
        deltatime = self.entry_deltatime.get()
        # print(type(deltatime))


        if deltatime.isdecimal():
            self.accum_vol.set_deltatime(int(deltatime))
            # print('set_deltatime... {}'.format(deltatime))
        else:
            print('deltatime is not int')


    def set_trade_amount(self):
        trade_amount = self.entry_trade_amount.get()

        if self.is_float(trade_amount):
            # print('set_trade_amount... {}'.format(trade_amount))
            self.accum_vol.set_trade_amount(float(trade_amount))
        else:
            print('trade_amount is not float or int')


    def set_max_position(self):
        max_position = self.entry_max_position.get()
        # print('set_max_position... {}'.format(max_position))

        if max_position.isdecimal():
            # print('set_max_position... {}'.format(max_position))
            self.accum_vol.set_max_position(int(max_position))
        else:
            print('max_position is not int')


    def is_float(self, s):
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True


    def run_accum_vol(self):
        self.accum_vol.run_websocket()
        self.accum_vol.run_trade_main()

        self.run_plot_main()


    def run_plot_main(self):
        self.accum_vol.flag_plot = True

        th_plot_main_2 = threading.Thread(target=self.accum_vol.plot_main_2, args=(1000, ))
        th_plot_main_2.start()


    def stop_plot_main(self):
        self.accum_vol.flag_plot = False



if __name__ == '__main__':

    plt.rcParams['font.family'] = 'Migu 1M'
    plt.rcParams['font.size'] = '11'

    path_cd = sys.argv[1]


    # 実行
    root = tk.Tk()

    # タスクバーを非表示にする ウィンドウの移動ができなくなるので無し
    # root.overrideredirect(True)

    # 閉じるボタンを無効化
    root.protocol('WM_DELETE_WINDOW', (lambda: 'pass'))


    myapp = Application(master=root)
    myapp.master.title("My Application") # タイトル
    myapp.master.geometry("400x200") # ウィンドウの幅と高さピクセル単位で指定（width x height）


    myapp.mainloop()
