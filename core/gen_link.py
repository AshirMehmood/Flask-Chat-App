from random import choice
import string

def gen_link(lenght=8, chars=string.ascii_letters + string.digits):
    return ''.join([choice(chars) for i in range(lenght)])