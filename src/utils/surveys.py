from typing import List

from src.schemas.survey import SurveyAnswerCreate

"""
Заготовка для дальнейшего развития логики тестов.
"""


class Surveys:
    """
    Класс для расчетов результатов тестов.
    """
    @staticmethod
    def survey_type(answers: List[SurveyAnswerCreate]):
        """
        Метод для соотношения теста с логикой нужного теста.
        """
        result = []
        for item in answers:
            match item.test_number:
                case 1:
                    item = Surveys.lusher(item)
                case 2:
                    item = Surveys.etkind(item)
            result.append(item)
        overall_result = Surveys.overall(result)
        return result, overall_result

    @staticmethod
    def lusher(item: SurveyAnswerCreate):
        """
        Метод для расчета результата теста Люшера.
        """
        if item.answers == [1, 2, 3, 4, 5, 6]:
            setattr(item, 'results', 'good')
            return item
        setattr(item, 'results', 'bad')
        return item

    @staticmethod
    def etkind(item: SurveyAnswerCreate):
        """
        Метод для расчета результата теста Эткинда.
        """
        setattr(item, 'results', 'bad')
        return item

    @staticmethod
    def overall(items: List[SurveyAnswerCreate]):
        """
        Метод для расчета суммарного результата всех тестов.
        """
        summary = []
        for item in items:
            obj = item.model_dump()
            summary.append(obj['results'])
        if summary == ['good', 'bad']:
            return {'result': 'good'}
        return {'result': 'bad'}
