import logging  # Import the logging module to log events for debugging and tracking.
from telegram import Update, ReplyKeyboardMarkup  # Import necessary Telegram API classes.
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler  # Import Telegram bot handlers and context.
from generate_image import generate_news_image  # Import the custom image generation function.
import datetime  # Import datetime for date and time manipulation.
from PIL import Image
import telegram

TOKEN = '8056950160:AAGIF7ColbOQH5wF6lhWC2HNAib5mb624K8'  # Telegram bot token.

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define log format.
    level=logging.INFO  # Set log level to INFO to capture detailed logs.
)
logger = logging.getLogger(__name__)  # Create a logger instance.

# Token بات

# مراحل گفتگو
AUTH, IMAGE, TITLE, CONTENT, SLOGAN, SLOGAN_CUSTOM, DATE, FUTURE_DAYS, EVENTS, FONT_SIZES, CUSTOM_FONT_SIZES = range(11)  # Conversation steps.

# داده‌های کاربر
data = {}  # Dictionary to store user-provided data during the conversation.

# Timeout duration (in seconds)
TIMEOUT = 300  # Define conversation timeout duration.

PASSWORD = "securepassword"  # Set your desired password
AUTHORIZED_USERS = set()  # Set to store authorized user IDs


async def start(update: Update, context: CallbackContext):
    logger.info("User started the bot.")  # Log the start of the conversation.
    context.user_data.clear()  # Clear any previous user data.
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("به ربات خوش آمدید! لطفاً رمز بات را ارسال کنید.") 
        return AUTH
    await update.message.reply_text("به ربات خوش آمدید! لطفاً تصویر خود را ارسال کنید.")  # Welcome message to the user.
    return IMAGE  # Move to the IMAGE step.

async def autherize(update: Update, context: CallbackContext):
    user_id = update.effective_user.id  # Get the user's unique ID.
    password = update.message.text  # Get the user's input.

    if not password:
        logger.warning("Expected text for password but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یک پس‌وورد ارسال کنید.")  # Prompt the user to send text.
        return AUTH  # Stay in the AUTH step.

    logger.info("Password received.")  # Log that a password was received.

    # Check if the password matches
    if password == PASSWORD:
        AUTHORIZED_USERS.add(user_id)  # Add the user ID to the authorized set.
        logger.info(f"User authorized: {user_id}")  # Log the authorization event.
        await update.message.reply_text(
            "دسترسی به بات مجاز شد. لطفاً جهت استفاده از ربات /start را ارسال کنید."
        )  # Notify the user of successful authorization.
        return ConversationHandler.END  # End the current conversation.

    # Incorrect password case
    logger.info(f"Incorrect password entered by user: {user_id}.")  # Log the failed attempt.
    await update.message.reply_text("پس‌وورد ارسالی نادرست است. لطفاً دوباره تلاش کنید.")  # Notify the user.
    return AUTH  # Stay in the AUTH step.


async def receive_image(update: Update, context: CallbackContext):
    if not update.message.photo:  # Check if the message contains a photo.
        logger.warning("Expected an image but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یک تصویر ارسال کنید.")  # Prompt the user to send an image.
        return IMAGE  # Stay in the IMAGE step.

    logger.info("Image received.")  # Log that the image was received.
    photo = update.message.photo[-1]  # Get the highest-resolution photo from the message.
    photo_file = await photo.get_file()  # Fetch the photo file.
    await photo_file.download_to_drive('input_image.jpg')  # Save the photo locally.
    await update.message.reply_text("تصویر دریافت شد. لطفاً عنوان خبر را وارد کنید.")  # Prompt for the news title.
    return TITLE  # Move to the TITLE step.

async def receive_title(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for title but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یک عنوان ارسال کنید.")  # Prompt the user to send text.
        return TITLE  # Stay in the TITLE step.

    data['title'] = update.message.text  # Store the title in the data dictionary.
    logger.info(f"Title received: {data['title']}")  # Log the received title.
    await update.message.reply_text("عالی! حالا متن اصلی خبر را وارد کنید.")  # Prompt for the main news content.
    return CONTENT  # Move to the CONTENT step.

async def receive_content(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for content but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً متن خبر را ارسال کنید.")  # Prompt the user to send text.
        return CONTENT  # Stay in the CONTENT step.

    data['content'] = update.message.text  # Store the content in the data dictionary.
    logger.info(f"Content received: {data['content']}")  # Log the received content.
    reply_markup = ReplyKeyboardMarkup([['استفاده از شعار پیش‌فرض', 'وارد کردن شعار دلخواه']], one_time_keyboard=True)  # Create a keyboard for slogan selection.
    await update.message.reply_text("آیا مایل به استفاده از شعار پیش‌فرض هستید یا می‌خواهید شعار دلخواه وارد کنید؟", reply_markup=reply_markup)  # Prompt for slogan selection.
    return SLOGAN  # Move to the SLOGAN step.

async def receive_slogan(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for slogan but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یک شعار ارسال کنید.")  # Prompt the user to send text.
        return SLOGAN  # Stay in the SLOGAN step.

    if update.message.text == 'استفاده از شعار پیش‌فرض':  # Check if the user chose the default slogan.
        data['slogan'] = "اکنون زمانِ اقتصاد است!"  # Set the default slogan.
        logger.info("Default slogan selected.")  # Log the default slogan choice.
        reply_markup = ReplyKeyboardMarkup([['تاریخ امروز', 'انتخاب تاریخ آینده']], one_time_keyboard=True)  # Create a keyboard for date selection.
        await update.message.reply_text("شعار ذخیره شد. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)  # Prompt for date selection.
        return DATE  # Move to the DATE step.
    else:
        # If the user selects a custom slogan, prompt them to enter it.
        await update.message.reply_text("لطفاً شعار دلخواه خود را وارد کنید:")  
        return SLOGAN_CUSTOM  # Transition to the SLOGAN_CUSTOM step.

async def receive_custom_slogan(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for custom slogan but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یک شعار ارسال کنید.")  # Prompt the user to send text.
        return SLOGAN_CUSTOM  # Stay in the SLOGAN_CUSTOM step.

    # Save the custom slogan provided by the user.
    data['slogan'] = update.message.text
    logger.info(f"Custom slogan received: {data['slogan']}")  # Log the received custom slogan.
    reply_markup = ReplyKeyboardMarkup([['تاریخ امروز', 'انتخاب تاریخ آینده']], one_time_keyboard=True)  # Create a keyboard for date selection.
    await update.message.reply_text("شعار ذخیره شد. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)  # Prompt for date selection.
    return DATE  # Move to the DATE step.

async def receive_date(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for date selection but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید.")  # Prompt the user to select a date.
        return DATE  # Stay in the DATE step.

    if update.message.text.lower() == "تاریخ امروز":  # Check if the user selected today's date.
        data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')  # Store today's date.
        data['days_into_future'] = 0  # Set days into the future to 0.
        logger.info("Today's date selected.")  # Log the selection.
        reply_markup = ReplyKeyboardMarkup([['بله', 'خیر']], one_time_keyboard=True)  # Create a keyboard for event addition.
        await update.message.reply_text("تاریخ امروز انتخاب شد. آیا مایل به اضافه کردن رویدادهای این روز هستید؟", reply_markup=reply_markup)  # Prompt for event addition.
        return EVENTS  # Move to the EVENTS step.
    else:
        logger.info("User chose a future date.")  # Log the selection of a future date.
        await update.message.reply_text("چند روز در آینده را انتخاب می‌کنید؟ لطفاً عدد را وارد کنید:")  # Prompt for the number of future days.
        return FUTURE_DAYS  # Move to the FUTURE_DAYS step.

async def receive_future_days(update: Update, context: CallbackContext):
    try:
        days = int(update.message.text)  # Parse the number of days from the user's input.
        future_date = datetime.datetime.now() + datetime.timedelta(days=days)  # Calculate the future date.
        data['date'] = future_date.strftime('%Y-%m-%d')  # Store the future date.
        data['days_into_future'] = days  # Store the number of days into the future.
        logger.info(f"Future date selected: {data['date']} ({days} days into the future)")  # Log the selected future date.
        reply_markup = ReplyKeyboardMarkup([['بله', 'خیر']], one_time_keyboard=True)  # Create a keyboard for event addition.
        await update.message.reply_text(f"تاریخ انتخاب شده: {data['date']}. آیا مایل به اضافه کردن رویدادهای این روز هستید؟", reply_markup=reply_markup)  # Prompt for event addition.
        return EVENTS  # Move to the EVENTS step.
    except ValueError:
        logger.warning("Invalid number of days entered.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یک عدد معتبر وارد کنید.")  # Prompt the user to enter a valid number.
        return FUTURE_DAYS  # Stay in the FUTURE_DAYS step.

async def receive_events(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for events but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً بله یا خیر را انتخاب کنید.")  # Prompt the user to choose yes or no.
        return EVENTS  # Stay in the EVENTS step.

    if update.message.text == "خیر":  # Check if the user chose not to add events.
        data['todays_events'] = []  # Store an empty list for events.
        logger.info("No events added.")  # Log the selection.
        reply_markup = ReplyKeyboardMarkup([['استفاده از اندازه پیش‌فرض', 'انتخاب اندازه دلخواه']], one_time_keyboard=True)  # Create a keyboard for font size selection.
        await update.message.reply_text("آیا مایل به تغییر اندازه فونت‌ها هستید؟", reply_markup=reply_markup)  # Prompt for font size selection.
        return FONT_SIZES  # Move to the FONT_SIZES step.
    elif update.message.text == "بله":  # Check if the user chose to add events.
        logger.info("User opted to add events.")  # Log the selection.
        await update.message.reply_text("لطفاً رویدادهای روز را هر کدام در یک خط وارد کنید (حداکثر ۳ رویداد):")  # Prompt for event details.
        return EVENTS  # Stay in the EVENTS step.
    else:
        events = update.message.text.splitlines()[:3]  # Split the input into lines and limit to 3 events.
        data['todays_events'] = events  # Store the events.
        logger.info(f"Events received: {events}")  # Log the received events.
        reply_markup = ReplyKeyboardMarkup([['استفاده از اندازه پیش‌فرض', 'انتخاب اندازه دلخواه']], one_time_keyboard=True)  # Create a keyboard for font size selection.
        await update.message.reply_text("رویدادها ذخیره شدند. آیا مایل به تغییر اندازه فونت‌ها هستید؟", reply_markup=reply_markup)  # Prompt for font size selection.
        return FONT_SIZES  # Move to the FONT_SIZES step.

async def receive_font_sizes(update: Update, context: CallbackContext):
    if not update.message.text:  # Check if the message contains text.
        logger.warning("Expected text for font size selection but received something else.")  # Log a warning for invalid input.
        await update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید.")  # Prompt the user to choose an option.
        return FONT_SIZES  # Stay in the FONT_SIZES step.

    if update.message.text == "استفاده از اندازه پیش‌فرض":  # Check if the user chose default font sizes.
        data['title_font_size'] = 40  # Set default title font size.
        data['content_font_size'] = 50  # Set default content font size.
        data['slogan_font_size'] = 25  # Set default slogan font size.
        logger.info("Default font sizes selected.")  # Log the selection.
        await generate_and_send_image(update, context)  # Generate and send the image.
        return ConversationHandler.END  # End the conversation.

    elif update.message.text == 'انتخاب اندازه دلخواه':
        logger.info("User opted to change font sizes.")  # Log the selection.
        await update.message.reply_text("لطفاً اندازه فونت تیتر، متن اصلی و شعار را هر کدام در یک خط وارد کنید. (مقدار پیش‌فرض اندازه فونت تیتر برابر با ۴۰، متن اصلی ۵۰و شعار ۲۵ است.)")  # Prompt for custom font sizes.
        return FONT_SIZES  # Stay in the FONT_SIZES step.

    else:
        try:
            font_sizes = list(map(int, update.message.text.splitlines()[:3]))  # Parse font sizes as integers.
            data['title_font_size'] = font_sizes[0]  # Store title font size.
            data['content_font_size'] = font_sizes[1]  # Store content font size.
            data['slogan_font_size'] = font_sizes[2]  # Store slogan font size.
            logger.info(f"Custom font sizes received: {font_sizes}")  # Log the custom font sizes.
            await generate_and_send_image(update, context)  # Generate and send the image.
            return ConversationHandler.END  # End the conversation.
        except (ValueError, IndexError):
            logger.warning("Invalid font size input.")  # Log invalid input.
            await update.message.reply_text("لطفاً سه عدد معتبر وارد کنید (هر عدد در یک خط).")  # Prompt the user to re-enter.
            return FONT_SIZES  # Stay in the FONT_SIZES step.


async def generate_and_send_image(update: Update, context: CallbackContext):
    logger.info("Generating news image.")  # Log the start of image generation.
    generate_news_image(
        output_path='final_image.png',  # Output file path.
        title=data['title'],  # News title.
        main_content=data['content'],  # News content.
        slogan=data['slogan'],  # Slogan.
        user_image_path='input_image.jpg',  # User-provided image path.
        todays_events="\n".join(data.get('todays_events', [])),  # Events of the day.
        days_into_future=data['days_into_future'],  # Number of days into the future.
        title_font_size=data.get('title_font_size', 40),  # Title font size.
        content_font_size=data.get('content_font_size', 50),  # Content font size.
        slogan_font_size=data.get('slogan_font_size', 25)  # Slogan font size.
    )
    # Open the generated image
    img = Image.open('final_image.png')
    
    # Convert to RGB if necessary
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Save as final JPEG image
    img.save('final_image.jpg', 'JPEG')

    await update.message.reply_text("تصویر خبر شما ایجاد شد!درحال ارسال...")  # Notify the user that the image is ready.

    for attempt in range(3):  # Retry up to 3 times
        try:
            # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('final_image.jpg', 'rb'))
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open('final_image.jpg', 'rb'))
            logger.info("News image sent successfully.")
            break
        except telegram.error.TimedOut:
            logger.warning(f"Attempt {attempt + 1}: Timeout while sending image.")
            if attempt == 2:  # If all attempts fail
                await update.message.reply_text("خطا در ارسال تصویر. لطفاً دوباره تلاش کنید.")

async def timeout_handler(update: Update, context: CallbackContext):
    """Notify the user when the conversation times out."""
    logger.warning("Conversation timed out.")
    await update.message.reply_text("زمان گفتگو به پایان رسیده است. لطفاً دوباره /start را ارسال کنید.")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    logger.info("User canceled the operation.")  # Log the cancellation.
    await update.message.reply_text("عملیات لغو شد. برای شروع دوباره /start را ارسال کنید.")  # Notify the user about the cancellation.
    return ConversationHandler.END  # End the conversation.



def main():
    application = Application.builder().token(TOKEN).http_version("1.1").build()
    job_queue = application.job_queue
    job_queue.start()

    # Conversation handler with the AUTH step included
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, autherize)],  # Authorization step
            IMAGE: [MessageHandler(filters.PHOTO, receive_image)],  # Handle images
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],  # Handle titles
            CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_content)],  # Handle content
            SLOGAN: [
                MessageHandler(filters.TEXT & filters.Regex('^استفاده از شعار پیش‌فرض$'), receive_slogan),
                MessageHandler(filters.TEXT & filters.Regex('^وارد کردن شعار دلخواه$'), receive_slogan),
            ],  # Handle slogan options
            SLOGAN_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_custom_slogan)],  # Custom slogan
            DATE: [
                MessageHandler(filters.TEXT & filters.Regex("^تاریخ امروز$"), receive_date),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_future_days),
            ],  # Handle date inputs
            FUTURE_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_future_days)],  # Future days
            EVENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_events)],  # Events
            FONT_SIZES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_font_sizes)],  # Font sizes
        },
        fallbacks=[
            CommandHandler('cancel', cancel),  # Cancel handler
            MessageHandler(filters.ALL, timeout_handler),  # Timeout fallback
        ],
        conversation_timeout=TIMEOUT,  # Set conversation timeout
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Log and start polling
    logger.info("Bot started.")
    application.run_polling()

if __name__ == '__main__':
    main()
