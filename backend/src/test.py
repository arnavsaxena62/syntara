from auth import *

string = "wowmyiga"
hashedstring = pwd_context.hash(string)
print(verify_password(hashedstring, string))    