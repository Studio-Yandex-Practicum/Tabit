from src.schemas.survey import SurveyAnswerCreate


class Surveys:
    """
    Класс для расчетов результатов тестов.
    """

    def __init__(self, item: SurveyAnswerCreate):
        self.item = item

    def survey_type(self):
        """
        Метод для соотношения теста с логикой нужного теста.
        """
        match self.item.survey_list_id:
            case 1:
                return self.lusher()
            case 2:
                return self.etkind()

    def lusher(self):
        """
        Метод для расчета результата теста Люшера.
        """
        if self.item.answers == [1, 2, 3, 4, 5, 6]:
            return {'result': 'good'}
        return {'result': 'bad'}

    def etkind(self):
        """
        Метод для расчета результата теста Эткинда.
        """
        return {'result': 'bad'}

    def overall(self):
        """
        Метод для расчета окончательного результата всех тестов.
        """
        return {'result': 'good'}
