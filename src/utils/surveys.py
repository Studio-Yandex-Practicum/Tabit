from src.schemas.survey import SurveyAnswerCreate


class Surveys:
    def __init__(self, item: SurveyAnswerCreate):
        self.item = item

    def survey_type(self):
        match self.item.survey_list_id:
            case 1:
                return self.lusher()
            case 2:
                return self.etkind()

    def lusher(self):
        if self.item.answers == [1, 2, 3, 4, 5, 6]:
            return {'result': 'good'}
        return {'result': 'bad'}

    def etkind(self):
        return {'result': 'bad'}
