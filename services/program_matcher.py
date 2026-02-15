"""
Сервис для подбора образовательных программ
"""
from typing import List, Dict, Any
from services.llm_service import LLMService
from utils.data_loader import data_loader
from utils.institute_validator import institute_validator
from utils.logger import logger

class ProgramMatcher:
    """Класс для подбора образовательных программ"""
    
    def __init__(self):
        self.llm = LLMService()
    
    def find_best_program(self, user_data: dict, institute_codes: List[str]) -> str:
        """Найти наиболее подходящую программу"""
        try:
            # Загружаем программы для выбранных институтов
            programs = data_loader.get_programs_by_institutes(institute_codes)
            
            # Фильтруем по бюджету, если нужно
            if user_data.get('budget_only'):
                programs = data_loader.filter_programs_by_budget(programs, budget_only=True)
            
            # Фильтруем по статусу иностранного студента
            is_foreign = user_data.get('is_foreign', False)
            programs = data_loader.filter_programs_by_foreign(programs, is_foreign=is_foreign)
            
            if not programs:
                return "К сожалению, не найдено подходящих программ по вашим критериям."
            
            # Формируем промпт для LLM
            prompt = self._build_matching_prompt(user_data, programs, institute_codes)
            
            # Генерируем ответ
            result = self.llm.generate_response(prompt)
            
            # Валидируем и исправляем названия институтов
            result = institute_validator.validate_and_fix_response(result, institute_codes)
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при подборе программы: {e}", exc_info=True)
            return "Извините, произошла ошибка при подборе программы. Попробуйте позже."
    
    def find_alternative_programs(self, user_data: dict, previous_recommendation: str) -> str:
        """Найти альтернативные программы"""
        try:
            institute_codes = user_data.get('institutes', [])
            programs = data_loader.get_all_programs()
            
            # Фильтруем программы
            if user_data.get('budget_only'):
                programs = data_loader.filter_programs_by_budget(programs, budget_only=True)
            
            is_foreign = user_data.get('is_foreign', False)
            programs = data_loader.filter_programs_by_foreign(programs, is_foreign=is_foreign)
            
            # Получаем все уникальные названия институтов из программ
            all_institute_names = set()
            for program in programs:
                inst_code = program.get("institute", "")
                if inst_code:
                    # Получаем полное название по коду
                    inst_name = data_loader.get_institute_name(inst_code)
                    if inst_name:
                        all_institute_names.add(inst_name)
            
            institute_names_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(sorted(all_institute_names))])
            
            prompt = f"""
Ты консультант приёмной комиссии Казанского Федерального Университета. Абитуриент предварительно определился с итоговой программой для обучения в КФУ, 
тебе нужно подобрать ещё 2 альтернативные программы обучения в КФУ, которые также могут подойти этому абитуренту.

Подбери ещё 2 образовательные программы из институтов, которые подойдут этому абитуренту на основе его ответов на вопросы и интересов. 
Не выбирай ту же программу, что и в первый раз! ВЫБЕРИ ИМЕННО ТЕ ПРОГРАММЫ, КОТОРЫЕ ЕСТЬ В СПИСКЕ ПРОГРАММ НИЖЕ!

ДОСТУПНЫЕ ИНСТИТУТЫ (используй ТОЛЬКО эти названия, без изменений):
{institute_names_list}

КРИТИЧЕСКИ ВАЖНО - ПРАВИЛА ИСПОЛЬЗОВАНИЯ НАЗВАНИЙ:
1. Для каждой программы укажи ТОЧНОЕ название института из списка выше
2. НЕ изменяй, НЕ сокращай и НЕ перефразируй названия
3. НЕ выдумывай новые названия институтов
4. Скопируй название БУКВА В БУКВУ из списка выше

Формат ответа для каждой программы (СТРОГО соблюдай):
[ТОЧНОЕ НАЗВАНИЕ ИНСТИТУТА ИЗ СПИСКА ВЫШЕ]

Образовательная программа:
- Название: [название из списка программ]
- Код: [код из списка программ]
- Описание: [описание программы]
- Количество мест: [бюджет/контракт из списка]

Объяснение, почему она подойдёт: [твое объяснение]

Оценка шанса поступления: [оценка]

Входные данные:
Резюме абитурента:
{self._format_user_resume(user_data)}

Выбранная ранее программа:
{previous_recommendation}

Все доступные программы:
{self._format_programs(programs)}
"""
            result = self.llm.generate_response(prompt)
            
            # Валидируем ответ (для альтернативных программ проверяем все институты)
            all_codes = data_loader._data.get("institutes", {}).keys()
            result = institute_validator.validate_and_fix_response(result, list(all_codes))
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при подборе альтернативных программ: {e}", exc_info=True)
            return "Извините, произошла ошибка. Попробуйте позже."
    
    def _build_matching_prompt(self, user_data: dict, programs: List[Dict], institute_codes: List[str]) -> str:
        """Построение промпта для подбора программы"""
        import json
        
        # Получаем названия институтов
        institute_names = [data_loader.get_institute_name(code) for code in institute_codes]
        
        resume = self._format_user_resume(user_data)
        programs_json = json.dumps(programs, ensure_ascii=False, indent=2)
        
        # Формируем список названий для промпта
        institute_names_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(institute_names)])
        
        prompt = f"""
Ты консультант приёмной комиссии Казанского Федерального Университета. Твоя задача - на основе информации о пользователе, 
его ответах на вопросы, а также выбранного ранее экспертной системой института подобрать ОДНУ наиболее подходящую образовательную 
программу из списка программ этого института.

Для этого проанализируй информацию о пользователе и описание учебных программ института / институтов, которые выбрала экспертная система, 
и подбери наиболее подходящую программу, где этому студенту будет интересно учиться!

ДОСТУПНЫЕ ИНСТИТУТЫ (используй ТОЛЬКО эти названия, без изменений):
{institute_names_list}

КРИТИЧЕСКИ ВАЖНО - ПРАВИЛА ИСПОЛЬЗОВАНИЯ НАЗВАНИЙ:
1. В ответе НА ПЕРВОЙ СТРОКЕ укажи ТОЧНО одно из названий выше
2. НЕ изменяй, НЕ сокращай и НЕ перефразируй названия
3. НЕ выдумывай новые названия институтов
4. Скопируй название БУКВА В БУКВУ из списка выше

Входные данные:
{resume}

Также продумай подробное объяснение, почему ты выбрал именно такую программу

Формат ответа (СТРОГО соблюдай этот формат):
[ТОЧНОЕ НАЗВАНИЕ ИНСТИТУТА ИЗ СПИСКА ВЫШЕ - СКОПИРУЙ БУКВА В БУКВУ]

Образовательная программа:
- Название: [название из списка программ]
- Код: [код из списка программ]
- Описание: [описание программы]
- Количество мест: [бюджет/контракт из списка]

Объяснение, почему программа подойдёт: [твое объяснение]

Оценка шанса поступления: [оценка на основе баллов ЕГЭ]

Образовательные программы, из которых нужно выбрать одну:
{programs_json}
"""
        return prompt
    
    def _format_user_resume(self, user_data: dict) -> str:
        """Форматирование резюме пользователя"""
        parts = []
        parts.append("Краткое резюме абитуриента:")
        
        if user_data.get('about'):
            parts.append(f"Кратко об абитуриенте и его интересах: {user_data['about']}")
        if user_data.get('profession'):
            parts.append(f"Видение будущей профессии: {user_data['profession']}")
        if user_data.get('subjects'):
            parts.append(f"Предметы с хорошей успеваемостью в школе: {user_data['subjects']}")
        if user_data.get('activities'):
            parts.append(f"Внеучебная деятельность в школе: {user_data['activities']}")
        
        if user_data.get('interest_area'):
            parts.append(f"\nЧто интересно студенту в области: {user_data['interest_area']}. ВАЖНО: Обрати внимание на эту область, на её основе и выбери программу")
        
        if user_data.get('personal_questions'):
            parts.append("\nДополнительные вопросы и ответы, уточняющие образовательную программу пользователя:")
            for i, (q, a) in enumerate(user_data['personal_questions'], 1):
                parts.append(f"{i}. {q} - {a}")
        
        parts.append(f"\nИнностранный абитуриент: {'Да' if user_data.get('is_foreign') else 'Нет'}")
        if user_data.get('is_foreign'):
            parts.append("(Если это иностранный абитуриент, то ищи программы для приёма иностранных граждан)")
        
        if user_data.get('exams'):
            parts.append(f"\nДанные о результатах ЕГЭ - также учти их!")
            parts.append(f"Сдаваемые предметы ЕГЭ: {', '.join(user_data['exams'])}")
            if user_data.get('exams_score'):
                parts.append(f"Балл ЕГЭ: {user_data['exams_score']}. На основе этого балла по данным из твоих знаний оцени шанс поступления")
        else:
            parts.append("\n⚠️ Абитуриент еще не сдал ЕГЭ. Учти это при подборе программы.")
        
        return "\n".join(parts)
    
    def _format_programs(self, programs: List[Dict]) -> str:
        """Форматирование списка программ"""
        import json
        return json.dumps(programs, ensure_ascii=False, indent=2)
