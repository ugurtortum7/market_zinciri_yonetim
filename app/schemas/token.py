from pydantic import BaseModel

class Token(BaseModel):
    """
    Login işlemi sonrası kullanıcıya dönecek olan token modelidir.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    JWT token'ın içindeki veriyi temsil eder (payload).
    """
    username: str | None = None