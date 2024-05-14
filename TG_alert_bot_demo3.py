# coding=u8
import datetime
import time
import requests
import telebot

# import ccxt
# import pandas as pd
# import pandas_ta as ta

# exchange = ccxt.poloniex({'enableRateLimit': True})
# exchange.load_markets()

API_KEY = '6549214641:AAFDYrwOmsfA9cM4WXWNYQ8t3xfCX9A-Qz0'
bot = telebot.TeleBot(API_KEY)


#
#
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    print(message.chat.id)
    bot.reply_to(message, "What's up")


# bot.polling()


# symbol = 'BTC/USDT'
#
# # 上穿告警的指定价格
# cross_value = 40500
#
# 需要指定某个chat_id
CHAT_ID = -1001897970172
#
# alert_dt = datetime.datetime(1970, 1, 1, 0, 0, 0)


# while True:
#     time.sleep(2)
#     data = exchange.fetchOHLCV(symbol, '5m', limit=100)
#     bid = exchange.fetch_ticker(symbol)['bid']
#     print('bid: %s' % bid)
#     df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#
#     df['crossover'] = ta.cross_value(df['close'], cross_value)
#     latest_price = df.at[len(df) - 1, 'close']
#     print('latest price: %s' % round(latest_price, 2))
#     latest_crossover = df.at[len(df) - 1, 'crossover']
#     print('latest price: %s' % latest_crossover)
#     print(df[['timestamp', 'close', 'crossover']].tail())
#
#     alert_once = False
#     now = datetime.datetime.now()
#     alert_duration = now - alert_dt
#
#     if latest_crossover == 1 and not alert_once and alert_duration.seconds / 3600 > 1:
#         message = f'请注意：{symbol}价格向上穿越 {cross_value}啦😉'
#         bot.send_message(CHAT_ID, message)
#         alert_once = True
#         alert_dt = now

separator = "\n-----------------------------------------\n"
count = 0


def initialize_api_data(api_base_url, api_data_list):
    """首次运行时获取所有API数据并填充到api_data_list中"""
    bot.send_message(CHAT_ID, '数据初始化！')

    for api_info in api_data_list:
        unique_name = api_info['uniqueName']
        url = f"{api_base_url}?uniqueName={unique_name}"
        response = requests.get(url)
        count = 0
        if response.status_code == 200:
            api_info['previous_data'] = response.json()
            current_data = response.json()
            print(f"初始化数据完成，{api_info['name']} ，返回数据：{response.json()}")
            message = ''
            for data_list in current_data['data']:
                if count >= 15:
                    break
                count += 1
                # print(f"产品：{data_list['instId']} X{data_list['lever']}\n方向：{'多' if data_list['side'] == 'buy' else '空'}\n开仓价：{data_list['openAvgPx']}")
                message += f"产品：{data_list['instId']} X{data_list['lever']}\n方向：{'多' if data_list['side'] == 'buy' else '空'}\n开仓价：{data_list['openAvgPx']}"
                if count < 15:
                    message += separator
                # bot.send_message(CHAT_ID, f"跟单员：{api_info['name']} \n产品：{data_list['instId']} X{data_list['lever']}\n方向：{'多' if data_list['side'] == 'buy' else '空'}\n开仓价：{data_list['openAvgPx']}")
            # bot.send_message(CHAT_ID, message)
            if message != '':
                bot.send_message(CHAT_ID,
                                 f"跟单员：{api_info['name']} \n{message}\n 免费跟单操作：https://t.me/yiyanchat99")
        else:
            print(f"初始化数据失败，{url} 请求失败，状态码：{response.status_code}")


def initialize_api_data_mx(api_base_url, api_data_list):
    """首次运行时获取所有API数据并填充到api_data_list中"""
    for api_info in api_data_list:
        unique_name = api_info['uniqueName']
        url = f"{api_base_url}?uniqueName={unique_name}"
        response = requests.get(url)
        if response.status_code == 200:
            api_info['previous_data_mx'] = response.json()
            print(f"初始化明细数据完成，{api_info['name']} ，返回数据：{response.json()}")
        else:
            print(f"初始化明细数据失败，{url} 请求失败，状态码：{response.status_code}")


def check_api_changes(api_base_url, api_data_list):
    for api_info in api_data_list:
        unique_name = api_info['uniqueName']
        url = f"{api_base_url}?uniqueName={unique_name}"
        previous_data = api_info.get('previous_data_mx')
        now = datetime.datetime.now()
        response = requests.get(url)
        if response.status_code == 200:
            current_data = response.json()
            if current_data['data'] != '':
                message = ''
                if current_data['data'][0]['openTime'] > previous_data['data'][0]['openTime']:
                    for i in range(len(previous_data['data'])):
                        if current_data['data'][i]['openTime'] >= previous_data['data'][0]['openTime']:
                            message += f"时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n产品：{current_data['data'][i]['instId']} X{current_data['data'][i]['lever']}\n方向：{'多' if current_data['data'][i]['side'] == 'buy' else '空'}\n开仓价：{current_data['data'][i]['openAvgPx']}"
                            message += separator
                    api_info['previous_data_mx'] = current_data
                else:
                    print(f"{api_info['name']} 的数据无变动。{now.strftime('%Y-%m-%d %H:%M:%S')}")
                if message != '':
                    bot.send_message(CHAT_ID,
                                     f"操作变动\n跟单员：{api_info['name']} \n{message}\n 免费跟单操作：https://t.me/yiyanchat99")
                # for i in range(len(previous_data['data'])):
                #     now = datetime.datetime.now()
                #     # print(f"数据：{previous_data['data'][i]['instId']}")
                #     if previous_data['data'][i]['instId'] != current_data['data'][i]['instId'] or \
                #             previous_data['data'][i]['side'] != current_data['data'][i]['side']:
                #         print(f"{api_info['name']} 的数据有变动！{now.strftime('%Y-%m-%d %H:%M:%S')}")
                #         print(
                #             f"产品：{current_data['data'][i]['instId']} X{current_data['data'][i]['lever']}\n方向：{'多' if current_data['data'][i]['side'] == 'buy' else '空'}\n开仓价：{current_data['data'][i]['openAvgPx']}")
                #
                #         message += f"时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n产品：{current_data['data'][i]['instId']} X{current_data['data'][i]['lever']}\n方向：{'多' if current_data['data'][i]['side'] == 'buy' else '空'}\n开仓价：{current_data['data'][i]['openAvgPx']}"
                #         message += separator
                #         # 处理变动逻辑，比如发送通知
                #         # bot.send_message(CHAT_ID, f"时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n带单员：{api_info['name']}\n产品：{current_data['data'][i]['instId']} X{current_data['data'][i]['lever']}\n方向：{'多' if current_data['data'][i]['side'] == 'buy' else '空'}\n开仓价：{current_data['data'][i]['openAvgPx']}")
                #         api_info['previous_data'] = current_data
                #     # for data_list in previous_data['data']:
                #     #     print(f"产品：{data_list['instId']} X{data_list['lever']}\n方向：{'多' if data_list['side'] == 'buy' else '空'}\n开仓价：{data_list['openAvgPx']}")
                #
                #     else:
                #         print(f"{api_info['name']} 的数据无变动。{now.strftime('%Y-%m-%d %H:%M:%S')}")
                #     if message != '':
                #         bot.send_message(CHAT_ID, f"操作变动\n跟单员：{api_info['name']} \n{message}\n 免费跟单操作：https://t.me/yiyanchat99")
        else:
            print(f"{api_info['name']} 请求失败，状态码：{response.status_code}")


# 汇总接口
api_url_hz = "https://www.okx.com/priapi/v5/ecotrade/public/position-summary"
# 明细接口
api_url_mx = "https://www.okx.com/priapi/v5/ecotrade/public/position-detail"

api_data = [
    {'uniqueName': 'F62DDDE09CAD8075', 'name': '木兮x', 'previous_data': None, 'previous_data_mx': None},
    {'uniqueName': 'DDF529A6117DBB92', 'name': '雪球王', 'previous_data': None, 'previous_data_mx': None},
    {'uniqueName': 'B24109240499F28C', 'name': '币盛客BYK', 'previous_data': None, 'previous_data_mx': None},
    {'uniqueName': '37ED9FA6572D8115', 'name': 'KateCryptoAI', 'previous_data': None, 'previous_data_mx': None},
    {'uniqueName': '24D8CE79A97FD35D', 'name': '明明明宏', 'previous_data': None, 'previous_data_mx': None},
    {'uniqueName': '540D011FDACCB47A', 'name': '从小有个百万梦', 'previous_data': None, 'previous_data_mx': None}
]

initialize_api_data(api_url_hz, api_data)
initialize_api_data_mx(api_url_mx, api_data)

while True:
    check_api_changes(api_url_mx, api_data)
    time.sleep(15)  # 每隔60秒检查一次
