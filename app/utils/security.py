from pwdlib import PasswordHash

password_hash=PasswordHash.recommended()


def hash_password(password:str)->str:
    """ generate hashed password and return that hashed password """
    hash=password_hash.hash(password)
    return hash

def verify_password(plain_password:str,hashed_password:str)->bool:
    """ verify the password and return the boolean value """

    return password_hash.verify(plain_password,hashed_password)

