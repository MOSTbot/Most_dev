import hashlib


class MessageText:
    def __init__(self, message_text: (str, iter) = None):
        self.__message_text = message_text

    def get_message_text(self):
        return self.__message_text

    def set_message_text(self, message_text):
        if not isinstance(message_text, str) and not iter(message_text):
            raise ValueError('message.text может быть либо строковым значением либо итерируемым объектом!')
        self.__message_text = message_text


class HashData:
    @staticmethod
    def hash_data(string: (str, int)) -> str:
        hash_obj = hashlib.sha256(str(string).encode())
        return hash_obj.hexdigest()
