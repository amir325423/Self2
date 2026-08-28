from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters
import logging

TOKEN = "8887093613:AAFkqOtkanU7E0qM4ArE8iQeOTBX4EtA9vU" # توکن ربات هلپر

# توجه برای اینکه هلپر کار کنه بابد بخش اینلاین مود ربات رو توی بات فادر فعال کنید

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

HELP_TEXTS = {
    "time": """
⏰ <b>مدیریت تایم</b>

<b>دستورات قابل کپی:</b>
<code>تایم روشن</code>
<code>تایم خاموش</code>

<b>کاربرد:</b>
نمایش زمان کنار نام کاربری
آپدیت خودکار هر دقیقه
فونت‌های مختلف برای زمان

<b>فونت‌های موجود:</b>
𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗 - فونت 1
𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵 - فونت 2  
０１２３４５６７８９ - فونت 3
𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫 - فونت 4
𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡 - فونت 5
0҉1҉2҉3҉4҉5҉6҉7҉8҉9҉ - فونت 6
""",

    "instagram": """
📥 <b>دانلودر اینستاگرام</b>

<b>دستور قابل کپی:</b>
<code>اینستا لینک_پست</code>

<b>مثال‌ها:</b>
<code>اینستا https://www.instagram.com/reel/DOkym3fCFqg/</code>
<code>اینستا https://www.instagram.com/p/CzuF4KQqJ7q/</code>
<code>اینستا https://www.instagram.com/tv/Cxxxxxxxx/</code>

<b>کاربرد:</b>
• دانلود پست‌های اینستاگرام
• دانلود ریل‌ ها و ویدیو ها
• دانلود عکس‌های پست

<b>قابلیت‌ها:</b>
✅ دانلود با کیفیت اصلی
✅ نمایش توضیحات پست
✅ نمایش اطلاعات کاربر
✅ آپلود در همان چت
""",

    "id": """
🆔 <b>سیستم آیدی پیشرفته</b>

<b>دستور قابل کپی:</b>
<code>ایدی</code>

<b>دو حالت استفاده:</b>

1️⃣ <b>بدون ریپلای:</b>
<code>ایدی</code>
• نمایش اطلاعات خودتان
• نمایش اطلاعات چت فعلی
• نمایش آیدی عددی

2️⃣ <b>با ریپلای:</b>
<code>ایدی</code> (روی پیام کاربر ریپلای)
• نمایش اطلاعات کامل کاربر
• نمایش گروه‌های مشترک  
• نمایش آیدی و یوزرنیم

<b>اطلاعات نمایش داده شده:</b>
✅ آیدی عددی کاربر
✅ یوزرنیم و نام کامل
✅ وضعیت پریمیوم
✅ تعداد عکس‌های پروفایل
✅ آیدی چت و عنوان
✅ تعداد اعضا (در گروه)
✅ گروه‌های مشترک (در صورت وجود)

<b>مثال خروجی:</b>
• اطلاعات شما + چت فعلی
• یا اطلاعات کاربر ریپلای شده
""",

    "photo": """
📸 <b>ذخیره عکس تایمدار</b>

<b>دستور قابل کپی:</b>
<code>عکس سیو</code> (ریپلای روی عکس)

<b>کاربرد:</b>
ذخیره دستی عکس‌های تایمدار
ارسال اطلاعات کامل کاربر

<b>نکته:</b>
فقط روی عکس‌های تایمدار کار می‌کند
عکس معمولی قابل ذخیره نیست
""",

    "backup": """
💾 <b>پشتیبان‌گیری</b>

<b>دستور قابل کپی:</b>
<code>سیو @یوزرنیم</code>

<b>مثال:</b>
<code>سیو @username</code>

<b>کاربرد:</b>
ذخیره تاریخچه چت در فایل متنی
ارسال فایل به پیام‌های ذخیره شده
""",

    "font": """
🔤 <b>مدیریت فونت</b>

<b>دستورات قابل کپی:</b>
<code>لیست فونت</code>
<code>تنظیم فونت 1</code> تا <code>تنظیم فونت 6</code>

<b>کاربرد:</b>
تغییر فونت نمایش زمان
پیش‌نمایش فونت‌های مختلف
اعمال فونت روی زمان به صورت زنده
""",

    "price": """
💱 <b>قیمت ارز</b>

<b>دستور قابل کپی:</b>
<code>قیمت ارز</code>

<b>مثال‌ها:</b>
<code>قیمت BTC</code>
<code>قیمت ETH</code>
<code>قیمت TON</code>

<b>کاربرد:</b>
نمایش قیمت لحظه‌ای ارزهای دیجیتال
نمایش قیمت تومانی و دلاری
نمایش تغییرات 24 ساعته
میتوانید اسم ارزو رو به فارسی بزارید
""",

    "spam": """
🔁 <b>ارسال اسپم</b>

<b>دستور قابل کپی:</b>
<code>اسپم تعداد متن</code>

<b>مثال‌ها:</b>
<code>اسپم 10 سلام</code>
<code>اسپم 5 تست</code>

<b>کاربرد:</b>
ارسال پیام تکراری
حداکثر 50 پیام در یک دستور
قابلیت ریپلای روی پیام
""",

    "format": """
🎨 <b>سیستم فرمت خودکار HTML</b>

<b>دستورات قابل کپی:</b>
<code>فرمت بولد روشن</code>
<code>فرمت بولد خاموش</code>
<code>فرمت ایتالیک روشن</code>
<code>فرمت ایتالیک خاموش</code>
<code>فرمت زیرخط روشن</code>
<code>فرمت زیرخط خاموش</code>
<code>فرمت خط‌خورده روشن</code>
<code>فرمت خط‌خورده خاموش</code>
<code>فرمت اسپویلر روشن</code>
<code>فرمت اسپویلر خاموش</code>
<code>فرمت کد روشن</code>
<code>فرمت کد خاموش</code>
<code>فرمت پیش‌فرمت روشن</code>
<code>فرمت پیش‌فرمت خاموش</code>
<code>فرمت نقل‌قول روشن</code>
<code>فرمت نقل‌قول خاموش</code>
<code>فرمت وضعیت</code>
<code>فرمت ریست</code>

<b>کاربرد:</b>
تبدیل خودکار پیام‌ ها به فرمت‌ های مختلف
پشتیبانی از تمام تگ‌های HTML تلگرام
امکان استفاده همزمان از چندین فرمت

<b>فرمت‌های پشتیبانی شده:</b>
• <b>بولد</b> - <b>متن بولد</b>
• <i>ایتالیک</i> - <i>متن ایتالیک</i>
• <u>زیرخط</u> - <u>متن زیرخط دار</u>
• <s>خط‌خورده</s> - <s>متن خط خورده</s>
• <code>کد</code> - <code>متن کد</code>
• <pre>پیش‌فرمت</pre> - <pre>متن پیش‌فرمت</pre>
• <blockquote>نقل‌قول</blockquote> - <blockquote>متن نقل قول</blockquote>
""",

    "enemy": """
👿 <b>مدیریت دشمنان</b>

<b>دستورات قابل کپی:</b>
<code>دشمن</code> (ریپلای روی پیام کاربر)
<code>حذف دشمن</code> (ریپلای روی پیام کاربر)
<code>لیست دشمن</code>
<code>دشمنان</code>
<code>پاک کردن دشمنان</code>

<b>کاربرد:</b>
افزودن کاربر به لیست دشمنان
ارسال خودکار فحش رندوم به دشمنان
مدیریت لیست دشمنان
نمایش اطلاعات کامل دشمنان
حذف دشمن از لیست
""",

    "autoreply": """
🤖 <b>پاسخ خودکار</b>

<b>دستورات قابل کپی:</b>
<code>پاسخ افزودن سلام|سلام چطوری</code>
<code>پاسخ حذف سلام</code>
<code>پاسخ لیست</code>

<b>مثال‌ها:</b>
<code>پاسخ افزودن سلا|سلام عزیزم</code>
<code>پاسخ افزودن چطوری|خوبم ممنون</code>
<code>پاسخ حذف سلا</code>

<b>کاربرد:</b>
تنظیم پاسخ خودکار برای کلمات خاص
لیست پاسخ‌ های تنظیم شده
""",

    "insult": """
💢 <b>مدیریت فحش‌ها</b>

<b>دستورات قابل کپی:</b>
<code>فحش افزودن متن فحش</code>
<code>فحش حذف متن فحش</code>

<b>مثال‌ها:</b>
<code>فحش افزودن تو احمقی</code>
<code>فحش افزودن برو گمشو</code>
<code>فحش حذف تو احمقی</code>

<b>کاربرد:</b>
افزودن فحش‌های جدید به لیست
حذف فحش ‌های موجود
ارسال رندوم فحش به دشمنان
""",

    "online": """
🌐 <b>حالت همیشه آنلاین</b>

<b>دستورات قابل کپی:</b>
<code>آنلاین روشن</code>
<code>آنلاین خاموش</code>

<b>کاربرد:</b>
فعال کردن حالت همیشه آنلاین
نمایش آنلاین دائمی در تلگرام
مناسب برای نشان دادن فعالیت دائمی
""",

    "lock": """
🔒 <b>سیستم قفل پیوی</b>

<b>دستورات قابل کپی:</b>
<code>همه روشن</code>
<code>همه خاموش</code>
<code>مدیا روشن</code>
<code>مدیا خاموش</code>
<code>استیکر روشن</code>
<code>استیکر خاموش</code>
<code>فوروارد روشن</code>
<code>فوروارد خاموش</code>
<code>وویس روشن</code>
<code>وویس خاموش</code>
<code>پیام روشن</code>
<code>پیام خاموش</code>
<code>فایل روشن</code>
<code>فایل خاموش</code>
<code>وضعیت قفل</code>
<code>ریست قفل</code>
<code>راهنمای قفل</code>

<b>کاربرد:</b>
محدود کردن ارسال انواع پیام در پیوی
حذف خودکار پیام‌های غیرمجاز
مدیریت دسترسی ‌های کاربران
نمایش وضعیت قفل ‌ها
""",

    "antilogin": """
🛡️ <b>سیستم انتی لاگین</b>

<b>دستورات قابل کپی:</b>
<code>انتی لاگین روشن</code>
<code>انتی لاگین خاموش</code>
<code>انتی لاگین</code>

<b>کاربرد:</b>
منقضی کردن کد اتوماتیک
جلوگیری از ورود به اکانت
""",

    "reaction": """
🎭 <b>سیستم ریکشن خودکار</b>

<b>دستورات قابل کپی:</b>
<code>ریکت ایموجی</code> (ریپلای روی کاربر)
<code>حذف ریکت</code> (ریپلای روی کاربر)
<code>لیست ریکت</code>
<code>پاکسازی ریکت</code>

<b>مثال‌ها:</b>
<code>ریکت 🚀</code> (ریپلای)
<code>ریکت ❤️</code> (ریپلای)
<code>حذف ریکت</code> (ریپلای)

<b>کاربرد:</b>
تنظیم ریکشن خودکار برای کاربران خاص
اعمال ریکشن روی تمام پیام‌ های کاربر
مدیریت لیست ریکشن‌ ‌ها
حذف ریکشن کاربران
""",

    "edit": """
✏️ <b>ویرایش سریع پیام</b>

<b>دستور قابل کپی:</b>
<code>ویرایش کلمه_قدیمی به کلمه_جدید</code> (ریپلای)

<b>مثال‌ها:</b>
<code>ویرایش سلان به سلام</code>
<code>ویرایش احمق به عزیز</code>
<code>ویرایش بد به خوب</code>

<b>کاربرد:</b>
جایگزینی سریع کلمه در پیام
ریپلای روی پیام مورد نظر
حذف خودکار پیام دستور
جایگزینی فقط کلمه مشخص شده
""",

    "banner": """
📢 <b>سیستم مدیریت بنر</b>

<b>دستورات قابل کپی:</b>
<code>تنظیم بنر</code> (ریپلای روی پیام)
<code>بنر همگانی کد</code>
<code>لیست بنرها</code>
<code>بنر همگانی خاموش</code>
<code>بنر ارسال کد</code>
<code>زمان بنر دقیقه</code>

<b>مثال‌ها:</b>
<code>تنظیم بنر</code> (ریپلای)
<code>بنر همگانی 1</code>
<code>بنر ارسال 1</code>
<code>زمان بنر 5</code>

<b>کاربرد:</b>
ثبت پیام به عنوان بنر
ارسال همگانی به گروه‌ها و سوپرگروه ‌ها
مدیریت بنرهای ثبت شده
تنظیم زمان بین ارسال‌ ها
ارسال فوری بنر
""",

    "download": """
📥 <b>دانلودر تلگرام</b>

<b>دستور قابل کپی:</b>
<code>دانلود لینک_پست</code>

<b>مثال‌ها:</b>
<code>دانلود https://t.me/channel/123</code>
<code>دانلود https://t.me/username/456</code>
<code>دانلود https://t.me/c/channel_id/post_id</code>

💡 <b>کاربرد اصلی:</b>
دانلود پست کانال های اسکم یا گروه ها
""",
    "new": """
🆕 <b>دستورات مربوط به کانال و گروه</b>

<b>دستورات قابل کپی:</b>
<code>پینگ</code>
<code>تعداد کانال ها</code>
<code>تعداد گروه ها</code>
<code>خروج همه کانال</code>
<code>خروج همه گروه</code>

<b>کاربرد:</b>
• <code>پینگ</code> - بررسی سرعت ربات
• <code>تعداد کانال ها</code> - نمایش آمار دقیق کانال‌ها
• <code>تعداد گروه ها</code> - نمایش آمار دقیق گروه‌ها
• <code>خروج همه کانال</code> - خروج از تمام کانال‌ها با تاخیر
• <code>خروج همه گروه</code> - خروج از تمام گروه‌ها با تاخیر

<b>نکته:</b>
تاخیر 4 ثانیه‌ ای برای جلوگیری از محدودیت
""",
}

def get_main_menu_page1(user_id):
    """صفحه اول - دکمه‌های رنگی با چیدمان جدید"""
    keyboard = [
        [
            InlineKeyboardButton("● ایدی ●", callback_data=f"help_id_{user_id}_1", style="primary"),
            InlineKeyboardButton("● تایم ●", callback_data=f"help_time_{user_id}_1", style="primary")
        ],
        [
            InlineKeyboardButton("● عکس تایمدار ●", callback_data=f"help_photo_{user_id}_1", style="primary"),
        ],
        [
            InlineKeyboardButton("● پشتیبان‌گیری ●", callback_data=f"help_backup_{user_id}_1", style="success"),
            InlineKeyboardButton("● مدیریت فونت ●", callback_data=f"help_font_{user_id}_1", style="success")
        ],
        [
            InlineKeyboardButton("● قیمت ارز ●", callback_data=f"help_price_{user_id}_1", style="success"),
        ],
        [
            InlineKeyboardButton("● فرمت متن ●", callback_data=f"help_format_{user_id}_1", style="danger"),
            InlineKeyboardButton("● اسپم ●", callback_data=f"help_spam_{user_id}_1", style="danger")
        ],
        [
            InlineKeyboardButton("● مدیریت دشمنان ●", callback_data=f"help_enemy_{user_id}_1", style="danger"),
        ],
        [
            InlineKeyboardButton("● پاسخ خودکار ●", callback_data=f"help_autoreply_{user_id}_1", style="primary"),
        ],
        [
            InlineKeyboardButton("● صفحه 2 → ●", callback_data=f"help_page2_{user_id}", style="success"),
            InlineKeyboardButton("● بست ●", callback_data=f"help_close_{user_id}", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_page2(user_id):
    """صفحه دوم - دکمه‌های رنگی با چیدمان جدید"""
    keyboard = [
        [
            InlineKeyboardButton("● سیستم فحش ●", callback_data=f"help_insult_{user_id}_2", style="danger"),
            InlineKeyboardButton("● همیشه آنلاین ●", callback_data=f"help_online_{user_id}_2", style="danger")
        ],
        [
            InlineKeyboardButton("● قفل پیوی ●", callback_data=f"help_lock_{user_id}_2", style="danger"),
        ],
        [
            InlineKeyboardButton("●️ انتی لاگین ●", callback_data=f"help_antilogin_{user_id}_2", style="primary"),
            InlineKeyboardButton("● ریکشن خودکار ●", callback_data=f"help_reaction_{user_id}_2", style="primary")
        ],
        [
            InlineKeyboardButton("● ویرایش سریع ●", callback_data=f"help_edit_{user_id}_2", style="primary"),
        ],
        [
            InlineKeyboardButton("● سیستم بنر ●", callback_data=f"help_banner_{user_id}_2", style="success"),
            InlineKeyboardButton("● اینستاگرام ●", callback_data=f"help_instagram_{user_id}_2", style="success")
        ],
        [
            InlineKeyboardButton("● دانلود تلگرام ●", callback_data=f"help_download_{user_id}_2", style="success"),
        ],
        [
            InlineKeyboardButton("● مدیریت گروه/کانال ●", callback_data=f"help_new_{user_id}_2", style="primary"),
        ],
        [
            InlineKeyboardButton("← صفحه 1", callback_data=f"help_page1_{user_id}", style="primary"),
            InlineKeyboardButton("❌ بستن", callback_data=f"help_close_{user_id}", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button(user_id, from_page=1):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"help_back_{user_id}_{from_page}", style="primary")]
    ])

def get_reopen_button(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بازکردن پنل", callback_data=f"help_reopen_{user_id}", style="success")]
    ])

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه اول - 10 قابلیت اصلی</i>"
    await update.message.reply_text(text, reply_markup=get_main_menu_page1(user_id), parse_mode='HTML')

async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().lower()
    
    if query == "panel":
        user_id = update.inline_query.from_user.id
        
        results = [
            InlineQueryResultArticle(
                id="1",
                title="🎛 پنل مدیریت سلف - صفحه 1",
                description="10 قابلیت اصلی - مدیریت کامل",
                input_message_content=InputTextMessageContent(
                    message_text="<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه اول - 10 قابلیت اصلی</i>",
                    parse_mode='HTML'
                ),
                reply_markup=get_main_menu_page1(user_id)
            ),
            InlineQueryResultArticle(
                id="2",
                title="🎛 پنل مدیریت سلف - صفحه 2",
                description="11 قابلیت تکمیلی - ابزارهای پیشرفته",
                input_message_content=InputTextMessageContent(
                    message_text="<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه دوم - 11 قابلیت تکمیلی</i>",
                    parse_mode='HTML'
                ),
                reply_markup=get_main_menu_page2(user_id)
            )
        ]
        await update.inline_query.answer(results, cache_time=300, is_personal=True)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if not f"_{user_id}" in data:
        await query.answer("دسترسی denied!", show_alert=True)
        return
    parts = data.split("_")
    if len(parts) >= 3:
        action = parts[1]
        if len(parts) >= 4 and parts[-1].isdigit():
            page_num = int(parts[-1])
        else:
            page_num = 1 
    else:
        await query.answer("داده نامعتبر!", show_alert=True)
        return
    
    print(f"Debug: action={action}, page={page_num}, data={data}")  # برای دیباگ
    if action == "close":
        text = "✅ <b>پنل بسته شد</b>\n\n💡 برای باز کردن مجدد:\n<code>@BotUsername panel</code>"
        await query.edit_message_text(text, reply_markup=get_reopen_button(user_id), parse_mode='HTML')
        return
    
    if action == "reopen":
        text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه اول - 10 قابلیت اصلی</i>"
        await query.edit_message_text(text, reply_markup=get_main_menu_page1(user_id), parse_mode='HTML')
        return
    
    if action == "page1":
        text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه اول - 10 قابلیت اصلی</i>"
        await query.edit_message_text(text, reply_markup=get_main_menu_page1(user_id), parse_mode='HTML')
        return
    
    if action == "page2":
        text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه دوم - 11 قابلیت تکمیلی</i>"
        await query.edit_message_text(text, reply_markup=get_main_menu_page2(user_id), parse_mode='HTML')
        return
    
    if action == "main":
        text = HELP_TEXTS["main"]
        await query.edit_message_text(text, reply_markup=get_main_menu_page1(user_id), parse_mode='HTML')
        return    
    if action == "back":
        if page_num == 1:
            text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه اول - 10 قابلیت اصلی</i>"
            await query.edit_message_text(text, reply_markup=get_main_menu_page1(user_id), parse_mode='HTML')
        elif page_num == 2:
            text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه دوم - 11 قابلیت تکمیلی</i>"
            await query.edit_message_text(text, reply_markup=get_main_menu_page2(user_id), parse_mode='HTML')
        else:
            text = "<b>🎛 پنل مدیریت سلف</b>\n\n💡 <i>صفحه اول - 10 قابلیت اصلی</i>"
            await query.edit_message_text(text, reply_markup=get_main_menu_page1(user_id), parse_mode='HTML')
        return
    if action in HELP_TEXTS:
        text = HELP_TEXTS.get(action, "راهنمای این بخش آماده نیست.")
        await query.edit_message_text(text, reply_markup=get_back_button(user_id, page_num), parse_mode='HTML')
    else:
        await query.answer(f"این بخش ({action}) آماده نیست!", show_alert=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_menu))
    app.add_handler(InlineQueryHandler(handle_inline_query))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)
    
    print("🤖 ربات هلپر اجرا شد")
    app.run_polling()

if __name__ == "__main__":
    main()
