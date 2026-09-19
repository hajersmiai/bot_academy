import logging
import json
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# États
WELCOME, PHONE, EMAIL, POSITION, EXPERIENCE, TECHNICAL, MOTIVATION, AVAILABILITY, CONFIRMATION = range(9)

# Questions d'interview
QUESTIONS = {
    "POSITION": {
        "text": "📍 ما هي مهنتك الحالية؟",
        "options": ["طالبة", "موظفة", "أم في البيت", "عاملة", "أخرى"]
    },
    "EXPERIENCE": {
        "text": "📅 هل حفظتِ شيئاً من القرآن من قبل؟",
        "options": ["لا, أول مرة", "نعم, أحزاب قليلة", "نعم, أجزاء عديدة", "نعم, أكثر من نصف"]
    },
    "TECHNICAL": {
        "text": "💻 كم ساعة يومياً تستطيعين تخصيصها للحفظ والتسميع؟",
        "options": ["أقل من ساعة", "1-2 ساعات", "2-3 ساعات", "أكثر من 3 ساعات"]
    },
    "MOTIVATION": {
        "text": "🎯 ما دافعك الأساسي للالتحاق بالبرنامج؟",
        "options": None  # Réponse libre
    },
    "AVAILABILITY": {
        "text": "⏰ هل تستطيعين الالتزام بالبرنامج لمدة 3 سنوات؟",
        "options": ["نعم, مستعدة تماماً", "غالباً، لكن قد يكون هناك طوارئ", "أحتاج وقتاً لأفكر", "لست متأكدة"]
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarrage du bot"""
    user = update.effective_user
    # Récupérer l'ID depuis le lien (ex: /start candidate_001)
    candidate_id = None
    if context.args and len(context.args) > 0:
        candidate_id = context.args[0]
    message = f"""
السلام عليكم ورحمة الله وبركاته 👋 {user.first_name}

أهلا بك في أكاديمية "قد أفلح من زكّاها" 📖
نسعد بانضمامك معنا في رحلة حفظ كتاب الله

⏳ قبل البدء في المقابلة:
1️⃣ تأكدي من ملء نموذج التسجيل:
https://forms.gle/QcSpoU2BcTdHiqkH8

2️⃣ بعد إكمال النموذج، اضغطي /interview للبدء

هل ملأتِ النموذج؟ 🤔
"""
    
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    context.user_data['candidate'] = {
        'telegram_id': user.id,
        'candidate_id': candidate_id,  # ← ID UNIQUE
        'first_name': user.first_name,
        'start_time': datetime.now().isoformat()
    }
    logger.info(f"✅ Candidate ID: {candidate_id}")
    return WELCOME


async def interview_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarre l'interview"""
    
    message = """
🎙️ ممتاز! سننطلق معك الآن في المقابلة

هذه أسئلة قصيرة لنعرفك أكثر.

السؤال 1️⃣ :
"""
    
    question = QUESTIONS["POSITION"]
    keyboard = [question["options"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        resize_keyboard=True
    )
    
    await update.message.reply_text(message + question["text"], reply_markup=reply_markup)
    return PHONE


async def get_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère la position"""
    context.user_data['candidate']['position'] = update.message.text
    
    question = QUESTIONS["EXPERIENCE"]
    keyboard = [question["options"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        "السؤال 2️⃣ :\n" + question["text"],
        reply_markup=reply_markup
    )
    return EMAIL


async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère l'expérience"""
    context.user_data['candidate']['experience'] = update.message.text
    
    question = QUESTIONS["TECHNICAL"]
    keyboard = [question["options"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        "السؤال 3️⃣ :\n" + question["text"],
        reply_markup=reply_markup
    )
    return POSITION


async def get_technical(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère les compétences techniques"""
    context.user_data['candidate']['technical_skills'] = update.message.text
    
    question = QUESTIONS["MOTIVATION"]
    await update.message.reply_text(
        "السؤال 4️⃣ :\n" + question["text"],
        reply_markup=ReplyKeyboardRemove()
    )
    return EXPERIENCE


async def get_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère la motivation"""
    context.user_data['candidate']['motivation'] = update.message.text
    
    question = QUESTIONS["AVAILABILITY"]
    keyboard = [question["options"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        "السؤال 5️⃣ :\n" + question["text"],
        reply_markup=reply_markup
    )
    return TECHNICAL


async def get_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère la disponibilité"""
    context.user_data['candidate']['availability'] = update.message.text
    context.user_data['candidate']['end_time'] = datetime.now().isoformat()
    
    # Résumé
    candidate = context.user_data['candidate']
    summary = f"""
✅ شكراً على إجاباتك!

📋 ملخص بياناتك:
🔹 المهنة: {candidate.get('position', 'N/A')}
🔹 الحفظ  السابق: {candidate.get('experience', 'N/A')}
🔹 الوقت المتاح: {candidate.get('technical_skills', 'N/A')}
🔹 الدافع: {candidate.get('motivation', 'N/A')}
🔹 الالتزام: {candidate.get('availability', 'N/A')}

هل هذه البيانات صحيحة؟
"""
    
    keyboard = [["✅ نعم, أكمل", "❌ لا, أعد الإجابة"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(summary, reply_markup=reply_markup)
    return CONFIRMATION


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Traite la confirmation"""
    
    if "نعم" in update.message.text:
        candidate_data = context.user_data['candidate']
        save_candidate(candidate_data)
        
        await update.message.reply_text(
            """
🎉 جزاكِ الله خيراً!

تم تسجيل بياناتك بنجاح ✅
سيتم التواصل معك قريباً بخصوص المقابلة النهائية.

🤲 "وما توفيقي إلا بالله"
""",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "حسناً، لنعد من البداية 🔄\n\nما حالتك الحالية؟",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['candidate'] = {
            'telegram_id': update.effective_user.id,
            'start_time': datetime.now().isoformat()
        }
        return PHONE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annule"""
    await update.message.reply_text(
        "حسناً، السلام عليكم 👋",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def save_candidate(candidate_data: dict) -> None:
    """Sauvegarde les données"""
    os.makedirs('candidates_data', exist_ok=True)
     # Utiliser l'ID comme nom de fichier
    candidate_id = candidate_data.get('candidate_id', 'unknown')
    filename = f"candidates_data/{candidate_id}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(candidate_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Candidat sauvegardé: {filename}")


def main() -> None:
    """Démarre le bot"""
    
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ ERREUR: TOKEN non défini!")
        print("Définissez TELEGRAM_BOT_TOKEN")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Handler pour /interview
    app.add_handler(CommandHandler("interview", interview_start))
    
    # Handler principal
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, interview_start)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_technical)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_motivation)],
            TECHNICAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_availability)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    
    print("✅ Bot démarré...")
    app.run_polling()


if __name__ == '__main__':
    main()