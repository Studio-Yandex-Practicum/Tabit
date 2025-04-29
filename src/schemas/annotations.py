from datetime import date, timedelta
from typing import Annotated, Optional

from pydantic import AfterValidator, Field, HttpUrl, StringConstraints

from src.schemas.validators.admin_company import check_date_earlier_than_today

from .constants import Default, Length, MiscConstants

"""Аннотации для дат и ссылок"""
date_and_validation = Annotated[date, AfterValidator(check_date_earlier_than_today)]
url_to_string = Annotated[HttpUrl, AfterValidator(str)]

"""Аннотации для базовых полей"""
NameField = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME),
]
OptionalNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME),
]
CompanyNameField = Annotated[
    str, StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_COMPANY)
]
OptionalCompanyNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_COMPANY),
]
UserNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME),
]
PlaceField = Annotated[
    str, StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_NAME)
]
OptionalPlaceField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_NAME),
]
TitleField = Annotated[
    str, StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_NAME)
]
OptionalTitleField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_NAME),
]
TagField = Annotated[
    str, StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME)
]

"""Аннотации для описаний и текстов"""
DescriptionField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_DESCRIPTION_COMPANY),
]
TextField = Annotated[str, StringConstraints(max_length=Length.MAX_TEXT_LENGTH)]
AddressField = Annotated[str, StringConstraints(max_length=Length.MAX_TEXT_LENGTH)]
CommentTextField = Annotated[
    str, StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_TEXT_LENGTH)
]
MessageTextField = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_TEXT_LENGTH),
]
FeedbackField = Annotated[str, StringConstraints(max_length=Length.MAX_TEXT_LENGTH)]
VotingTextField = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_TEXT_LENGTH, max_length=Length.MAX_TEXT_LENGTH),
]
FeedbackQuestionField = Annotated[str, StringConstraints(max_length=Length.MAX_TEXT_LENGTH)]

"""Аннотации для телефонных номеров и Telegram"""
PhoneNumberField = Annotated[
    Optional[str],
    StringConstraints(
        min_length=Length.MIN_TEXT_LENGTH,
        max_length=Length.MAX_PHONE_LENGTH,
    ),
]
TelegramUsernameField = Annotated[
    Optional[str],
    StringConstraints(
        min_length=Length.MIN_TELEGRAMM_USERNAME, max_length=Length.MAX_TELEGRAM_USERNAME
    ),
]

"""Аннотации для ссылок и аватаров"""
AvatarLinkField = Annotated[Optional[url_to_string], Field(max_length=Length.MAX_FILE_LINK_LENGTH)]

"""Аннотации для лицензий"""
LicenseNameField = Annotated[
    str, StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME)
]
OptionalLicenseNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME),
]
LicenseTermField = Annotated[timedelta, Field(ge=timedelta(**Default.LICENSE_TERM))]
OptionalLicenseTermField = Annotated[
    Optional[timedelta], Field(ge=timedelta(**Default.LICENSE_TERM))
]

"""Аннотации для счетчиков и пагинации"""
CountField = Annotated[int, Field(gt=MiscConstants.ZERO)]
OptionalCountField = Annotated[Optional[int], Field(gt=MiscConstants.ZERO)]
PageField = Annotated[Optional[int], Field(ge=Default.MIN_PAGE_SIZE)]
PageSizeField = Annotated[Optional[int], Field(ge=Default.MIN_PAGE_SIZE, le=Default.MAX_PAGE_SIZE)]
