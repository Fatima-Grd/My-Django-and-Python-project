#!/usr/bin/python
# -*- coding: utf-8 -*-

import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.util import antiflood
import os
import datetime
import time
import logging
import requests
import mysql.connector
from config import config
from DML import insert_product_data, add_product_mid
from DQL import get_product_data
from config import *

# ایجاد پوشه Data در صورت عدم وجود
os.makedirs('Data', exist_ok=True)

# دیکشنری‌های ذخیره‌سازی داده‌های کاربران
user_steps = dict()  # ذخیره مرحله فعلی کاربران
user_data = dict()   # ذخیره داده‌های موقت کاربران
shopping_cart = dict()  # سبد خرید کاربران




# شناسه‌های پیام‌های از پیش تعریف شده
message_ids = {
    'start'         :   7,
    'invite_link'   :   9,
}

# دستورات معمولی ربات
commands = {
    'start'                 :   "شروع کار با ربات",
    'help'                  :   "نمایش راهنما",
    'menu'                  :   "نمایش منوی اصلی",
    'profile'               :   "مدیریت پروفایل",
    'settings'              :   "تنظیمات ربات",
    'feedback'              :   "ارسال بازخورد",
    'products'              :   "نمایش محصولات",
    'send_document'         :   "ارسال سند",
    'send_file'             :   "ارسال فایل",
    'send_photo'            :   "ارسال عکس",
    'sample_inline'         :   "نمونه اینلاین",
    'show_product'          :   "نمایش محصول",
    'edit_message'          :   "ویرایش پیام",
    'delete_message'        :   "حذف پیام",
    'markdown_text'         :   "متن مارک‌داون",
    'invite_link'           :   "لینک دعوت",
    'get_contact'           :   "دریافت مخاطب",
    'check_sub'             :   "بررسی عضویت",
}

# دستورات ادمین
admin_commands = {
    'add_product'           :   "افزودن محصول به دیتابیس",
    'get_channel_info'      :   "دریافت اطلاعات کانال",
    'set_channel'           :   "تنظیم آیدی کانال",
}

# محصولات نمونه
products = {
    100: {'name': 'خودکار بیک', 'desc': 'خودکار با کیفیت بالا روان و ماندگار', 'price': 15000, 'inv': 50, 'file_id': "pen.jpg"},
    101: {'name': 'مداد HB', 'desc': 'مداد نرم و با کیفیت مناسب برای طراحی', 'price': 8000, 'inv': 100, 'file_id': "pencil.jpg"},
    102: {'name': 'پاک کن نرم', 'desc': 'پاک کن مرغوب و بدون اثرگذاری روی کاغذ', 'price': 5000, 'inv': 75, 'file_id': "eraser.jpg"},
    103: {'name': 'خط کش 30cm', 'desc': 'خط کش دقیق و با کیفیت', 'price': 12000, 'inv': 30, 'file_id': "ruler.jpg"}
}

# صفحه کلید مخفی
hideboard = ReplyKeyboardRemove()

def send_message(*args, **kwargs):
    """
    تابع ارسال پیام با قابلیت ضد اسپم
    """
    try:
        return antiflood(bot.send_message, *args, **kwargs)
    except Exception as e:
        logging.exception('error in send message')

def get_products_channel():
    """
    دریافت آیدی کانال محصولات
    """
    global PRODUCTS_CHANNEL
    return PRODUCTS_CHANNEL

def listener(messages):
    """
    تابع شنود برای لاگ کردن پیام‌ها
    """
    for m in messages:
        if m.content_type == 'text':
            print(f"{m.chat.first_name} [{m.chat.id}]: {m.text}")

# ایجاد نمونه ربات
bot = telebot.TeleBot(API_TOKEN)
bot.set_update_listener(listener)

def clean_text(text):
    """
    تابع برای escape کردن کاراکترهای مخصوص MarkdownV2
    """
    return str(text).replace('.', '\\.').replace('_', '\\_').replace('*', '\\*').replace('-', '\\-').replace('!', '\\!')

def get_product_markup(code, qty):
    """
    ایجاد صفحه کلید اینلاین برای محصول
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('➖', callback_data=f'change_{code}_{qty-1}'),
        InlineKeyboardButton(str(qty), callback_data='Nothing'),
        InlineKeyboardButton('➕', callback_data=f'change_{code}_{qty+1}'))
    markup.add(InlineKeyboardButton('افزودن به سبد', callback_data=f'add_{code}_{qty}'))
    markup.add(InlineKeyboardButton('انصراف', callback_data='cancel'))
    return markup

def create_product_caption(name, desc, price, category, product_id, for_channel=True, quantity=0):
    """
    ایجاد کپشن برای محصول
    """
    text = f"""
*نام محصول:* {clean_text(name)}
*توضیحات محصول:* {clean_text(desc)}
*قیمت محصول:* {clean_text(price)} تومان
*دسته‌بندی:* {clean_text(category)}"""
    if for_channel:
        text += f"\n*\\[خرید\\]* (https://t.me/Python_advance_FatiMa_Bot?start=buy_{product_id})"
    else:
        text += f"\n*قیمت کل:* {clean_text(price*quantity)} تومان"
    return text

def show_product_detail(cid, product_id):
    """
    تابع نمایش جزئیات محصول
    """
    product_info = products.get(product_id)
    if product_info:
        caption = f"""
📦 *{product_info['name']}*

📝 توضیحات: {product_info['desc']}
💰 قیمت: {product_info['price']:,} تومان
📊 موجودی: {product_info['inv']} عدد

🆔 کد محصول: {product_id}
        """
        
        try:
            # تلاش برای ارسال عکس
            with open(product_info['file_id'], 'rb') as photo:
                bot.send_photo(
                    cid, 
                    photo, 
                    caption=caption, 
                    parse_mode='Markdown',
                    reply_markup=get_product_markup(product_id, 1)
                )
        except FileNotFoundError:
            # اگر عکس پیدا نشد، فقط متن ارسال شود
            bot.send_message(
                cid, 
                caption, 
                parse_mode='Markdown',
                reply_markup=get_product_markup(product_id, 1)
            )
    else:
        bot.send_message(cid, "❌ محصولی با این کد یافت نشد.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """
    هندلر کلیک روی دکمه‌های اینلاین
    """
    call_id = call.id
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    print(f'call id: {call_id}, cid: {cid}, mid: {mid}, data: {data}')
    
    if data.startswith('show_'):
        # هندلر نمایش محصول از طریق اینلاین
        product_id = int(data.split('_')[1])
        show_product_detail(cid, product_id)
        bot.answer_callback_query(call_id, f"نمایش محصول {product_id}")
    
    elif data.startswith('data_button'):
        # هندلر دکمه‌های داده‌ای
        button_no = data.split('_')[-1]
        bot.answer_callback_query(call_id, f'you pressed button {button_no}')
    
    elif data.startswith('change'):
        # هندلر تغییر تعداد محصول
        _, product_id, qty = data.split('_')
        qty = int(qty)
        if qty <= 0:
            bot.answer_callback_query(call_id, 'تعداد نمی‌تواند صفر یا کمتر باشد')
        else:
            product_info = products.get(int(product_id))
            if product_info:
                new_caption = create_product_caption(product_info['name'], product_info['desc'], product_info['price'], "لوازم التحریر", product_id, for_channel=False, quantity=qty)
                bot.edit_message_caption(new_caption, cid, mid, parse_mode='MarkdownV2', reply_markup=get_product_markup(int(product_id), qty))
    
    elif data.startswith('add'):
        # هندلر افزودن به سبد خرید
        _, code, qty = data.split('_')
        code = int(code)
        qty = int(qty)
        shopping_cart.setdefault(cid, dict())
        shopping_cart[cid].setdefault(code, 0)
        shopping_cart[cid][code] += qty
        bot.answer_callback_query(call_id, f'محصول {code} به تعداد {qty} به سبد اضافه شد')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('افزودن به سبد ✅', callback_data='nothing'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('پرداخت', callback_data='checkout'))
        markup.add(InlineKeyboardButton('ادامه خرید', callback_data='remove'))
        bot.send_message(cid, 'یکی از گزینه‌ها را انتخاب کنید', reply_markup=markup)
        
    elif data == 'checkout':
        # هندلر پرداخت
        bot.answer_callback_query(call_id, 'پرداخت')
        if cid in shopping_cart and shopping_cart[cid]:
            amount = 0
            text = 'موارد سبد خرید:\n'
            for code, qty in shopping_cart[cid].items():
                product_info = products.get(code)
                amount += product_info['price'] * qty
                text += f"{product_info['name']}, تعداد: {qty}\n"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('پرداخت', callback_data=f'pay_{amount}'))
            bot.edit_message_text(text, cid, mid, reply_markup=markup)
        else:
            bot.send_message(cid, "هیچ موردی در سبد وجود ندارد")
    
    elif data.startswith('pay'):
        # هندلر درگاه پرداخت
        _, amount = data.split('_')
        amount = float(amount)
        send_message(cid, f'لطفا مبلغ {clean_text(amount)} تومان را به حساب زیر واریز و عکس فیش را ارسال کنید\n`6037991111111111`', parse_mode='MarkdownV2')
        user_steps[cid] = 'PAY'
        user_data[cid] = amount  
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('پرداخت ✅', callback_data='nothing'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    
    elif data == 'remove':
        # هندلر ادامه خرید
        bot.answer_callback_query(call_id, 'ادامه خرید')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('ادامه خرید ✅', callback_data='nothing'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    
    elif data == 'cancel':
        # هندلر انصراف
        bot.answer_callback_query(call_id, 'انصراف')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('✔ انصراف ✔', callback_data='nothing'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    
    elif data == 'nothing':
        # هندلر دکمه بدون عمل
        bot.answer_callback_query(call_id, 'چیزی برای نمایش وجود ندارد')
    
    else:
        # هندلر داده ناشناخته
        bot.answer_callback_query(call_id, 'داده ناشناخته')
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)

@bot.message_handler(commands=['get_channel_info'])
def command_get_channel_info_handler(message):
    """
    هندلر دریافت اطلاعات کانال (فقط ادمین)
    """
    cid = message.chat.id
    if cid not in admins:
        bot.send_message(cid, "❌ این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return
    
    try:
        if PRODUCTS_CHANNEL:
            try:
                channel_info = bot.get_chat(PRODUCTS_CHANNEL)
                info_text = f"""
✅ کانال محصولات شناسایی شد:

📝 عنوان: {channel_info.title}
🆔 آیدی: {channel_info.id}
📞 نام کاربری: @{channel_info.username if channel_info.username else 'ندارد'}
🔗 لینک دعوت: {channel_info.invite_link if hasattr(channel_info, 'invite_link') else 'ندارد'}

متغیر PRODUCTS_CHANNEL: {PRODUCTS_CHANNEL}
"""
                bot.send_message(cid, info_text)
            except Exception as e:
                bot.send_message(cid, f"❌ خطا در اتصال به کانال: {e}")
        else:
            bot.send_message(cid, "❌ کانال محصولات تنظیم نشده است.")
    except Exception as e:
        bot.send_message(cid, f"❌ خطا: {e}")

@bot.message_handler(commands=['set_channel'])
def command_set_channel_handler(message):
    """
    هندلر تنظیم کانال (فقط ادمین)
    """
    cid = message.chat.id
    if cid not in admins:
        bot.send_message(cid, "❌ این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return
    
    try:
        if len(message.text.split()) == 2:
            channel_id = message.text.split()[1]
            try:
                channel_id_int = int(channel_id)
                global PRODUCTS_CHANNEL
                PRODUCTS_CHANNEL = channel_id_int
                try:
                    channel_info = bot.get_chat(channel_id_int)
                    bot.send_message(cid, f"✅ کانال با موفقیت تنظیم شد: {channel_info.title}")
                except Exception as e:
                    bot.send_message(cid, f"⚠️ کانال تنظیم شد اما خطا در اتصال: {e}")
            except ValueError:
                bot.send_message(cid, "❌ فرمت آیدی نامعتبر است.")
        else:
            bot.send_message(cid, "❌ فرمت دستور نادرست است.\nمثال: /set_channel -1001234567890")
    except Exception as e:
        bot.send_message(cid, f"❌ خطا: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    هندلر شروع ربات
    """
    cid = message.chat.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🛍 محصولات', '👤 پروفایل')
    keyboard.add('🛒 سبد خرید', '⚙️ تنظیمات')
    keyboard.add('📖 راهنما', '📝 بازخورد')
    
    welcome_text = """
🎉 به فروشگاه لوازم التحریر خوش آمدید!

📌 برای مشاهده محصولات از منوی زیر استفاده کنید.
💡 برای راهنمایی بیشتر /help را ارسال کنید.
    """
    
    if len(message.text.split()) == 2:
        invite_link = message.text.split()[-1]
        if invite_link == 'send_file':
            command_send_file_handler(message)
        elif invite_link.startswith('buy'):
            try:
                product_code = int(invite_link.split('_')[-1])
                product_info = products.get(product_code)
                if product_info:
                    caption = create_product_caption(product_info['name'], product_info['desc'], product_info['price'], "لوازم التحریر", product_code, for_channel=False, quantity=1)
                    try:
                        with open(product_info['file_id'], 'rb') as photo:
                            bot.send_photo(cid, photo, caption=caption, parse_mode='MarkdownV2', reply_markup=get_product_markup(product_code, 1))
                    except:
                        bot.send_message(cid, caption, parse_mode='MarkdownV2', reply_markup=get_product_markup(product_code, 1))
                else:
                    bot.send_message(cid, 'کد محصول نامعتبر است')
            except ValueError:
                bot.send_message(cid, 'فرمت لینک نامعتبر است')
        else:
            if CHANNEL_CID:
                try:
                    bot.copy_message(cid, CHANNEL_CID, message_ids['invite_link'], reply_to_message_id=message.message_id, reply_markup=keyboard)
                except:
                    bot.send_message(cid, welcome_text, reply_markup=keyboard)
            else:
                bot.send_message(cid, welcome_text, reply_markup=keyboard)
    else:
        bot.send_message(cid, welcome_text, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def command_help_handler(message):
    """
    هندلر نمایش راهنما
    """
    cid = message.chat.id
    text = "📖 راهنمای دستورات ربات:\n\n"
    for command, desc in commands.items():
        text += f"✅ /{command} - {desc}\n"
    
    if cid in admins:
        text += "\n*****دستورات ادمین:*****\n"
        for command, desc in admin_commands.items():
            text += f"🔧 /{command} - {desc}\n"
    
    bot.send_message(cid, text)

@bot.message_handler(commands=['menu'])
def command_menu_handler(message):
    """
    هندلر نمایش منو
    """
    send_welcome(message)

@bot.message_handler(commands=['add_product'])
def command_add_product_handler(message):
    """
    هندلر افزودن محصول (فقط ادمین)
    """
    cid = message.chat.id
    if cid in admins:
        bot.send_message(cid, """📦 لطفاً عکس محصول را با فرمت زیر ارسال کنید:

name:نام محصول
desc:توضیحات محصول
price:قیمت محصول
inv:موجودی محصول
cat:دسته‌بندی محصول
""")
        user_steps[cid] = 'AP'
    else:
        command_default(message)

@bot.message_handler(func=lambda message: message.text == '🛍 محصولات')
def products_handler(message):
    """
    هندلر نمایش محصولات
    """
    cid = message.chat.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('✏️ خودکار و مداد', '📎 لوازم التحریر')
    keyboard.add('🔙 بازگشت')
    bot.send_message(cid, '📂 لطفاً دسته‌بندی مورد نظر را انتخاب کنید:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '✏️ خودکار و مداد')
def pens_pencils_handler(message):
    """
    هندلر نمایش خودکار و مداد
    """
    cid = message.chat.id
    show_product(cid, 100)
    show_product(cid, 101)

@bot.message_handler(func=lambda message: message.text == '📎 لوازم التحریر')
def stationery_handler(message):
    """
    هندلر نمایش لوازم التحریر
    """
    cid = message.chat.id
    show_product(cid, 102)
    show_product(cid, 103)

def show_product(cid, product_id):
    """
    تابع نمایش محصول
    """
    product_info = products.get(product_id)
    if product_info:
        caption = f"""
📦 {product_info['name']}

📝 توضیحات: {product_info['desc']}
💰 قیمت: {product_info['price']:,} تومان
📊 موجودی: {product_info['inv']} عدد
        """
        try:
            with open(product_info['file_id'], 'rb') as photo:
                bot.send_photo(cid, photo, caption=caption, reply_markup=get_product_markup(product_id, 1))
        except FileNotFoundError:
            bot.send_message(cid, caption, reply_markup=get_product_markup(product_id, 1))

@bot.message_handler(commands=['show_product'])
def command_show_product_handler(message):
    """
    هندلر نمایش محصول خاص
    """
    cid = message.chat.id
    
    # بررسی پارامتر
    if len(message.text.split()) < 2:
        # اگر پارامتر نداشت، لیست محصولات را نشان بده
        keyboard = InlineKeyboardMarkup()
        for product_id, product_info in products.items():
            keyboard.add(InlineKeyboardButton(
                product_info['name'], 
                callback_data=f'show_{product_id}'
            ))
        
        bot.send_message(cid, "🛍 لطفاً محصول مورد نظر را انتخاب کنید:", reply_markup=keyboard)
        return
    
    try:
        product_id = int(message.text.split()[1])
        show_product_detail(cid, product_id)
    except ValueError:
        bot.send_message(cid, "❌ کد محصول نامعتبر است. لطفاً یک عدد وارد کنید.")
    except Exception as e:
        bot.send_message(cid, f"❌ خطا در نمایش محصول: {e}")

@bot.message_handler(func=lambda message: message.text == '🛒 سبد خرید')
def cart_handler(message):
    """
    هندلر نمایش سبد خرید
    """
    cid = message.chat.id
    if cid not in shopping_cart or not shopping_cart[cid]:
        bot.send_message(cid, '🛒 سبد خرید شما خالی است. 😢')
        return
    
    text = '🛒 سبد خرید شما:\n\n'
    total_amount = 0
    for code, qty in shopping_cart[cid].items():
        product_info = products.get(code)
        if product_info:
            total = product_info['price'] * qty
            total_amount += total
            text += f"📦 {product_info['name']}\n   تعداد: {qty} × {product_info['price']} = {total} تومان\n\n"

    text += f"💰 جمع کل: {total_amount} تومان"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('💰 پرداخت', callback_data='checkout'))
    markup.add(InlineKeyboardButton('🗑 خالی کردن سبد', callback_data='clear_cart'))

    bot.send_message(cid, text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👤 پروفایل')
def profile_handler(message):
    """
    هندلر مدیریت پروفایل
    """
    cid = message.chat.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('📝 تنظیم نام', '📞 تنظیم تلفن')
    keyboard.add('🔙 بازگشت')
    bot.send_message(cid, '⚙️ تنظیمات پروفایل', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📝 تنظیم نام')
def set_name_handler(message):
    """
    هندلر تنظیم نام
    """
    cid = message.chat.id
    bot.send_message(cid, '👤 لطفاً نام کامل خود را وارد کنید:')
    user_steps[cid] = "set_name"

@bot.message_handler(func=lambda message: message.text == '📞 تنظیم تلفن')
def set_phone_handler(message):
    """
    هندلر تنظیم تلفن
    """
    cid = message.chat.id
    bot.send_message(cid, '📞 لطفاً شماره تلفن خود را وارد کنید:')
    user_steps[cid] = "set_phone"

@bot.message_handler(func=lambda message: message.text == '⚙️ تنظیمات')
def settings_handler(message):
    """
    هندلر تنظیمات ربات
    """
    cid = message.chat.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🌐 تنظیم زبان', '🔔 تنظیم اطلاع‌رسانی')
    keyboard.add('🔙 بازگشت')
    bot.send_message(cid, '⚙️ تنظیمات ربات', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📝 بازخورد')
def feedback_handler(message):
    """
    هندلر ارسال بازخورد
    """
    cid = message.chat.id
    bot.send_message(cid, '💬 لطفاً نظر یا پیشنهاد خود را وارد کنید:')
    user_steps[cid] = "waiting_feedback"

@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == "waiting_feedback")
def process_feedback(message):
    """
    هندلر پردازش بازخورد
    """
    cid = message.chat.id
    feedback_text = message.text
    
    # ذخیره بازخورد در فایل
    with open('feedback.txt', 'a', encoding='utf-8') as f:
        f.write(f"User: {cid}, Time: {datetime.datetime.now()}, Feedback: {feedback_text}\n")
    
    # ارسال پیام تأیید
    bot.send_message(cid, '✅ با تشکر از بازخورد شما! نظرتان ثبت شد.')
    
    # همچنین برای ادمین‌ها ارسال شود
    for admin_id in admins:
        try:
            bot.send_message(admin_id, f"📝 بازخورد جدید:\nاز کاربر: {cid}\nمتن: {feedback_text}")
        except:
            pass
    
    # حذف مرحله کاربر
    user_steps.pop(cid)

@bot.message_handler(func=lambda message: message.text == '🔙 بازگشت')
def back_handler(message):
    """
    هندلر بازگشت به منوی اصلی
    """
    send_welcome(message)

@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == "set_name")
def step_set_name_handler(message):
    """
    هندلر مرحله تنظیم نام
    """
    cid = message.chat.id
    name = message.text
    user_data.setdefault(cid, {'name': None, 'phone': None})
    user_data[cid]['name'] = name
    bot.send_message(cid, f'✅ نام شما با موفقیت ثبت شد: {name}')
    user_steps.pop(cid)

@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == "set_phone")
def step_set_phone_handler(message):
    """
    هندلر مرحله تنظیم تلفن
    """
    cid = message.chat.id
    phone = message.text
    user_data.setdefault(cid, {'name': None, 'phone': None})
    user_data[cid]['phone'] = phone
    bot.send_message(cid, f'✅ شماره تلفن شما با موفقیت ثبت شد: {phone}')
    user_steps.pop(cid)

@bot.message_handler(content_types=['photo'])
def content_photo_handler(message):
    """
    هندلر دریافت عکس
    """
    cid = message.chat.id
    if cid in admins and user_steps.get(cid) == 'AP':
        # هندلر افزودن محصول توسط ادمین
        file_id = message.photo[-1].file_id
        caption = message.caption
        if caption:
            try:
                product_info = caption.split('\n')
                name = product_info[0].split(':')[-1].strip()
                desc = product_info[1].split(':')[-1].strip()
                price = float(product_info[2].split(':')[-1].strip())
                inv = int(product_info[3].split(':')[-1].strip())
                category = product_info[4].split(':')[-1].strip()
                
                new_code = max(products.keys()) + 1 if products else 100
                products[new_code] = {
                    'name': name,
                    'desc': desc,
                    'price': price,
                    'inv': inv,
                    'file_id': file_id
                }
                bot.send_message(cid, f'✅ محصول با موفقیت اضافه شد!\nکد محصول: {new_code}')
                user_steps.pop(cid)
            except Exception as e:
                bot.send_message(cid, f'❌ خطا در پردازش اطلاعات محصول: {e}')
        else:
            bot.send_message(cid, '❌ لطفا caption را همراه عکس ارسال کنید')
    elif user_steps.get(cid) == 'PAY':
        # هندلر ارسال فیش پرداخت
        bot.send_message(cid, '✅ عکس فیش پرداخت دریافت شد. لطفاً منتظر تأیید باشید.')
        user_steps.pop(cid)

# هندلرهای اضافه شده برای دستورات تعریف شده

@bot.message_handler(commands=['send_document'])
def command_send_document_handler(message):
    """
    هندلر ارسال سند
    """
    cid = message.chat.id
    try:
        with open('sample.pdf', 'rb') as doc:
            bot.send_document(cid, doc, caption='این یک سند نمونه است')
    except FileNotFoundError:
        bot.send_message(cid, '❌ فایل سند یافت نشد')

@bot.message_handler(commands=['send_file'])
def command_send_file_handler(message):
    """
    هندلر ارسال فایل
    """
    cid = message.chat.id
    try:
        with open('sample.txt', 'rb') as file:
            bot.send_document(cid, file, caption='این یک فایل نمونه است')
    except FileNotFoundError:
        bot.send_message(cid, '❌ فایل یافت نشد')

@bot.message_handler(commands=['send_photo'])
def command_send_photo_handler(message):
    """
    هندلر ارسال عکس
    """
    cid = message.chat.id
    try:
        with open('sample.jpg', 'rb') as photo:
            bot.send_photo(cid, photo, caption='این یک عکس نمونه است')
    except FileNotFoundError:
        bot.send_message(cid, '❌ عکس یافت نشد')

@bot.message_handler(commands=['sample_inline'])
def command_sample_inline_handler(message):
    """
    هندلر نمونه اینلاین
    """
    cid = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('دکمه 1', callback_data='data_button_1'))
    markup.add(InlineKeyboardButton('دکمه 2', callback_data='data_button_2'))
    bot.send_message(cid, 'این یک نمونه صفحه کلید اینلاین است:', reply_markup=markup)

@bot.message_handler(commands=['edit_message'])
def command_edit_message_handler(message):
    """
    هندلر ویرایش پیام
    """
    cid = message.chat.id
    msg = bot.send_message(cid, 'این پیام ویرایش خواهد شد...')
    time.sleep(2)
    bot.edit_message_text('پیام ویرایش شد! ✅', cid, msg.message_id)

@bot.message_handler(commands=['delete_message'])
def command_delete_message_handler(message):
    """
    هندلر حذف پیام
    """
    cid = message.chat.id
    msg = bot.send_message(cid, 'این پیام حذف خواهد شد...')
    time.sleep(2)
    bot.delete_message(cid, msg.message_id)

@bot.message_handler(commands=['markdown_text'])
def command_markdown_text_handler(message):
    """
    هندلر متن مارک‌داون
    """
    cid = message.chat.id
    text = """
*متن Bold*
_متن Italic_
[لینک](https://t.me/Python_advance_FatiMa_Bot)
`کد`
```کد بلوک```
"""
    bot.send_message(cid, text, parse_mode='Markdown')

@bot.message_handler(commands=['invite_link'])
def command_invite_link_handler(message):
    """
    هندلر لینک دعوت
    """
    cid = message.chat.id
    bot.send_message(cid, 'لینک دعوت به ربات: https://t.me/Python_advance_FatiMa_Bot')

@bot.message_handler(commands=['get_contact'])
def command_get_contact_handler(message):
    """
    هندلر دریافت مخاطب
    """
    cid = message.chat.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📞 اشتراک گذاری شماره', request_contact=True))
    keyboard.add('🔙 بازگشت')
    bot.send_message(cid, 'لطفاً شماره تماس خود را اشتراک گذاری کنید:', reply_markup=keyboard)

@bot.message_handler(commands=['check_sub'])
def command_check_sub_handler(message):
    """
    هندلر بررسی عضویت در کانال
    """
    cid = message.chat.id
    try:
        member = bot.get_chat_member(CHANNEL_CID, cid)
        if member.status in ['member', 'administrator', 'creator']:
            bot.send_message(cid, '✅ شما در کانال عضو هستید!')
        else:
            bot.send_message(cid, '❌ شما در کانال عضو نیستید!')
    except Exception as e:
        bot.send_message(cid, f'❌ خطا در بررسی عضویت: {e}')

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    """
    هندلر دریافت مخاطب
    """
    cid = message.chat.id
    contact = message.contact
    bot.send_message(cid, f'✅ شماره {contact.phone_number} دریافت شد!', reply_markup=hideboard)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(message):
    """
    هندلر پیش‌فرض برای پیام‌های متنی
    """
    cid = message.chat.id
    text = message.text
    
    if text == '💰 پرداخت':
        # هندلر پرداخت از طریق دکمه
        if not shopping_cart.get(cid):
            bot.send_message(cid, 'سبد خرید شما خالی است')
            return
        
        total_amount = 0
        for code, qty in shopping_cart[cid].items():
            product_info = products.get(code)
            if product_info:
                total_amount += product_info['price'] * qty
        
        bot.send_message(cid, f'لطفا مبلغ {clean_text(total_amount)} تومان را به حساب زیر واریز و عکس فیش را ارسال کنید\n`6037991111111111`', parse_mode='MarkdownV2')
        user_steps[cid] = 'PAY'
    
    elif text == '🗑 خالی کردن سبد':
        # هندلر خالی کردن سبد خرید
        shopping_cart[cid] = {}
        bot.send_message(cid, '✅ سبد خرید با موفقیت خالی شد.')
    
    elif text == '🌐 تنظیم زبان':
        # هندلر تنظیم زبان
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('فارسی', 'English')
        keyboard.add('🔙 بازگشت')
        bot.send_message(cid, '🌐 زبان مورد نظر خود را انتخاب کنید:', reply_markup=keyboard)
    
    elif text == '🔔 تنظیم اطلاع‌رسانی':
        # هندلر تنظیم اطلاع‌رسانی
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('🔔 فعال', '🔕 غیرفعال')
        keyboard.add('🔙 بازگشت')
        bot.send_message(cid, '🔔 تنظیمات اطلاع‌رسانی:', reply_markup=keyboard)
    
    elif text in ['فارسی', 'English']:
        # هندلر تغییر زبان
        bot.send_message(cid, f'✅ زبان به {text} تغییر یافت.')
    
    elif text in ['🔔 فعال', '🔕 غیرفعال']:
        # هندلر تغییر وضعیت اطلاع‌رسانی
        status = 'فعال' if text == '🔔 فعال' else 'غیرفعال'
        bot.send_message(cid, f'✅ اطلاع‌رسانی {status} شد.')
    
    else:
        # هندلر پیام‌های ناشناخته
        bot.send_message(cid, "🤔 متوجه نشدم. لطفاً از منوی اصلی استفاده کنید.")

if __name__ == '__main__':
    print("🤖 ربات در حال اجرا است...")
    print("🛍 تعداد محصولات:", len(products))
    print("🔧 برای تنظیم کانال محصولات از دستور /set_channel استفاده کنید")
    print("🔍 برای بررسی کانال از دستور /get_channel_info استفاده کنید")
    bot.infinity_polling()
