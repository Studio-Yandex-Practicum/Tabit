from pydantic import BaseModel


class CompanyCreate(BaseModel):
    pass


class CompanyDB(BaseModel):
    pass


class CompanyDBForUser(BaseModel):
    pass


class CompanyUpdate(BaseModel):
    pass


class CompanyUpdateForUser(BaseModel):
    pass
