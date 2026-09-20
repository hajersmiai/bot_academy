import logging
import json
import os
import gspread
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
WELCOME, NAME, NATIONALITY, POSITION, EXPERIENCE, TECHNICAL, MOTIVATION, AVAILABILITY, CONFIRMATION, ASKING_QUESTION, ANSWERING_QUESTION, SEARCHING = range(12)
# Sheet ID - À remplacer avec votre ID
SHEET_ID = "1TQLcg8d1Py3XbuqZsUvw9qsUswqpH1Ia4edDEZhSSVg"
# Questions d'interview
QUESTIONS = {
     "NAME": {
        "text": "📝 ما اسمك الكامل؟",
        "options": None  # Réponse libre
    },
    "NATIONALITY": {
        "text": "🌍 ما جنسيتك؟",
        "options": None  # Réponse libre
    },
    "POSITION": {
        "text": "📍 ما هي مهنتك الحالية؟",
        "options": [["طالبة"], ["موظفة"], ["أم في البيت"], ["عاملة"], ["أخرى"]]
    },
    "EXPERIENCE": {
        "text": "📅 هل حفظتِ شيئاً من القرآن من قبل؟",
        "options": [["لا، أول مرة"], ["نعم، أحزاب قليلة"], ["نعم، أجزاء عديدة"], ["نعم، أكثر من نصف"]]
    },
    "TECHNICAL": {
        "text": "💻 كم ساعة يومياً تستطيعين تخصيصها للحفظ والتسميع؟",
        "options": [["أقل من ساعة"], ["1-2 ساعات"], ["2-3 ساعات"], ["أكثر من 3 ساعات"]]
    },
    "MOTIVATION": {
        "text": "🎯 ما دافعك الأساسي للالتحاق بالبرنامج؟",
        "options": None  # Réponse libre
    },
    "AVAILABILITY": {
        "text": "⏰ هل تستطيعين الالتزام بالبرنامج لمدة 3 سنوات؟",
        "options": [["نعم، مستعدة تماماً"], ["غالباً، لكن قد يكون هناك طوارئ"], ["أحتاج وقتاً لأفكر"], ["لست متأكدة"]]
    }
}
def get_sheet():
    """Connecte à Google Sheets"""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_CREDENTIALS non défini!")
            return None
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        return sh.sheet1
    except Exception as e:
        logger.error(f"Erreur Google Sheets: {e}")
        return None
        
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

⏳الآن سننطلق معك في المقابلة:

  اضغطي على /interview للبدء

هل أنت مستعدة؟؟ 🤔
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
    
    question = QUESTIONS["NAME"]
    await update.message.reply_text(message + question["text"], reply_markup=ReplyKeyboardRemove())
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère le nom complet"""
    context.user_data['candidate']['full_name'] = update.message.text
    
    question = QUESTIONS["NATIONALITY"]
    await update.message.reply_text(
        "السؤال 2️⃣ :\n" + question["text"],
        reply_markup=ReplyKeyboardRemove()
    )
    return NATIONALITY

async def get_nationality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère la nationalité"""
    context.user_data['candidate']['nationality'] = update.message.text
    
    question = QUESTIONS["POSITION"]
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
        "السؤال 4️⃣ :\n" + question["text"],
        reply_markup=reply_markup
    )
    return EXPERIENCE


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
        "السؤال 5️⃣ :\n" + question["text"],
        reply_markup=reply_markup
    )
    return TECHNICAL


async def get_technical(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère les compétences techniques"""
    context.user_data['candidate']['technical_skills'] = update.message.text
    
    question = QUESTIONS["MOTIVATION"]
    await update.message.reply_text(
        "السؤال 6️⃣ :\n" + question["text"],
        reply_markup=ReplyKeyboardRemove()
    )
    return MOTIVATION


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
        "السؤال 7️⃣ :\n" + question["text"],
        reply_markup=reply_markup
    )
    return AVAILABILITY


async def get_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Récupère la disponibilité"""
    context.user_data['candidate']['availability'] = update.message.text
    context.user_data['candidate']['end_time'] = datetime.now().isoformat()
    
    # Résumé
    candidate = context.user_data['candidate']
    summary = f"""
✅ شكراً على إجاباتك!

📋 ملخص بياناتك:
🔹 الاسم الكامل: {candidate.get('full_name', 'N/A')}
🔹 الجنسية: {candidate.get('nationality', 'N/A')}
🔹 المهنة: {candidate.get('position', 'N/A')}
🔹 الحفظ السابق: {candidate.get('experience', 'N/A')}
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
        # Enregistrer dans Google Sheets
        save_to_google_sheet(candidate_data)
        
        success_message = """
        🎉 جزاكِ الله خيراً!
        
        تم تسجيل بيانات ك بنجاح ✅
        سيتم التواصل معك قريباً بخصوص المقابلة النهائية.
        
        🙏 "وما توفيقي إلا بالله"
        
        إذا لديك أي استفسار اكتبي /question واطرحي سؤالك
        """
        
        await update.message.reply_text(
            success_message,
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "حسناً، لنعد من البداية 🔄",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['candidate'] = {
            'telegram_id': update.effective_user.id,
            'start_time': datetime.now().isoformat()
        }
        return NAME


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annule"""
    await update.message.reply_text(
        "حسناً، السلام عليكم 👋",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
async def question_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarre le flux de question - vérifie d'abord si la candidate existe"""
    user = update.effective_user
    
    logger.info(f"📝 /question appelée par Telegram ID: {user.id}")
    
    # Vérifier si la candidate a complété l'interview
    if not has_completed_interview(user.id):
        logger.warning(f"⚠️ Candidate {user.id} n'a pas complété l'interview")
        
        await update.message.reply_text(
            """
⚠️ **نعتذر!**

يجب عليك أولاً إكمال المقابلة قبل طرح الأسئلة.

📝 الرجاء تنفيذ الخطوات التالية:
1️⃣ اضغطي على /start
2️⃣ اضغطي على /interview
3️⃣ أكملي كل الأسئلة السبعة
4️⃣ ثم استخدمي /question

شكراً لكِ! 🙏
""",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Si la candidate existe, demander sa question
    logger.info(f"✅ Candidate {user.id} a le droit de poser une question")
    
    await update.message.reply_text(
        "📝 تفضلي، اكتبي سؤالك:\n\n(أرسلي رسالة واحدة فقط)",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASKING_QUESTION

def save_question_to_sheet(candidate_name: str, telegram_id: int, question: str) -> None:
    """Enregistre la question dans la feuille Questions"""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_CREDENTIALS non défini!")
            return
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        
        # Ouvrir la feuille "Questions"
        try:
            questions_sheet = sh.worksheet("Questions")
        except:
            # Si la feuille n'existe pas, la créer
            questions_sheet = sh.add_worksheet(title="Questions", rows=100, cols=8)
            header = ["ID", "Candidate_Name", "Telegram_ID", "Question", "Date_Question", "Status", "Reponse_admin", "Date_Reponse"]
            questions_sheet.insert_row(header, index=1)
        
        # Ajouter la question
        row_data = [
            "",
            candidate_name,
            str(telegram_id),
            question,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "En attente",
            "",
            ""
        ]
        
        questions_sheet.append_row(row_data)
        logger.info(f"✅ Question enregistrée pour {candidate_name}")
        
    except Exception as e:
        logger.error(f"❌ ERREUR Google Sheets: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def save_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enregistre la question dans Google Sheets"""
    user = update.effective_user
    question_text = update.message.text
    
    try:
        # Récupérer le nom de la candidate depuis Google Sheets
        candidate_name = get_candidate_name(user.id)
        
        # Enregistrer la question
        save_question_to_sheet(
            candidate_name=candidate_name,
            telegram_id=user.id,
            question=question_text
        )
        
        await update.message.reply_text(
            "✅ تم تسجيل سؤالك بنجاح!\n"
            "سيتم الرد عليك قريباً إن شاء الله 🙏",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement: {e}")
        await update.message.reply_text(
            "❌ حدث خطأ، حاولي مجدداً",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END
def has_completed_interview(telegram_id: int) -> bool:
    """
    Vérifie si la candidate a complété l'interview en cherchant son Telegram_ID
    dans la feuille "Candidates"
    
    Retourne:
        True si la candidate existe dans la feuille
        False sinon
    """
    try:
        sheet = get_sheet()
        if not sheet:
            logger.error("❌ Impossible de se connecter à Google Sheets")
            return False
        
        # Récupérer toutes les valeurs
        all_values = sheet.get_all_values()
        logger.info(f"📊 Total lignes dans Candidates: {len(all_values)}")
        
        if len(all_values) <= 1:  # Juste l'header
            logger.warning(f"⚠️ Aucune candidate trouvée pour Telegram_ID: {telegram_id}")
            return False
        
        # Chercher le Telegram_ID dans la colonne D (index 3)
        telegram_id_str = str(telegram_id)
        
        for idx, row in enumerate(all_values[1:], start=2):  # Ignorer l'header
            if len(row) > 3:  # Vérifier que la ligne a assez de colonnes
                candidate_telegram_id = str(row[3]).strip()  # Colonne D: Telegram_ID
                candidate_name = row[1] if len(row) > 1 else "Unknown"
                
                logger.info(f"🔍 Ligne {idx}: Cherche {telegram_id_str} vs {candidate_telegram_id}")
                
                if candidate_telegram_id == telegram_id_str:
                    logger.info(f"✅ Candidate trouvée: {candidate_name} (ID: {telegram_id})")
                    return True
        
        logger.warning(f"⚠️ Aucune candidate trouvée avec Telegram_ID: {telegram_id}")
        return False
        
    except Exception as e:
        logger.error(f"❌ ERREUR dans has_completed_interview: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
def get_candidate_name(telegram_id: int) -> str:
    """Récupère le nom de la candidate"""
    try:
        sheet = get_sheet()
        if sheet:
            all_values = sheet.get_all_values()
            for row in all_values[1:]:  # Ignorer l'header
                if len(row) > 3 and str(row[3]) == str(telegram_id):
                    return row[1]  # Colonne B: Nom_Complet
        return "Unknown"
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return "Unknown"


        
def save_candidate(candidate_data: dict) -> None:
    """Sauvegarde les données"""
    os.makedirs('candidates_data', exist_ok=True)
    # Utiliser l'ID comme nom de fichier
    candidate_id = candidate_data.get('candidate_id', 'unknown')
    filename = f"candidates_data/{candidate_id}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(candidate_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Candidat sauvegardé: {filename}")
    
async def admin_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche toutes les questions en attente pour les admins"""
    user = update.effective_user
    
    # 🔒 Vérifier si c'est un admin (optional - pour la sécurité)
    # Pour maintenant, on ignore la vérification
    
    try:
        # Récupérer la feuille "Questions"
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            await update.message.reply_text("❌ Erreur: Google non configuré")
            return
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        
        try:
            questions_sheet = sh.worksheet("Questions")
        except:
            await update.message.reply_text("❌ Feuille 'Questions' non trouvée")
            return
        
        # Récupérer toutes les questions
        all_values = questions_sheet.get_all_values()
        
        if len(all_values) <= 1:  # Juste l'header
            await update.message.reply_text("✅ Pas de questions en attente pour le moment")
            return
        
        # Filtrer les questions "En attente"
        pending_questions = []
        for idx, row in enumerate(all_values[1:], start=2):  # Ignorer l'header
            if len(row) > 5 and row[5] == "En attente":  # Colonne F: Status
                pending_questions.append({
                    'row_index': idx,
                    'id': row[0] if len(row) > 0 else '',
                    'candidate_name': row[1] if len(row) > 1 else 'Unknown',
                    'telegram_id': row[2] if len(row) > 2 else '',
                    'question': row[3] if len(row) > 3 else '',
                    'date': row[4] if len(row) > 4 else ''
                })
        
        if not pending_questions:
            await update.message.reply_text("✅ Pas de questions en attente pour le moment")
            return
        
        # Afficher toutes les questions
        message = f"""
📋 **QUESTIONS EN ATTENTE** ({len(pending_questions)})

"""
        
        for i, q in enumerate(pending_questions, 1):
            message += f"""
{i}️⃣ **{q['candidate_name']}** (ID: {q['telegram_id']})
📝 Q: {q['question']}
📅 Date: {q['date']}
━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        message += "\n💡 Utilisez `/repondre [ID]` pour répondre à une question"
        
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await update.message.reply_text(f"❌ Erreur: {str(e)}")

async def repondre_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarre le flux de réponse pour un admin"""
    user = update.effective_user
    
    # Récupérer l'ID de la question depuis la commande
    # Format: /repondre 1
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "❌ Format incorrect!\n"
            "Utilisez: /repondre [question_id]\n\n"
            "Exemple: /repondre 1",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    question_id = context.args[0]
    
    # Sauvegarder l'ID dans le contexte
    context.user_data['admin_question_id'] = question_id
    
    # Chercher la question dans la feuille "Questions"
    question_data = get_question_by_id(question_id)
    
    if not question_data:
        await update.message.reply_text(
            f"❌ Question ID {question_id} non trouvée!",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Afficher la question avant de répondre
    preview_message = f"""
📋 **QUESTION À TRAITER:**

👤 Candidate: {question_data['candidate_name']}
📝 Q: {question_data['question']}
📅 Date: {question_data['date']}

━━━━━━━━━━━━━━━━━━━━━━━━

✍️ Tapez votre réponse ci-dessous:
(une seule message)
"""
    
    await update.message.reply_text(
        preview_message,
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ANSWERING_QUESTION


async def save_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enregistre la réponse dans Google Sheets"""
    user = update.effective_user
    answer_text = update.message.text
    question_id = context.user_data.get('admin_question_id')
    
    if not question_id:
        await update.message.reply_text(
            "❌ Erreur: Question ID non trouvée",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    try:
        # Enregistrer la réponse
        update_question_with_answer(
            question_id=question_id,
            answer=answer_text,
            admin_name=user.first_name or "Admin"
        )
        
        await update.message.reply_text(
            "✅ Réponse enregistrée avec succès!\n"
            "La candidate sera notifiée.",
            reply_markup=ReplyKeyboardRemove()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement: {e}")
        await update.message.reply_text(
            "❌ Erreur lors de l'enregistrement de la réponse",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END
def get_question_by_id(question_id: str) -> dict:
    """Récupère une question par son ID"""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            return None
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        
        try:
            questions_sheet = sh.worksheet("Questions")
        except:
            return None
        
        all_values = questions_sheet.get_all_values()
        
        for idx, row in enumerate(all_values[1:], start=2):
            if len(row) > 0 and row[0] == question_id:
                return {
                    'row_index': idx,
                    'id': row[0] if len(row) > 0 else '',
                    'candidate_name': row[1] if len(row) > 1 else 'Unknown',
                    'telegram_id': row[2] if len(row) > 2 else '',
                    'question': row[3] if len(row) > 3 else '',
                    'date': row[4] if len(row) > 4 else '',
                    'status': row[5] if len(row) > 5 else ''
                }
        
        return None
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return None


def update_question_with_answer(question_id: str, answer: str, admin_name: str) -> None:
    """Met à jour une question avec la réponse de l'admin"""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_CREDENTIALS non défini!")
            return
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        
        questions_sheet = sh.worksheet("Questions")
        all_values = questions_sheet.get_all_values()
        
        # Trouver la ligne avec cette question_id
        for idx, row in enumerate(all_values[1:], start=2):
            if len(row) > 0 and row[0] == question_id:
                # Mettre à jour les colonnes:
                # F: Status → "Répondée"
                # G: Reponse_admin → answer
                # H: Date_Reponse → datetime.now()
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Utiliser cell_list pour mettre à jour plusieurs cellules
                try:
                    questions_sheet.update_cell(idx, 6, "Répondée")  # Colonne F: Status
                    questions_sheet.update_cell(idx, 7, f"{answer} (par {admin_name})")  # Colonne G: Réponse
                    questions_sheet.update_cell(idx, 8, current_time)  # Colonne H: Date
                    
                    logger.info(f"✅ Question {question_id} mise à jour avec la réponse")
                except Exception as e:
                    logger.error(f"Erreur update_cell: {e}")
                
                return
        
        logger.warning(f"Question {question_id} non trouvée")
        
    except Exception as e:
        logger.error(f"Erreur Google Sheets: {e}")
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recherche une candidate par son nom"""
    user = update.effective_user
    
    # Récupérer le nom depuis la commande
    # Format: /rechercher Fatima
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "❌ Format incorrect!\n"
            "Utilisez: /rechercher [nom]\n\n"
            "Exemple: /rechercher Fatima",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    search_name = " ".join(context.args)  # Permet les noms avec plusieurs mots
    
    try:
        # Chercher la candidate dans la feuille "Candidates"
        candidate_data = get_candidate_by_name(search_name)
        
        if not candidate_data:
            await update.message.reply_text(
                f"❌ Candidate '{search_name}' non trouvée",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        # Récupérer ses questions
        questions = get_candidate_questions(candidate_data['telegram_id'])
        
        # Construire le message
        message = f"""
📋 **DÉTAILS DE LA CANDIDATE**

👤 **Nom:** {candidate_data['full_name']}
🌍 **Nationalité:** {candidate_data['nationality']}
💼 **Métier:** {candidate_data['position']}
📅 **Inscrite:** {candidate_data['start_time'].split('T')[0]}

━━━━━━━━━━━━━━━━━━━━━━━━

📚 **DÉTAILS DE L'INTERVIEW:**
👉 Expérience antérieure: {candidate_data['experience']}
👉 Temps disponible: {candidate_data['technical_skills']}
👉 Motivation: {candidate_data['motivation']}
👉 Engagement 3 ans: {candidate_data['availability']}

━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Ajouter les questions
        if questions:
            message += f"\n💬 **SES QUESTIONS** ({len(questions)}):\n\n"
            for i, q in enumerate(questions, 1):
                status_emoji = "✅" if q['status'] == "Répondée" else "⏳"
                message += f"""{i}️⃣ **Q:** {q['question']}
{status_emoji} **Status:** {q['status']}"""
                
                if q['status'] == "Répondée":
                    message += f"\n📝 **Réponse:** {q['answer']}\n"
                else:
                    message += "\n"
                
                message += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        else:
            message += "\n✅ Aucune question posée pour le moment\n"
        
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await update.message.reply_text(
            f"❌ Erreur lors de la recherche: {str(e)}",
            reply_markup=ReplyKeyboardRemove()
        )

def get_candidate_by_name(search_name: str) -> dict:
    """Cherche une candidate par son nom"""
    try:
        sheet = get_sheet()
        if not sheet:
            return None
        
        all_values = sheet.get_all_values()
        
        # Chercher par correspondance partielle (insensible à la casse)
        search_lower = search_name.lower()
        
        for row in all_values[1:]:  # Ignorer l'header
            if len(row) > 1:
                candidate_name = row[1].lower()  # Colonne B: Nom_Complet
                if search_lower in candidate_name or candidate_name in search_lower:
                    return {
                        'full_name': row[1] if len(row) > 1 else '',
                        'nationality': row[2] if len(row) > 2 else '',
                        'telegram_id': row[3] if len(row) > 3 else '',
                        'position': row[4] if len(row) > 4 else '',
                        'experience': row[5] if len(row) > 5 else '',
                        'technical_skills': row[6] if len(row) > 6 else '',
                        'motivation': row[7] if len(row) > 7 else '',
                        'availability': row[8] if len(row) > 8 else '',
                        'start_time': row[9] if len(row) > 9 else ''
                    }
        
        return None
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return None


def get_candidate_questions(telegram_id: str) -> list:
    """Récupère toutes les questions d'une candidate"""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            return []
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        
        try:
            questions_sheet = sh.worksheet("Questions")
        except:
            return []
        
        all_values = questions_sheet.get_all_values()
        candidate_questions = []
        
        for row in all_values[1:]:  # Ignorer l'header
            if len(row) > 2 and str(row[2]) == str(telegram_id):  # Colonne C: Telegram_ID
                candidate_questions.append({
                    'id': row[0] if len(row) > 0 else '',
                    'question': row[3] if len(row) > 3 else '',
                    'date': row[4] if len(row) > 4 else '',
                    'status': row[5] if len(row) > 5 else '',
                    'answer': row[6] if len(row) > 6 else ''
                })
        
        return candidate_questions
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return []

async def reponses_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche un résumé de toutes les candidates"""
    user = update.effective_user
    
    try:
        # Récupérer toutes les candidates
        sheet = get_sheet()
        if not sheet:
            await update.message.reply_text("❌ Erreur: Google Sheets non accessible")
            return
        
        all_values = sheet.get_all_values()
        
        if len(all_values) <= 1:  # Juste l'header
            await update.message.reply_text("✅ Aucune candidate inscrite pour le moment")
            return
        
        # Construire la liste
        candidates = []
        for idx, row in enumerate(all_values[1:], start=1):  # Ignorer l'header
            if len(row) > 1:
                candidate = {
                    'num': idx,
                    'full_name': row[1] if len(row) > 1 else 'Unknown',
                    'nationality': row[2] if len(row) > 2 else '',
                    'position': row[4] if len(row) > 4 else '',
                    'telegram_id': row[3] if len(row) > 3 else '',
                    'date_inscrite': row[9].split('T')[0] if len(row) > 9 else ''
                }
                candidates.append(candidate)
        
        if not candidates:
            await update.message.reply_text("✅ Aucune candidate inscrite pour le moment")
            return
        
        # Construire le message
        message = f"""
📊 **RÉSUMÉ DE TOUTES LES CANDIDATES**

📈 Total inscrites: {len(candidates)}
📅 Mise à jour: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for candidate in candidates:
            message += f"""{candidate['num']}️⃣ **{candidate['full_name']}**
   🌍 {candidate['nationality']} | 💼 {candidate['position']}
   📱 ID: {candidate['telegram_id']}
   📅 Inscrite: {candidate['date_inscrite']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Ajouter des statistiques
        stats = get_statistics()
        message += f"""
📊 **STATISTIQUES:**
✅ Entretiens complétés: {stats['total_candidates']}
💬 Questions posées: {stats['total_questions']}
📋 Questions en attente: {stats['pending_questions']}
✔️ Questions répondues: {stats['answered_questions']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Utilisez `/rechercher [nom]` pour voir les détails d'une candidate
"""
        
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await update.message.reply_text(
            f"❌ Erreur lors de la récupération des données: {str(e)}",
            reply_markup=ReplyKeyboardRemove()
        )

def get_statistics() -> dict:
    """Récupère les statistiques globales"""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            return {
                'total_candidates': 0,
                'total_questions': 0,
                'pending_questions': 0,
                'answered_questions': 0
            }
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SHEET_ID)
        
        # Compter les candidates
        candidates_sheet = sh.sheet1
        candidates_values = candidates_sheet.get_all_values()
        total_candidates = len(candidates_values) - 1  # Ignorer l'header
        
        # Compter les questions
        try:
            questions_sheet = sh.worksheet("Questions")
            questions_values = questions_sheet.get_all_values()
            
            total_questions = 0
            pending_questions = 0
            answered_questions = 0
            
            for row in questions_values[1:]:  # Ignorer l'header
                if len(row) > 0:
                    total_questions += 1
                    if len(row) > 5:
                        if row[5] == "En attente":
                            pending_questions += 1
                        elif row[5] == "Répondée":
                            answered_questions += 1
            
            return {
                'total_candidates': max(0, total_candidates),
                'total_questions': total_questions,
                'pending_questions': pending_questions,
                'answered_questions': answered_questions
            }
        
        except:
            return {
                'total_candidates': max(0, total_candidates),
                'total_questions': 0,
                'pending_questions': 0,
                'answered_questions': 0
            }
    
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return {
            'total_candidates': 0,
            'total_questions': 0,
            'pending_questions': 0,
            'answered_questions': 0
        }


def save_to_google_sheet(candidate_data: dict) -> None:
    """Enregistre dans Google Sheets"""
    try:
        sheet = get_sheet()
        if sheet:
            row_data = [
                candidate_data.get('candidate_id', ''),
                candidate_data.get('full_name', ''),
                candidate_data.get('nationality', ''),
                candidate_data.get('telegram_id', ''),
                candidate_data.get('position', ''),
                candidate_data.get('experience', ''),
                candidate_data.get('technical_skills', ''),
                candidate_data.get('motivation', ''),
                candidate_data.get('availability', ''),
                candidate_data.get('start_time', ''),
                candidate_data.get('end_time', '')
            ]
            
            sheet.insert_row(row_data, index=2) 
            logger.info("✅ Données enregistrées dans Google Sheets")
    except Exception as e:
        logger.error(f"Erreur Google Sheets: {e}")

def main() -> None:
    """Démarre le bot"""
    
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ ERREUR: TOKEN non défini!")
        print("Définissez TELEGRAM_BOT_TOKEN")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # ============================================
    # Handler 1: INTERVIEW (/start flow)
    # ============================================
    interview_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, interview_start)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            NATIONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nationality)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            TECHNICAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_technical)],
            MOTIVATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_motivation)],
            AVAILABILITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_availability)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # ============================================
    # Handler 2: QUESTIONS (/question et /repondre)
    # ============================================
    question_handler = ConversationHandler(
        entry_points=[
            CommandHandler("question", question_command),
            CommandHandler("repondre", repondre_command)
        ],
        states={
            ASKING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)],
            ANSWERING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # ============================================
    # Ajouter les handlers au bot
    # ============================================
    app.add_handler(interview_handler)
    app.add_handler(question_handler)
    
    # Admin commands (pas de ConversationHandler - réponses directes)
    app.add_handler(CommandHandler("admin_questions", admin_questions))
    app.add_handler(CommandHandler("rechercher", search_command))
    app.add_handler(CommandHandler("reponses", reponses_command))
    
    print("✅ Bot démarré...")
    app.run_polling()


if __name__ == '__main__':
    main()
