# 🤖 بوت تيليغرام ذكاء اصطناعي - Claude

## 🚀 الرفع على Railway (مجاناً)

### الخطوة 1 - رفع الكود على GitHub
1. اذهب إلى [github.com](https://github.com) وأنشئ حساباً إذا ليس عندك
2. اضغط **New repository** → سمّه `telegram-ai-bot`
3. ارفع الملفات الأربعة: `main.py`, `requirements.txt`, `Procfile`, `railway.json`

### الخطوة 2 - إنشاء مشروع على Railway
1. اذهب إلى [railway.app](https://railway.app)
2. سجل دخول بحساب GitHub
3. اضغط **New Project** ← **Deploy from GitHub repo**
4. اختر الـ repo اللي أنشأته

### الخطوة 3 - إضافة المفاتيح (Environment Variables)
في صفحة المشروع:
1. اضغط على الـ service
2. اذهب لتبويب **Variables**
3. أضف هذين المتغيرين:

| المفتاح | القيمة |
|---------|--------|
| `TELEGRAM_TOKEN` | توكن البوت من @BotFather |
| `ANTHROPIC_API_KEY` | مفتاح Anthropic من console.anthropic.com |

### الخطوة 4 - Deploy!
بعد إضافة المتغيرات، Railway سيعيد الـ deploy تلقائياً ✅

---

## 🔑 كيف تحصل على المفاتيح؟

### Telegram Token:
1. افتح تيليغرام وابحث عن **@BotFather**
2. أرسل `/newbot`
3. اختر اسماً للبوت
4. انسخ التوكن

### Anthropic API Key:
1. اذهب إلى [console.anthropic.com](https://console.anthropic.com)
2. سجل دخول أو أنشئ حساباً
3. اذهب إلى **API Keys** ← **Create Key**
4. انسخ المفتاح

---

## 📋 الأوامر المتاحة في البوت
- `/start` - البداية
- `/new` - محادثة جديدة
- `/help` - المساعدة
- `/stats` - الإحصائيات

---

## 💡 ملاحظات
- Railway يعطيك **$5 رصيد مجاني** شهرياً
- البوت الخفيف يصرف ~$1-2 شهرياً
- يعمل 24/7 بدون توقف
