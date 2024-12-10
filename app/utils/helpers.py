from passlib.context import CryptContext

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pass(plain):
    return pwd_context.hash(plain)

def verify_pass(hash,plain):
    return pwd_context.verify(plain,hash)