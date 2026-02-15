import telebot
import json
from btns import *
from questions_generator import *
from llm import *


institutes = ["ИВМиИТ", "ИИРСИ", "ИТИС", "ИФ", "ИГиНГТ"]

INSTITUTE_EXAMS = {
    "ИВМиИТ": ["профиль", "русский", "информатика", "физика"],
    "ИИРСИ": ["профиль", "русский", "информатика", "физика"],
    "ИТИС": ["профиль", "русский", "информатика"],
    "ИФ": ["профиль", "русский", "физика"],
    "ИГиНГТ": ["профиль", "русский", "география", "физика"],
    "ИМиМ": ["профиль", "русский", "информатика", "физика"],
    "ХИ": ["химия", "русский", "профиль"],
    "ИФМиБ": ["биология", "русский", "химия"],
    "ИЭБиП": ["биология", "русский", "химия", "география", "профиль"],
    "ИДиПИ": ["профиль", "русский", "литература", "история"],
    "ИПиО": ["биология", "русский", "общество", "профиль"],
    "ИСФНиМК": ["русский", "обществознание", "история", "иностранный"],
    "ИУЭФ": ["профиль", "русский", "обществознание", "информатика"],
    "ЮФ": ["русский", "обществознание", "история", "математика"],
    "ИМОИВ": ["русский", "история", "иностранный", "обществознание"],
    "ИФМК": ["русский", "иностранный", "литература", "обществознание"]
}

def check_institutes_exams(institute, user_exams_text, message):
        flag = False

        r_exams = []
        for exam in INSTITUTE_EXAMS[institute]:
            if exam in user_exams_text:
                r_exams.append(exam)
        if len(r_exams) >= 3:
            flag = True
        return flag
                

user_data = {}
user_areas = {}
user_answers = {}
user_questions = {}
user_dop = {}

bot = telebot.TeleBot("8482909906:AAEZ-OKRTRbY8b_nhB9hZonglkXxXXy4dOM")
@bot.message_handler(commands=['start'])
def start_bot(message):
    user_data[message.chat.id] = []
    user_areas[message.chat.id] = []
    user_answers[message.chat.id] = []
    bot.send_message(message.chat.id, "Добрый день! Это бот экспертной системы, который поможет Вам подобрать подходящую образовательную программу в институтах КФУ!", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Выберите город, в котором Вы хотите учиться", reply_markup=cities_menu)
    bot.register_next_step_handler(message, student_type)


def student_type(message):
    bot.send_message(message.chat.id, "Вы иностранный абитуриент?", reply_markup=menu3)
    bot.register_next_step_handler(message, validate_nul)


def validate_nul(message):
    user_dop[message.chat.id] = {}
    if message.text == 'Да':
        user_dop[message.chat.id]['foreign'] = "Да"
    else:
        user_dop[message.chat.id]['foreign'] = "Нет"
    bot.send_message(message.chat.id, "Выберите уровень образования", reply_markup=level_menu)
    bot.register_next_step_handler(message, validate_first)

def validate_first(message):
    if message.text == 'Бакалавриат' or 'бакалавр' in message.text.lower():
        bot.send_message(message.chat.id, "1. Кратко расскажите о себе. Чем Вы интересуетесь, какие у вас хобби и увлечения?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, validate_steps_0)


def validate_steps_0(message):
        user_answers[message.chat.id].append(message.text)
        bot.send_message(message.chat.id, "2. Представляете ли кем хотите работать в будущем?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, validate_steps_1)


def validate_steps_1(message):
    user_answers[message.chat.id].append(message.text)
    bot.send_message(message.chat.id, "3. По каким предметам была хорошая успеваемость в школе?")
    bot.register_next_step_handler(message, validate_steps_2)


def validate_steps_2(message):
    user_answers[message.chat.id].append(message.text)
    bot.send_message(message.chat.id, "4. Какой внеучебной деятельностью занимались в школе?")
    bot.register_next_step_handler(message, get_pr_status)


def get_pr_status(message):
    user_answers[message.chat.id].append(message.text)
    bot.send_message(message.chat.id, "Вы рассматриваете для обучения только бюджет?", reply_markup=menu3)
    bot.register_next_step_handler(message, ege)


def ege(message):
    if 'да' in message.text.lower():
        user_dop[message.chat.id]["form"] = "budget"
    else:
        user_dop[message.chat.id]["form"] = "contract"
    bot.send_message(message.chat.id, "Какие экзамены ЕГЭ вы сдавали? Укажите через запятую")
    bot.register_next_step_handler(message, ege_ball)

def ege_ball(message):
    user_dop[message.chat.id]['exams'] = message.text.lower()
    bot.send_message(message.chat.id, "Укажите Ваш суммарный бал ЕГЭ за 3 экзамена")
    bot.register_next_step_handler(message, set_ege_ball)

def set_ege_ball(message):
    user_dop[message.chat.id]['exams_ball'] = message.text
    bot.send_message(message.chat.id, "Какая область Вам интересна?", reply_markup=menu1)
    bot.register_next_step_handler(message, validate_institute_step1)



def validate_institute_step1(message):
    user_dop[message.chat.id]['obl'] = message.text
    user_dop[message.chat.id]["int"] = message.text
    if message.text == 'ИТ':
        for ins in institutes[:4]:
            user_areas[message.chat.id].append(ins)
        bot.send_message(message.chat.id, "Вас интересует обучение в области ИТ полностью на английском языке?", reply_markup=menu3)
        bot.register_next_step_handler(message, validate_it0)
    elif message.text == 'Математические науки':
        bot.send_message(message.chat.id, "Что Вам интереснее в математике?", reply_markup=math_menu)
        bot.register_next_step_handler(message, validate_math_1)
    elif message.text == 'Языки':
        bot.send_message(message.chat.id, "Что вам интереснее в изучении языков?", reply_markup=lang_menu)
    elif message.text == 'Науки о Земле':
        bot.send_message(message.chat.id, "Что вам интереснее в области наук о Земле?", reply_markup=earth_science_menu)
        bot.register_next_step_handler(message, validate_earth_1)
    elif message.text == 'Медицина':
        user_data[message.chat.id].append("ИФМиБ")
        choose_program_1(message)
    elif message.text == 'Культура и искусство':
        user_data[message.chat.id].append("ИДиПИ")
        choose_program_1(message)
    elif message.text == 'Науки о человеке и обществе':
        bot.send_message(message.chat.id, "Что вам интереснее в области наук о человеке и обществе?", reply_markup=human_science_menu)
        bot.register_next_step_handler(message, validate_human_1)
    elif message.text == 'Экономика и бизнес':
        bot.send_message(message.chat.id, "Что для Вас интереснее?", reply_markup=business_menu)
        bot.register_next_step_handler(message, validate_iuf)
    elif message.text == 'Инженерные и технические науки':
        bot.send_message(message.chat.id, "Что Вам интереснее в инженерных и технических науках?", reply_markup=technik_menu)
        bot.register_next_step_handler(message, validate_technik_1)
    elif message.text == 'Медиа':
        user_data[message.chat.id].append("ИСФНиМК")
        choose_program_1(message)
    elif message.text == 'Я не знаю':
        user_dop[message.chat.id]['no'] = True
        prompt = ""
        QG = QuestGen(prompt)
        tQuest = QG.gen_no_question()
        quest1, quest2, quest3 = tQuest.split("|")
        user_questions[message.chat.id] = {}
        user_questions[message.chat.id]['questions'] = [quest1, quest2, quest3]
        bot.send_message(message.chat.id, quest1, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, personal_quest_1)


def validate_technik_1(message):
    user_dop[message.chat.id]['obl'] = message.text
    if message.text == 'Робототехника и новые технологии':
        user_data[message.chat.id].append("ИИРСИ")
        choose_program_1(message)
    else:
        user_data[message.chat.id].append("ИФ")
        choose_program_1(message)



def validate_iuf(message):
    user_dop[message.chat.id]["obl"] = message.text
    user_data[message.chat.id].append("ИУЭФ")
    choose_program_1(message)

    
def validate_human_1(message):
    user_dop[message.chat.id]["obl"] = message.text
    if message.text == 'Психология':
        user_data[message.chat.id].append("ИПиО")
        choose_program_1(message)
    elif message.text == 'Юридические науки':
        user_data[message.chat.id].append("ЮФ")
        choose_program_1(message)
    elif message.text == 'Социология':
        user_data[message.chat.id].append("ИСФНиМК")
        choose_program_1(message)
    elif message.text == 'Менеджмент':
        user_data[message.chat.id].append("ИУЭФ")
        choose_program_1(message)
    elif message.text == 'Философия':
        user_data[message.chat.id].append("ИСФНиМК")
        choose_program_1(message)

def validate_earth_1(message):
    user_dop[message.chat.id]["int"] = message.text
    if message.text == 'Экология и Биология':
        bot.send_message(message.chat.id, "Что Вам интереснее?", reply_markup=bio1_menu)
        bot.register_next_step_handler(message, validate_bio)
    elif message.text == 'Физика':
        user_data[message.chat.id].append("ИФ")
        choose_program_1(message)
    elif message.text == 'Биология':
        bot.send_message(message.chat.id, "Что вам интереснее в биологии?", reply_markup=biology_menu)
        bot.register_next_step_handler(message, validate_bio_1)
    elif message.text == 'Химия':
        user_data[message.chat.id].append("ХИ")
        choose_program_1(message)
    elif message.text == 'География и Геология':
        user_data[message.chat.id].append("ИГиНГТ")
        choose_program_1(message)
    


def validate_bio(message):
    user_dop[message.chat.id]["int"] = message.text
    if message.text == 'Биология':
        bot.send_message("Что вам интереснее в области биологии?", reply_markup=biology_menu)
        bot.register_next_step_handler(message, validate_bio_1)
    elif message.text == 'Экология':
        user_data[message.chat.id].append("ИЭБиП")
        choose_program_1(message)
    else:
        choose_program_1(message)


def validate_bio_1(message):
    user_dop[message.chat.id]['obl'] = message.text
    if message.text == 'Прикладные и междисциплинарные исследования в биологии':
        user_data[message.chat.id].append("ИЭБиП")
        choose_program_1(message)
    elif message.text == 'Фундаментальное изучение биологии':
        user_data[message.chat.id].append("ИФМиБ")
        choose_program_1(message)
    else:
        choose_program_1(message)



def validate_lang_1(message):
    user_dop[message.chat.id]['obl'] = message.text
    if message.text == 'Изучение иностранных языков, как средства коммуникации':
        user_data[message.chat.id].append("ИМОиИВ")
        choose_program_1(message)
    elif message.text == 'Изучение языков с точки зрения их культуры и филологии':
        user_data[message.chat.id].append("ИФМК")
        choose_program_1(message)
    else:
        choose_program_1(message)


def validate_math_1(message):
    user_dop[message.chat.id]['obl'] = message.text
    if message.text == 'Прикладные разработки':
        user_data[message.chat.id].append("ИВМиИТ")
        choose_program_1(message)
    elif message.text == 'Наука и исследования':
        user_data[message.chat.id].append("ИВМиИТ")
        user_data[message.chat.id].append("ИМиМ")
        choose_program_1(message)
    elif message.text == 'Педагогика в математике':
        user_data[message.chat.id].append("ИМиМ")
        choose_program_1(message)
    else:
        choose_program_1(message)



def validate_it0(message):
    if message.text == 'Да':
        bot.send_message("Программная инженерия, профиль «Современная разработка программного обеспечения» (код 09.03.04) в институте ИТИС Казанского Федерального Университета.")
    else:
        bot.send_message(message.chat.id, "Что Вам интересно в области ИТ?", reply_markup=menu2)
        bot.register_next_step_handler(message, validate_it1)
    

def validate_it1(message):
    user_dop[message.chat.id]['obl'] = message.text
    if message.text == 'Высокоуровневая разработка':
        user_data[message.chat.id].append("ИВМиИТ")
        user_data[message.chat.id].append("ИТИС")
        choose_program_1(message)
    elif message.text == 'ИБ':
        user_data[message.chat.id].append("ИФ")
        user_data[message.chat.id].apppend("ИВМиИТ")
        choose_program_1(message)
    elif message.text == 'Низкоуровневая разработка':
        user_data[message.chat.id].append("ИИРСИ")
        user_data[message.chat.id].append("ИВМиИТ")
        user_data[message.chat.id].append("ИФ")
        choose_program_1(message)
    elif message.text == 'ИИ':
        bot.send_message(message.chat.id, "Что Вам интереснее в разработке ИИ?", reply_markup=ai_menu)
        bot.register_next_step_handler(message, validate_it_ai_1)
    elif message.text == 'Менеджмент в ИТ':
        user_data[message.chat.id].append("ИВМиИТ")
        user_data[message.chat.id].append("ИИРСИ")
        choose_program_1(message)
    else:
        user_dop[message.chat.id] = []
        user_dop[message.chat.id].append(message.text)
        choose_program_1(message)

    

def validate_it_ai_1(message):
    user_dop[message.chat.id]['obl'] = message.text
    if message.text == "Математическая составляющая":
        user_data[message.chat.id].append("ИВМиИТ")
        choose_program_1(message)
    elif message.text == "Инжиниринг данных":
        user_data[message.chat.id].append("ИТИС")
        choose_program_1(message)
    elif message.text == "Алгоритмы и шаблоны построения ИИ":
        user_data[message.chat.id].append("ИИРСИ")
        user_data[message.chat.id].append("ИВМиИТ")
        choose_program_1(message)
    else:
        choose_program_1(message)



def choose_program_1(message):
    # for inst in user_data[message.chat.id]:
    #     if not check_institutes_exams(inst, user_dop[message.chat.id]['exams'], message):
    #         user_data[message.chat.id].remove(inst)
    if len(user_data[message.chat.id]) == 0:
        bot.send_message(message.chat.id, "К сожалению, сдаваемые Вами экзамены не подходят для поступления на интересущее Вас направление :( \n\nПопробуйте заново /start")
    w = bot.send_message(message.chat.id, "✨ Генерация персональных вопросов...")
    prompt = ''
    for ans in user_answers[message.chat.id]:
        prompt += ans + "\n"

    prompt += f"Интересное для обучения направление: {user_dop[message.chat.id]["int"]}\n\nПеречень институтов в КФУ, где студент может учиться: {''.join(user_data[message.chat.id])}"

    programs = []
    if user_data[message.chat.id] is not None:
        for inst in user_data[message.chat.id]:
            with open("/Users/deniz_mlg/Desktop/Универ/Введение в разработку ИС/kfu_programs_by_institute.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            pr = data["institutes"][inst]["programs"]
            programs.append(json.dumps(pr, ensure_ascii=False))
        programs = "\n".join(programs)
        prompt += f'Приблизительный спектр подходящих студенту образовательных программ, из которых нужно будет выбрать. Твоя задача - составить такие вопросы, чтобы определить, какая из представленных программ может подойти абитуренту: {programs}'

    QG = QuestGen(prompt)
    tQuest = QG.gen4_questions()
    quest1, quest2, quest3, quest4 = tQuest.split("|")
    user_questions[message.chat.id] = {}
    user_questions[message.chat.id]['questions'] = [quest1, quest2, quest3, quest4]
    bot.delete_message(message.chat.id, w.message_id)
    bot.send_message(message.chat.id, quest1, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, personal_quest_1)


def personal_quest_1(message):
    user_questions[message.chat.id]['personal_answers'] = []
    user_questions[message.chat.id]['personal_answers'].append(message.text)
    bot.send_message(message.chat.id, user_questions[message.chat.id]['questions'][1])
    bot.register_next_step_handler(message, personal_quest_2)
    

def personal_quest_2(message):
    user_questions[message.chat.id]['personal_answers'].append(message.text)
    bot.send_message(message.chat.id, user_questions[message.chat.id]['questions'][2])
    bot.register_next_step_handler(message, personal_quest_3)

def personal_quest_3(message):
    user_questions[message.chat.id]['personal_answers'].append(message.text)
    bot.send_message(message.chat.id, user_questions[message.chat.id]['questions'][3])
    bot.register_next_step_handler(message, personal_quest_4)

def personal_quest_4(message):
    user_questions[message.chat.id]['personal_answers'].append(message.text)
    bot.send_message(message.chat.id, "✨ Подбор образовательной программы...")
    builder(message)


def builder(message):
    programs = []
    names = []
    if len(user_data[message.chat.id]) == 0:
        with open("/Users/deniz_mlg/Desktop/Универ/Введение в разработку ИС/kfu_programs_by_institute.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            programs = data
    else:
        for inst in user_data[message.chat.id]:
            with open("/Users/deniz_mlg/Desktop/Универ/Введение в разработку ИС/kfu_programs_by_institute.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            pr = data["institutes"][inst]["programs"]
            if user_dop[message.chat.id].get('form') == 'budget':
                pr = [program for program in pr if program.get('budget_places', 0) > 0]
            name = data["institutes"][inst]["name"]
            names.append(name)
            programs.append(json.dumps(pr, ensure_ascii=False))
    
    programs = "\n".join(programs)
    resume = f"""
Краткое резюме абитурента:
Кратко об абитуренте и его интересах: {user_answers[message.chat.id][0]}
Видение будущей профессии: {user_answers[message.chat.id][1]}
Предметы с хорошей успеваемостью в школе: {user_answers[message.chat.id][2]}
Внеучебная деятельность в школе: {user_answers[message.chat.id][3]}

Что интересно студенту в области: {user_dop[message.chat.id]['obl']} . ВАЖНО Обрати внимание на эту область, на её основе и выбери программу

Дополнительные вопросы и ответы, уточняющие образовательную программу пользователя:
1. {user_questions[message.chat.id]['questions'][0]} - {user_questions[message.chat.id]['personal_answers'][0]}
2. {user_questions[message.chat.id]['questions'][1]} - {user_questions[message.chat.id]['personal_answers'][1]}
3. {user_questions[message.chat.id]['questions'][2]} - {user_questions[message.chat.id]['personal_answers'][2]}
4. {user_questions[message.chat.id]['questions'][3]} - {user_questions[message.chat.id]['personal_answers'][3]}

Инностранный абитуриент: {user_dop[message.chat.id]['foreign']} (Если это иностранный абитурент, то ищи программы для приёма иностранных граждан)

Данные о результатах ЕГЭ - также учти их!
Сдаваемые предметы ЕГЭ: {user_dop[message.chat.id]['exams']} (Если эти прдемты не подойдут, то так и скажи, и не подбирай программу)
Балл ЕГЭ: {user_dop[message.chat.id]['exams_ball']} . На основе этого балла по данным из твоих знаний оцени шанс поступления
"""
    prompt = f"""
Ты консультант приёмной комиссии Казанского Федерального Университета. Твоя задача - на основе информации о пользователи, его ответах на вопросы, а также выбранного ранее экспертной системой инстиута подоборать, ОДНУ наиболее подходящую образовательную программу из списка программ этого института.
Для этого проанализируй информацию о пользователе и описание учебных программ института / институтов, которые выбрала экспертная система, и подбери наиболее походящую программу, где этому студенту будет интересно учиться!
Полное названия институтов выбранных экспертной системой: {"\n".join(names)}
Выбирай СТРОГО по логике!

Входные данные:
{resume}

Также продумай подробное объяснение, почему ты выбрал именно такую программу

Формат ответа:
Название института
Образовательная программа (Название, код, сведения о ней - описание, кол-во мест и т.д)
Объяснение, почему она подойдёт
Оценка шанса ЕГЭ

Образовательные программы, из которых нужно выбрать одну:
{programs}
"""
    model = LLM('yandex')
    result = model.generate_response(prompt)
    bot.send_message(message.chat.id, result, reply_markup=final_show_menu)
    bot.register_next_step_handler(message, end_bot, resume, result)


def end_bot(message, resume, after_program):
    with open("/Users/deniz_mlg/Desktop/Универ/Введение в разработку ИС/kfu_programs_by_institute.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    programs = "\n".join(data)
    if message.text == '✚ Подобрать ещё программы':
        prompt = f"""
Ты консультант приёмной комиссии Казанского Федерального Университета. Абитурент предварительно определился с итоговой программой для обучения в КФУ, тебе нужно подобрать ещё 2 альтернативные программы обучения в КФУ, которые также могут подойти этому абитуренту.
Подбери ещё 2 образовательные программы из институтов, которые подойдут этому абитуренту на основе его ответов на вопросы и интересов. Не выбирай ту же программу, что и в первый раз! ВЫБЕРИ ИМЕННО ТЕ ПРОГРАММЫ, КОТОРЫЕ ЕСТЬ В СПИСКЕ ПРОГРАММ НИЖЕ!
Формат ответа:
Название института
Образовательная программа (Название, код, сведения о ней - описание, кол-во мест и т.д)
Объяснение, почему она подойдёт
Оценка шанса ЕГЭ

Входные данные:
Резюме абитурента:
{resume}
Выбранная ранее программа:
{after_program}
Программы:
{programs}
"""
        w = bot.send_message(message.chat.id, "✨ Подбор альтернативных образовательных программ...")
        model = LLM('yandex')
        result = model.generate_response(prompt)
        bot.delete_message(message.chat.id, w.message_id)
        bot.send_message(message.chat.id, result, reply_markup=final_show_menu)




        
while True:
    bot.polling()
    



    
