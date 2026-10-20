# سیستم پخش صدای حیوانات کتاب چاپی کودک 🚜🌾

این پروژه یک سیستم کامل، سبک، زیبا، رایگان و بدون تبلیغات برای پخش صدای ۹ حیوان مزرعه است که از طریق کیوآرکدهای چاپی داخل کتاب در دسترس کودکان قرار می‌گیرد و بر روی **GitHub Pages** میزبانی می‌شود.

---

## 📁 ساختار کامل پروژه

```text
├── audio/                  # ۹ فایل صوتی واقعی با کیفیت بالا و بهینه‌شده
│   ├── hen.mp3
│   ├── cow.mp3
│   ├── sheep.mp3
│   ├── goose.mp3
│   ├── duck.mp3
│   ├── donkey.mp3
│   ├── dog.mp3
│   ├── horse.mp3
│   └── goat.mp3
├── data/
│   └── animals.json        # اطلاعات حیوانات (شناسه کوتاه، نام فارسی، ایموجی، آدرس صوت)
├── qr_output/              # فایل‌های آماده تحویل به صفحه آرا و چاپخانه
│   ├── svg/                # کیوآرکدهای برداری (Vector) مخصوص ایندیزاین و ایلستریتور
│   ├── png_300dpi/         # کیوآرکدهای پیکسلی با رزولوشن ۳۰۰ دی‌پی‌آی همراه با نام حیوان
│   └── manifest.csv        # فایل راهنمای جامع (شامل لینک‌ها، نام فایل‌ها و نام حیوانات)
├── scripts/
│   ├── generate_qrs.py     # اسکریپت پایتون جهت تولید کیوآرکدها و بررسی فایل‌های صوتی
│   └── assets/             # فونت زیبای وزیرمتن برای درج متن فارسی در تصاویر چاپی
├── .github/
│   └── workflows/
│       └── deploy.yml      # استقرار خودکار در GitHub Pages به محض Push کردن
├── index.html              # صفحه وب‌پلیر کودک‌پسند با طراحی شاد و استاندارد
├── style.css               # استایل ریسپانسیو (Mobile-First) با فونت وزیرمتن
├── app.js                  # مسیریابی بر اساس پارامتر آدرس (?s=hen) و منطق پخش صوت
└── requirements.txt        # کتابخانه‌های پایتون مورد نیاز
```

---

## 🐾 لیست حیوانات و شناسه‌ها

| رديف | حیوان | شناسه کوتاه (ID) | ایموجی | فایل صوتی | آدرس اختصاصی وب‌پلیر |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ۱ | مرغ | `hen` | 🐔 | `audio/hen.mp3` | `https://<username>.github.io/farm-book-sounds/?s=hen` |
| ۲ | گاو | `cow` | 🐄 | `audio/cow.mp3` | `https://<username>.github.io/farm-book-sounds/?s=cow` |
| ۳ | گوسفند | `sheep` | 🐑 | `audio/sheep.mp3` | `https://<username>.github.io/farm-book-sounds/?s=sheep` |
| ۴ | غاز | `goose` | 🪿 | `audio/goose.mp3` | `https://<username>.github.io/farm-book-sounds/?s=goose` |
| ۵ | اردک | `duck` | 🦆 | `audio/duck.mp3` | `https://<username>.github.io/farm-book-sounds/?s=duck` |
| ۶ | الاغ | `donkey` | 🫏 | `audio/donkey.mp3` | `https://<username>.github.io/farm-book-sounds/?s=donkey` |
| ۷ | سگ گله | `dog` | 🐕 | `audio/dog.mp3` | `https://<username>.github.io/farm-book-sounds/?s=dog` |
| ۸ | اسب | `horse` | 🐎 | `audio/horse.mp3` | `https://<username>.github.io/farm-book-sounds/?s=horse` |
| ۹ | بز | `goat` | 🐐 | `audio/goat.mp3` | `https://<username>.github.io/farm-book-sounds/?s=goat` |

---

## 🚀 راهنمای راه‌اندازی و انتشار روی GitHub Pages

### ۱. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### ۲. اجرای اسکریپت ساخت کیوآرکد با نام کاربری دلخواه گیتهاب
اگر می‌خواهید کیوآرکدها به آدرس گیتهاب شما تنظیم شوند، کافیست نام کاربری خود را به شکل زیر وارد کنید:
```bash
python scripts/generate_qrs.py --username your_github_username
```
*(اگر قبلاً با `gh auth login` وارد شده باشید، نام کاربری به صورت خودکار تشخیص داده می‌شود)*

### ۳. ساخت مخزن و ارسال به گیتهاب
در ترمینال همین پوشه:
```bash
git init
git add .
git commit -m "Initial commit for farm book sounds"
git branch -M main
git remote add origin https://github.com/your_github_username/farm-book-sounds.git
git push -u origin main
```

سپس در تنظیمات ریپازیتوری در گیتهاب:
به مسیر **Settings > Pages** بروید و در بخش **Build and deployment > Source** گزینه **GitHub Actions** را انتخاب کنید. پس از چند لحظه وب‌سایت شما فعال خواهد شد!
