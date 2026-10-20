#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تولید کیوآرکدهای کتاب صوتی مزرعه
تولید نسخه‌های برداری (SVG)، چاپی با کیفیت ۳۰۰ دی‌پی‌آی (PNG)، مانیفست اکسل و بررسی فایل‌های صوتی
"""

import os
import sys
import json
import csv
import argparse
import subprocess
import shutil

# اطمینان از خروجی یونیکد در کنسول ویندوز
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    import qrcode
    import qrcode.image.svg
except ImportError:
    print("خطا: کتابخانه qrcode نصب نیست. دستور 'pip install qrcode[pil]' را اجرا کنید.")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    print("خطا: کتابخانه‌های Pillow یا arabic-reshaper یا python-bidi نصب نیستند.")
    sys.exit(1)


def detect_github_username(cli_username=None):
    """تشخیص خودکار یا دستی نام کاربری گیتهاب"""
    if cli_username:
        return cli_username.strip()

    # تلاش برای خواندن از طریق دستور gh api user
    try:
        res = subprocess.run(
            ['gh', 'api', 'user'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            if 'login' in data and data['login']:
                return data['login']
    except Exception:
        pass

    # بررسی متغیرهای محیطی
    env_user = os.environ.get('GITHUB_USERNAME') or os.environ.get('GITHUB_USER')
    if env_user:
        return env_user.strip()

    # مقدار پیش‌فرض اگر هیچ‌کدام یافت نشد
    return 'milad'


def ensure_sample_audio_exists(animals, audio_dir):
    """بررسی وجود فایل‌های صوتی و ساخت نمونه در صورت نبودن"""
    os.makedirs(audio_dir, exist_ok=True)
    
    # فرکانس‌های پایه برای هر حیوان جهت تولید صدای نمونه ترکیبی سنتز شده در صورت نبودن فایل
    sample_notes = {
        'hen': [800, 1000, 900],
        'cow': [130, 110, 95],
        'sheep': [300, 350, 280],
        'goose': [500, 650, 450],
        'duck': [400, 320, 380],
        'donkey': [200, 450, 180],
        'dog': [250, 200, 150],
        'horse': [600, 400, 300],
        'goat': [320, 380, 310]
    }

    for animal in animals:
        audio_path = os.path.join(audio_dir, f"{animal['id']}.mp3")
        if not os.path.exists(audio_path):
            print(f"فایل صوتی {audio_path} یافت نشد. در حال ساخت فایل صوتی نمونه...")
            create_synthesized_mp3(audio_path, sample_notes.get(animal['id'], [440, 550, 660]))


def create_synthesized_mp3(output_path, freqs):
    """ساخت یک فایل صوتی ملودیک با ffmpeg در صورت نبودن فایل اصلی"""
    try:
        # ساخت با استفاده از مولد صوتی داخلی ffmpeg
        filter_expr = f"sine=frequency={freqs[0]}:duration=0.6,afade=t=out:st=0.4:d=0.2"
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i', filter_expr,
            '-b:a', '128k', output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"هشدار: ساخت نمونه صوتی با خطا مواجه شد: {e}")


def get_persian_font(size=44):
    """انتخاب و بارگذاری بهترین فونت فارسی موجود"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    candidate_paths = [
        os.path.join(script_dir, 'assets', 'Vazirmatn-Bold.ttf'),
        os.path.join(project_root, 'assets', 'Vazirmatn-Bold.ttf'),
        'C:/Windows/Fonts/Vazirmatn-Bold.ttf',
        'C:/Windows/Fonts/tahoma.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    ]

    for p in candidate_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue

    return ImageFont.load_default()


def generate_svg_qr(url, output_path):
    """تولید کیوآرکد برداری استاندارد با فرمت SVG مناسب چاپگر و ایلاستریتور"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=2,
        image_factory=qrcode.image.svg.SvgPathImage
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(output_path)


def generate_png_300dpi_with_label(url, label_text, output_path, font):
    """تولید تصویر کیوآرکد PNG با تراکم ۳۰۰ نقطه بر اینچ (300 DPI) و برچسب فارسی خوانا"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=18,
        border=3
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    qr_width, qr_height = qr_img.size

    # تنظیم متن فارسی با تغییر شکل و چینش راست‌به‌چپ
    try:
        reshaped = arabic_reshaper.reshape(label_text)
        bidi_text = get_display(reshaped)
    except Exception:
        bidi_text = label_text

    # فضای پایین برای برچسب
    label_padding_bottom = 30
    label_height = 80
    total_height = qr_height + label_height

    final_img = Image.new('RGB', (qr_width, total_height), 'white')
    final_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final_img)
    
    # محاسبه موقعیت متن برای قرارگیری دقیق در مرکز
    try:
        bbox = draw.textbbox((0, 0), bidi_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        text_w, text_h = (150, 40)

    text_x = max(10, (qr_width - text_w) // 2)
    text_y = qr_height + (label_height - label_padding_bottom - text_h) // 2

    # رسم متن نام حیوان
    draw.text((text_x, text_y), bidi_text, fill=(30, 30, 30), font=font)

    # ذخیره تصویر با متادیتای چاپی 300 DPI
    final_img.save(output_path, format='PNG', dpi=(300, 300))


def main():
    parser = argparse.ArgumentParser(description="تولید کیوآرکد و فایل‌های پروژه کتاب صوتی مزرعه")
    parser.add_argument('--username', type=str, default=None, help='نام کاربری گیتهاب')
    parser.add_argument('--repo', type=str, default='farm-book-sounds', help='نام مخزن گیتهاب')
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    username = detect_github_username(args.username)
    repo = args.repo.strip()
    base_url = f"https://{username}.github.io/{repo}/"

    print("=" * 60)
    print("سیستم تولید کیوآرکدهای کتاب کودک صوتی مزرعه")
    print(f"نام کاربری گیتهاب: {username}")
    print(f"نام مخزن: {repo}")
    print(f"آدرس پایه وب‌سایت: {base_url}")
    print("=" * 60)

    # ۱. خواندن اطلاعات حیوانات
    data_file = os.path.join('data', 'animals.json')
    if not os.path.exists(data_file):
        print(f"خطا: فایل {data_file} یافت نشد.")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)

    # ۲. بررسی و اطمینان از وجود فایل‌های صوتی
    audio_dir = os.path.join(project_root, 'audio')
    ensure_sample_audio_exists(animals, audio_dir)

    # ۳. آماده‌سازی پوشه‌های خروجی
    output_dir = os.path.join(project_root, 'qr_output')
    svg_dir = os.path.join(output_dir, 'svg')
    png_dir = os.path.join(output_dir, 'png_300dpi')
    os.makedirs(svg_dir, exist_ok=True)
    os.makedirs(png_dir, exist_ok=True)

    font = get_persian_font(size=44)

    # ۴. تولید کیوآرکدها و سطر‌های فایل مانیفست
    manifest_rows = []

    for item in animals:
        anim_id = item['id']
        anim_name = item['name']
        anim_emoji = item.get('emoji', '')
        anim_audio = item.get('audio', f'audio/{anim_id}.mp3')

        # لینک اختصاصی پلیر و لینک مستقیم فایل صوتی
        player_link = f"{base_url}?s={anim_id}"
        direct_audio_link = f"{base_url}{anim_audio}"

        svg_filename = f"{anim_id}.svg"
        png_filename = f"{anim_id}.png"

        svg_path = os.path.join(svg_dir, svg_filename)
        png_path = os.path.join(png_dir, png_filename)

        print(f"در حال پردازش: {anim_name} ({anim_id}) ...")

        # تولید SVG برداری
        generate_svg_qr(player_link, svg_path)

        # تولید PNG با کیفیت ۳۰۰ دی‌پی‌آی
        label = f"صدای {anim_name}"
        generate_png_300dpi_with_label(player_link, label, png_path, font)

        manifest_rows.append({
            'شناسه حیوان (ID)': anim_id,
            'نام حیوان': anim_name,
            'ایموجی': anim_emoji,
            'لینک وب‌پلیر (QR)': player_link,
            'لینک مستقیم فایل صوتی': direct_audio_link,
            'فایل برداری (SVG)': f"svg/{svg_filename}",
            'فایل چاپی (PNG 300DPI)': f"png_300dpi/{png_filename}"
        })

    # ۵. ذخیره فایل مانیفست راهنما
    manifest_file = os.path.join(output_dir, 'manifest.csv')
    fieldnames = [
        'شناسه حیوان (ID)',
        'نام حیوان',
        'ایموجی',
        'لینک وب‌پلیر (QR)',
        'لینک مستقیم فایل صوتی',
        'فایل برداری (SVG)',
        'فایل چاپی (PNG 300DPI)'
    ]
    with open(manifest_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    print("-" * 60)
    print("عملیات با موفقیت به پایان رسید:")
    print(f"۱. ۹ فایل SVG برداری در: {svg_dir}")
    print(f"۲. ۹ فایل PNG ۳۰۰ دی‌پی‌آی در: {png_dir}")
    print(f"۳. فایل اکسل مانیفست راهنما: {manifest_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()
