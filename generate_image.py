from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from khayyam import JalaliDatetime
import arabic_reshaper
from convertdate import islamic
from bidi.algorithm import get_display


def hijri_date_from_gregorian(gregorian_date):
    """
    Convert a Gregorian date to a Hijri (Islamic) date.

    Args:
        gregorian_date (datetime): The Gregorian date to convert.

    Returns:
        str: The Hijri date in the format "day month year" with month names in Arabic.
    """
    year, month, day = islamic.from_gregorian(
        gregorian_date.year, gregorian_date.month, gregorian_date.day
    )
    hijri_months = [
        "محرم", "صفر", "ربیع‌الاول", "ربیع‌الثانی", "جمادی‌الاول",
        "جمادی‌الثانی", "رجب", "شعبان", "رمضان", "شوال", "ذی‌القعده", "ذی‌الحجه"
    ]
    return f"{day} {hijri_months[month - 1]} {year}"

def generate_news_image(
    output_path,
    title,
    main_content,
    slogan,
    user_image_path,
    todays_events="",
    days_into_future=0,
    title_font_size=40,
    content_font_size=24,
    slogan_font_size=20
):
    """
    Generate a news image with customized content, including title, main text, slogan,
    events, and dynamic date formats (Shamsi, Miladi, Hejri).

    Args:
        output_path (str): The file path to save the generated image.
        title (str): The title text to display in the image.
        main_content (str): The main content text for the image.
        slogan (str): A slogan to display in the image.
        user_image_path (str): The path to the user's image to embed in the news image.
        todays_events (str): Multi-line string of events for the day. Each line is an event.
        days_into_future (int): Number of days into the future to calculate the date.
        title_font_size (int): Font size for the title.
        content_font_size (int): Font size for the main content.
        slogan_font_size (int): Font size for the slogan.

    Returns:
        None: Saves the generated image to the specified output path.
    """
    event_font_size=14
    weekday_font_size=20
    shamsi_day_font_size=30

    # Select the appropriate base image based on the number of events
    # The base image is selected based on the number of events (up to 3) to match the design layout.
    event_count = len(todays_events.splitlines()) if todays_events.strip() else 0
    base_image_path = f"Base{min(event_count, 3)}.png"
    base_image = Image.open(base_image_path)
    draw = ImageDraw.Draw(base_image)

    # Load user image
    user_image = Image.open(user_image_path)
    user_image = user_image.resize((680, 460))  # Resize the user image to fit the base image

    # Paste user image onto base image
    user_image_position = (200, 540)  # Adjust position as needed
    base_image.paste(user_image, user_image_position)

    # Load fonts
    title_font = ImageFont.truetype("BNazanin.ttf", title_font_size)
    content_font = ImageFont.truetype("Ray-ExtraBlack.ttf", content_font_size)
    slogan_font = ImageFont.truetype("A Nafis.ttf", slogan_font_size)
    event_font = ImageFont.truetype("A Nafis.ttf", event_font_size)
    weekday_font = ImageFont.truetype("A Nafis.ttf", weekday_font_size)
    shamsi_day_font = ImageFont.truetype("A Nafis.ttf", shamsi_day_font_size)
    miladi_date_font = ImageFont.truetype("Poppins-Regular.ttf", 14)

    # Function to reshape and reorder Farsi text
    def prepare_farsi_text(text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

    # Prepare dates
    future_date = datetime.now() + timedelta(days=days_into_future)
    miladi_date = future_date.strftime("%d %B %Y")

    hejri_date = hijri_date_from_gregorian(future_date)
    hejri_date = prepare_farsi_text(hejri_date)

    shamsi = JalaliDatetime(future_date)
    shamsi_day = shamsi.strftime("%d")
    shamsi_month_year = shamsi.strftime("%B %Y")
    weekday = shamsi.strftime("%A")

    # Default positions
    date_positions =  {
        "weekday": (190, 60),  # Position of the day of the week in Shamsi calendar
        "shamsi_day": (190, 90),  # Position of the day number in Shamsi calendar
        "shamsi_month_year": (190, 130),  # Position of the month and year in Shamsi calendar
        "miladi": (70, 160),  # Position of the Gregorian date
        "hejri": (190, 163),  # Position of the Hijri (Islamic) date
    }

    # Draw dates
    # Draw day of the week
    # Draw weekday (center-aligned)
    weekday_text = prepare_farsi_text(weekday)
    weekday_bbox = draw.textbbox((0, 0), weekday_text, font=weekday_font)
    weekday_width = weekday_bbox[2] - weekday_bbox[0]
    weekday_x = date_positions["weekday"][0] - (weekday_width // 2)  # Center-align
    draw.text((weekday_x, date_positions["weekday"][1]), weekday_text, font=weekday_font, fill="black")

    # Draw Shamsi day (center-aligned)
    shamsi_day_text = prepare_farsi_text(shamsi_day)
    shamsi_day_bbox = draw.textbbox((0, 0), shamsi_day_text, font=shamsi_day_font)
    shamsi_day_width = shamsi_day_bbox[2] - shamsi_day_bbox[0]
    shamsi_day_x = date_positions["shamsi_day"][0] - (shamsi_day_width // 2)  # Center-align
    draw.text((shamsi_day_x, date_positions["shamsi_day"][1]), shamsi_day_text, font=shamsi_day_font, fill="black")

    # Draw Shamsi month and year (center-aligned)
    shamsi_month_year_text = prepare_farsi_text(shamsi_month_year)
    shamsi_month_year_bbox = draw.textbbox((0, 0), shamsi_month_year_text, font=event_font)
    shamsi_month_year_width = shamsi_month_year_bbox[2] - shamsi_month_year_bbox[0]
    shamsi_month_year_x = date_positions["shamsi_month_year"][0] - (shamsi_month_year_width // 2)  # Center-align
    draw.text((shamsi_month_year_x, date_positions["shamsi_month_year"][1]), shamsi_month_year_text, font=event_font, fill="black")

    # Draw Miladi date (center-aligned)
    miladi_text = miladi_date
    miladi_bbox = draw.textbbox((0, 0), miladi_text, font=miladi_date_font)
    miladi_width = miladi_bbox[2] - miladi_bbox[0]
    miladi_x = date_positions["miladi"][0] - (miladi_width // 2)  # Center-align
    draw.text((miladi_x, date_positions["miladi"][1]), miladi_text, font=miladi_date_font, fill="black")

    
    # Draw Hejri date (center-aligned)
    hejri_text = hejri_date
    hejri_bbox = draw.textbbox((0, 0), hejri_text, font=event_font)
    hejri_width = hejri_bbox[2] - hejri_bbox[0]
    hejri_x = date_positions["hejri"][0] - (hejri_width // 2)  # Center-align
    draw.text((hejri_x, date_positions["hejri"][1]), hejri_text, font=event_font, fill="black")
        
    # Prepare Farsi text
    title = prepare_farsi_text(title)
    # main_content = prepare_farsi_text(main_content)
    # slogan = prepare_farsi_text(slogan)

    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_position = ((base_image.size[0] - title_width) // 2, 230)
    draw.text(title_position, title, font=title_font, fill="black")

    # Draw main content
    box_width = 980 - 100
    y_offset = 285
    current_line = ""
    lines = []

    for word in main_content.split():
        test_line = f"{current_line} {word}".strip()
        test_bbox = draw.textbbox((0, 0), test_line, font=content_font)
        test_width = test_bbox[2] - test_bbox[0]
        if test_width <= box_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    for line in lines:
        reshaped_line = prepare_farsi_text(line)
        line_bbox = draw.textbbox((0, 0), reshaped_line, font=content_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]
        x_position = 100 + (box_width - line_width) // 2
        draw.text((x_position, y_offset), reshaped_line, font=content_font, fill="black")
        y_offset += line_height
        if y_offset > 400:
            break

    # Draw slogan
    slogan_box_width = 505 - 270
    slogan_y_offset = 95
    current_slogan_line = ""
    slogan_lines = []

    for word in slogan.split():
        test_line = f"{current_slogan_line} {word}".strip()
        test_bbox = draw.textbbox((0, 0), test_line, font=slogan_font)
        test_width = test_bbox[2] - test_bbox[0]
        if test_width <= slogan_box_width:
            current_slogan_line = test_line
        else:
            slogan_lines.append(current_slogan_line)
            current_slogan_line = word
    if current_slogan_line:
        slogan_lines.append(current_slogan_line)

    for line in slogan_lines:
        reshaped_line = prepare_farsi_text(line)
        line_bbox = draw.textbbox((0, 0), reshaped_line, font=slogan_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]
        x_position = 270 + (slogan_box_width - line_width) // 2
        draw.text((x_position, slogan_y_offset), reshaped_line, font=slogan_font, fill=(4, 18, 66))  # Red color
        slogan_y_offset += line_height
        if slogan_y_offset > 130:
            break

    # Draw today's events
    if todays_events.strip():
        custom_positions = {
            0: [],  # Base0 positions
            1: [(108, 101)],  # Base1 positions
            2: [(108, 101), (108, 119)],  # Base2 positions
            3: [(108, 89), (108, 108), (108, 125)]   # Base3 positions
        }
        positions = custom_positions.get(event_count, [(50, 420)])

        for i, event in enumerate(todays_events.splitlines()):
            reshaped_event = prepare_farsi_text(event)
            line_bbox = draw.textbbox((0, 0), reshaped_event, font=event_font)
            event_width = line_bbox[2] - line_bbox[0]
            x_position, y_position = positions[i]
            adjusted_x_position = x_position - event_width  # Shift left for RTL alignment
            draw.text((adjusted_x_position, y_position), reshaped_event, font=event_font, fill="black")

    # Save the resulting image
    base_image.save(output_path)

# Example usage
generate_news_image(
    output_path="news_output.png",
    title="بازدهی ۴۰ درصدی گواهی سپرده سکه از ابتدای سال:",
    main_content="نوسان سکه رفاه در حوالی قله و چشم انداز آینده بازار، تحلیلگران رشد بیشتری را پیش بینی می‌کنند.",
    slogan="اکنون زمانِ اقتصاد است.",
    user_image_path="input_image.jpg",
    # todays_events="",
    # todays_events="رویداد ۱: افزایش نرخ ارز",
    # todays_events="رویداد ۱: افزایش نرخ ارز\nرویداد ۲: کاهش ارزش سهام",
    todays_events=" افزایش نرخ ارز\n کاهش ارزش سهام\n افزایش نرخ طلا",
    days_into_future=0,
    title_font_size=40,
    content_font_size=50,
    slogan_font_size=25,
)
