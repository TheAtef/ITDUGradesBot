from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from server import server
server()

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

URL = 'https://www.damascusuniversity.edu.sy/ite/index.php'
PREFIX = 'https://www.damascusuniversity.edu.sy/ite/'
API_KEY = os.environ.get('API_KEY')
CHATID = os.environ.get('CHATID')


bot = AsyncTeleBot(API_KEY)

close_button = types.InlineKeyboardButton(text='إغلاق', callback_data='result_no')

markup_year = types.InlineKeyboardMarkup(row_width=6)
markup_year.row(types.InlineKeyboardButton(text='ثانية', callback_data='year8'),
                types.InlineKeyboardButton(text='أولى', callback_data='year7')  
            )
markup_year.row(types.InlineKeyboardButton(text='رابعة', callback_data='year4'),
                types.InlineKeyboardButton(text='ثالثة', callback_data='year13')
            )
markup_year.row(close_button,
            types.InlineKeyboardButton(text='خامسة', callback_data='year5')
            )

markup_department = types.InlineKeyboardMarkup()
markup_department.row(types.InlineKeyboardButton(text='ذكاء', callback_data='dep1'),
                types.InlineKeyboardButton(text='برمحيات', callback_data='dep2'),
            )
markup_department.row(close_button,
                types.InlineKeyboardButton(text='شبكات', callback_data='dep5')
            )

markup_calendar = types.InlineKeyboardMarkup()
for i in range(23, 10, -3):
    markup_calendar.row(
                    types.InlineKeyboardButton(text=2000 + i, callback_data='cal' + str(2000 + i)),
                    types.InlineKeyboardButton(text=2000 + i + 1, callback_data='cal' + str(2000 + i + 1)),
                    types.InlineKeyboardButton(text=2000 + i + 2, callback_data='cal' + str(2000 + i + 2))
                    )
markup_calendar.row(close_button)

markup_season = types.InlineKeyboardMarkup()
markup_season.row(types.InlineKeyboardButton(text='الثاني', callback_data='season2'),
                types.InlineKeyboardButton(text='الأول', callback_data='season1'),
            )
markup_season.row(close_button,
            types.InlineKeyboardButton(text='تكميلي', callback_data='season3'),
            )

async def chat(message):
    userId = message.chat.id
    nameUser = str(message.chat.first_name) + ' ' + str(message.chat.last_name)
    username = message.chat.username
    text = message.text
    date = datetime.now()
    data = f'User id: {userId}\nUsername: @{username}\nName: {nameUser}\nText: {text}\nDate: {date}'
    await bot.send_message(chat_id=CHATID, text=data)

user_dict = dict()

def scrape():
    stuff = dict()
    user_dict['func'] = 2
    user_dict['set'] = 14
    user_dict['Category'] = 0
    user_dict['lang'] = 1
    r = requests.post(URL, data=user_dict)
    soup = BeautifulSoup(r.content, "lxml")
    try:
        table = soup.find('div', class_='Page_Body').table.find_all('tr')[1:]
    except:
        table = []
    if len(table) == 0:
        user_dict.clear()
        return None
    for index, item in enumerate(table):
        row = [] #title - department = year - calendar - season - href
        row.append(item.find_all('td')[0].text.strip())
        row.append(item.find_all('td')[1].text.strip())
        row.append(item.find_all('td')[2].text.strip())
        row.append(item.find_all('td')[3].text.strip())
        row.append(item.find_all('td')[4].text.strip())
        row.append(item.find_all('td')[-1].find('a', href=True)['href'])
        stuff[index] = row
    user_dict.clear()
    return stuff
    
@bot.message_handler(commands=['start'])
async def reply(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    caption = 'بوت العلامات لكلية المعلوماتية - جامعة دمشق\n/files ببعتلك ملفات العلامات\n/contact لتحاكي صاحب البوت'
    await bot.send_message(message.chat.id, caption, reply_to_message_id=message.message_id)
    await chat(message)
    
@bot.message_handler(commands=['contact'])
async def contact(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    smsg = "Contact bot creator to report a bug or suggest a feature:\n@Absurduck\nhttps://t.me/Absurduck"
    await bot.reply_to(message, smsg, disable_web_page_preview=True)
    await chat(message)
        
@bot.message_handler(commands=['files'])
async def reply(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    await bot.send_message(message.chat.id, 'اختار السنة          :', reply_markup= markup_year, reply_to_message_id=message.message_id)
    await chat(message)

@bot.message_handler(commands=None)
async def reply(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    caption = 'بوت العلامات لكلية المعلوماتية - جامعة دمشق\n/files ببعتلك ملفات العلامات\n/contact لتحاكي صاحب البوت'
    await bot.send_message(message.chat.id, caption, reply_to_message_id=message.message_id)
    await chat(message)
    
@bot.callback_query_handler(func=lambda call: True)
async def callback_data(call):
    if call.message:
        if call.data.startswith('year'):
            await bot.send_chat_action(call.message.chat.id, action='typing')
            data = call.data.removeprefix('year')
            user_dict['StadyYear'] = data
            if int(data) in [4 , 5]:
                await bot.edit_message_text('اختار القسم          :', call.message.chat.id, call.message.message_id, reply_markup=markup_department)
            else:
                user_dict['department_id'] = 3
                user_dict['CStadyYear'] = data
                await bot.edit_message_text('اختار السنة          :', call.message.chat.id, call.message.message_id, reply_markup=markup_calendar)

        if call.data.startswith('dep'):
            await bot.send_chat_action(call.message.chat.id, action='typing')
            data = call.data.removeprefix('dep')
            user_dict['department_id'] = data
            if user_dict['StadyYear'] == '4' and user_dict['department_id'] == '1':
                user_dict['StadyYear'] = 16 #forth year ai
                user_dict['CStadyYear'] = 16
            elif user_dict['StadyYear'] == '4' and user_dict['department_id'] == '2':
                user_dict['StadyYear'] = 4 #forth year prog
                user_dict['CStadyYear'] = 4
            if user_dict['StadyYear'] == '4' and user_dict['department_id'] == '5':
                user_dict['StadyYear'] = 14 #forth year networks
                user_dict['CStadyYear'] = 14
            if user_dict['StadyYear'] == '5' and user_dict['department_id'] == '1':
                user_dict['StadyYear'] = 9 #fifth year ai
                user_dict['CStadyYear'] = 9
            if user_dict['StadyYear'] == '5' and user_dict['department_id'] == '2':
                user_dict['StadyYear'] = 5 #fifth year prog
                user_dict['CStadyYear'] = 5
            if user_dict['StadyYear'] == '5' and user_dict['department_id'] == '5':
                user_dict['StadyYear'] = 15 #fifth year network
                user_dict['CStadyYear'] = 15
            
            await bot.edit_message_text('اختار السنة          :', call.message.chat.id, call.message.message_id, reply_markup=markup_calendar)

        if call.data.startswith('cal'):
            await bot.send_chat_action(call.message.chat.id, action='typing')
            data = call.data.removeprefix('cal')
            user_dict['Year'] = data
            await bot.edit_message_text('اختار الفصل          :', call.message.chat.id, call.message.message_id, reply_markup=markup_season)

        if call.data.startswith('season'):
            await bot.send_chat_action(call.message.chat.id, action='typing')
            data = call.data.removeprefix('season')
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            user_dict['Season'] = data
            await bot.send_sticker(call.message.chat.id, 'CAACAgQAAxkBAAEyjyhn0DRDIWF4EIYMJT7ONqX7Jq1onAAC5AwAApx16VCo-PNYmZ95ujYE')
            stuff = scrape()
            if '/files' in call.message.reply_to_message.text:
                if stuff == None:
                    await bot.send_sticker(call.message.chat.id, 'CAACAgQAAxkBAAEyjyRn0DQ9aKwmeS4H2HuSc_A_NTT_iwAClQwAApjVYVEkVNb5X8QurTYE')
                    await bot.send_message(call.message.chat.id, 'لسا مانزلوا العلامات أخوي')
                else:
                    await bot.send_message(call.message.chat.id, f'لاقيت {str(len(stuff))} ملف\n\n{stuff[0][2]}\n{stuff[0][4]} - {stuff[0][3]}\n{stuff[0][1]}' )
                    for i in stuff:
                        await bot.send_chat_action(call.message.chat.id, "upload_document")
                        x = stuff[i]
                        try:
                            link = (PREFIX + str(x[-1])).replace(' ', '%20')
                            await bot.send_document(call.message.chat.id, link, caption = x[0], timeout=600)
                        except:
                              await bot.send_message(call.message.chat.id, f"{x[0]}\n\nماقدرت ارفعو\n<a href='{PREFIX + str(x[-1]).replace(' ', '%20')}'>اللينك</a> لتنزلو إنت", parse_mode='html')
                    await bot.send_message(call.message.chat.id, 'تم رفوع')
                
        if call.data == 'result_no':
            user_dict.clear()
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

print('Bot is running...')
import asyncio
while True:
    try:
        asyncio.run(bot.infinity_polling(timeout=600, request_timeout=600))
    except:
        asyncio.sleep(10)