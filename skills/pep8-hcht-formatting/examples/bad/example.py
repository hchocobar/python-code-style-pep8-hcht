#!/usr/bin/env python3
"""Example of code with intentional formatting violations.

This file demonstrates common violations for pep8-hcht-formatting rules.
"""

def load_config(path):
    return {"host":"localhost","port":8080}
def connect(host,port):
    result=host+":"+str(port)
    print(f"Connecting to {result}")
    return True


class UserService:

    def __init__(self, base_url):
        self.base_url = base_url


    def get_user(self, user_id):
        return {"id":user_id}


    def list_users(self):
        return [{"id":1,"name":"Bob"}]
