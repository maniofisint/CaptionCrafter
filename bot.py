from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from generate_image import generate_news_image
import datetime
from PIL import Image

# Token بات
TOKEN = '8056950160:AAGIF7ColbOQH5wF6lhWC2HNAib5mb624K8'

# مراحل گفتگو
IMAGE, TITLE, CONTENT, SLOGAN, DATE, FUTURE_DAYS, EVENTS, FONT_SIZES = range(8)

# داده‌های کاربر
data = {}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("به ربات خوش آمدید! لطفاً تصویر خود را ارسال کنید.")
    return IMAGE

async def receive_image(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    await photo_file.download_to_drive('input_image.jpg')
    await update.message.reply_text("تصویر دریافت شد. لطفاً عنوان خبر را وارد کنید.")
    return TITLE

async def receive_title(update: Update, context: CallbackContext):
    data['title'] = update.message.text
    await update.message.reply_text("عالی! حالا متن اصلی خبر را وارد کنید.")
    return CONTENT

async def receive_content(update: Update, context: CallbackContext):
    data['content'] = update.message.text
    reply_markup = ReplyKeyboardMarkup([['استفاده از شعار پیش‌فرض', 'وارد کردن شعار دلخواه']], one_time_keyboard=True)
    await update.message.reply_text("آیا مایل به استفاده از شعار پیش‌فرض هستید یا می‌خواهید شعار دلخواه وارد کنید؟", reply_markup=reply_markup)
    return SLOGAN

async def receive_slogan(update: Update, context: CallbackContext):
    if update.message.text == 'استفاده از شعار پیش‌فرض':
        data['slogan'] = "منبع خبری مورد اعتماد شما"
    else:
        data['slogan'] = update.message.text
    reply_markup = ReplyKeyboardMarkup([['تاریخ امروز', 'انتخاب تاریخ آینده']], one_time_keyboard=True)
    await update.message.reply_text("شعار ذخیره شد. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)
    return DATE

async def receive_date(update: Update, context: CallbackContext):
    if update.message.text.lower() == "تاریخ امروز":
        data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        data['days_into_future'] = 0
        reply_markup = ReplyKeyboardMarkup([['بله', 'خیر']], one_time_keyboard=True)
        await update.message.reply_text("تاریخ امروز انتخاب شد. آیا مایل به اضافه کردن رویدادهای این روز هستید؟", reply_markup=reply_markup)
        return EVENTS
    else:
        await update.message.reply_text("چند روز در آینده را انتخاب می‌کنید؟ لطفاً عدد را وارد کنید:")
        return FUTURE_DAYS

async def receive_future_days(update: Update, context: CallbackContext):
    try:
        days = int(update.message.text)
        future_date = datetime.datetime.now() + datetime.timedelta(days=days)
        data['date'] = future_date.strftime('%Y-%m-%d')
        data['days_into_future'] = days
        reply_markup = ReplyKeyboardMarkup([['بله', 'خیر']], one_time_keyboard=True)
        await update.message.reply_text(f"تاریخ انتخاب شده: {data['date']}. آیا مایل به اضافه کردن رویدادهای این روز هستید؟", reply_markup=reply_markup)
        return EVENTS
    except ValueError:
        await update.message.reply_text("لطفاً یک عدد معتبر وارد کنید.")
        return FUTURE_DAYS

async def receive_events(update: Update, context: CallbackContext):
    if update.message.text == "خیر":
        data['todays_events'] = []
        reply_markup = ReplyKeyboardMarkup([['استفاده از اندازه پیش‌فرض', 'انتخاب اندازه دلخواه']], one_time_keyboard=True)
        await update.message.reply_text("آیا مایل به تغییر اندازه فونت‌ها هستید؟", reply_markup=reply_markup)
        return FONT_SIZES
    elif update.message.text == "بله":
        await update.message.reply_text("لطفاً رویدادهای روز را هر کدام در یک خط وارد کنید (حداکثر ۳ رویداد):")
        return EVENTS
    else:
        events = update.message.text.splitlines()[:3]
        data['todays_events'] = events
        reply_markup = ReplyKeyboardMarkup([['استفاده از اندازه پیش‌فرض', 'انتخاب اندازه دلخواه']], one_time_keyboard=True)
        await update.message.reply_text("رویدادها ذخیره شدند. آیا مایل به تغییر اندازه فونت‌ها هستید؟", reply_markup=reply_markup)
        return FONT_SIZES

async def receive_font_sizes(update: Update, context: CallbackContext):
    if update.message.text == "استفاده از اندازه پیش‌فرض":
        data['title_font_size'] = 40
        data['content_font_size'] = 60
        data['slogan_font_size'] = 25
    else:
        await update.message.reply_text("لطفاً اندازه فونت عنوان را وارد کنید:")
        return FONT_SIZES
    await generate_and_send_image(update, context)
    return ConversationHandler.END

async def receive_custom_font_sizes(update: Update, context: CallbackContext):
    try:
        size = int(update.message.text)
        if 'title_font_size' not in data:
            data['title_font_size'] = size
            await update.message.reply_text("لطفاً اندازه فونت محتوای اصلی را وارد کنید:")
        elif 'content_font_size' not in data:
            data['content_font_size'] = size
            await update.message.reply_text("لطفاً اندازه فونت شعار را وارد کنید:")
        else:
            data['slogan_font_size'] = size
            await generate_and_send_image(update, context)
            return ConversationHandler.END
        return FONT_SIZES
    except ValueError:
        await update.message.reply_text("لطفاً یک عدد معتبر وارد کنید.")
        return FONT_SIZES


async def generate_and_send_image(update: Update, context: CallbackContext):
    # Generate the image
    generate_news_image(
        output_path='final_image.png',  # Use PNG for intermediate saving
        title=data['title'],
        main_content=data['content'],
        slogan=data['slogan'],
        user_image_path='input_image.jpg',
        todays_events="\n".join(data.get('todays_events', [])),
        days_into_future=data['days_into_future'],
        title_font_size=data.get('title_font_size', 40),
        content_font_size=data.get('content_font_size', 60),
        slogan_font_size=data.get('slogan_font_size', 25)
    )
    
    # Open the generated image
    img = Image.open('final_image.png')
    
    # Convert to RGB if necessary
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Save as final JPEG image
    img.save('final_image.jpg', 'JPEG')
    
    # Send the image
    await update.message.reply_text("تصویر خبر شما ایجاد شد!")
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('final_image.jpg', 'rb'))

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("عملیات لغو شد. برای شروع دوباره /start را ارسال کنید.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            IMAGE: [MessageHandler(filters.PHOTO, receive_image)],
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_content)],
            SLOGAN: [
                MessageHandler(filters.TEXT & filters.Regex('^استفاده از شعار پیش‌فرض$'), receive_slogan),
                MessageHandler(filters.TEXT & filters.Regex('^وارد کردن شعار دلخواه$'), receive_slogan),
            ],
            DATE: [
                MessageHandler(filters.TEXT & filters.Regex("^تاریخ امروز$"), receive_date),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_future_days)
            ],
            FUTURE_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_future_days)],
            EVENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_events)],
            FONT_SIZES: [
                MessageHandler(filters.TEXT & filters.Regex('^استفاده از اندازه پیش‌فرض$'), receive_font_sizes),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_custom_font_sizes)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
