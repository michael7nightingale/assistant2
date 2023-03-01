import speech_recognition as sr
import pyaudio
import os
from gtts import gTTS
import random
import file_data_manager as FDM
from playsound import playsound
from threading import Thread
import time


class Assistant:
    def __new__(cls, *args, **kwargs):  # элементарный конструктор класса
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, index=1):    # элементарный инициализатор класса
        self.recognizer = sr.Recognizer()
        self.data = FDM.config_data
        self.phrases = []
        self.source = None
        self.threadAwait_flag = False
        self.threadAwait = Thread(target=self.breakout, daemon=True).start()

    def execute(self):
        if self.threadAwait_flag:
            return
        if not FDM.isRegistrated():
            self.name, self.age, self.keyword = self.register()
        else:
            self.name, self.age, self.keyword = FDM.get_user_info()
        self.answer(f"Привет, {self.name}")

    # проверка на регистрацию -> регистрация
    def register(self):
        if not FDM.isRegistrated():
            self.answer(response='Привет, давай познакомимся!', continue_target='service')
            self.answer(response='Как тебя зовут?', continue_target='service')
            while True:
                try_name = self.listen(objective="service")
                if try_name.isalpha():
                    self.answer(response='Отлично! Сколько тебе лет?', continue_target='service')
                    break
                else:
                    self.answer(response='Не понимаю! Как тебя зовут?', continue_target='service')
            while True:
                try_age = self.listen(objective="service")
                if try_age.isdigit() and 9 < int(try_age) < 100:
                    self.answer(response='Отлично! Придумай кодовое слово?', continue_target='service')
                    break
                else:
                    self.answer(response='Не понимаю! Сколько тебе лет?', continue_target='service')
            while True:
                try_keyword = self.listen(objective="service")
                if try_keyword.isalpha() and try_keyword != try_name:
                    self.answer(response='Отлично! Регистрация завершена! Скажите что-нибудь', continue_target='service')
                    break
                else:
                    self.answer(response='Не понимаю! Придумай кодовое слово?', continue_target='service')
            session = FDM.register(try_name, int(try_age), try_keyword)
            return session

    def listen(self, objective='commands'):   # метод прослушивания команд
        continue_target = objective
        # если все в штатном режиме, и пользователь произносит фразу из списка команд
        try:
            if self.source is None:
                with sr.Microphone() as self.source:
                    audio = self.recognizer.listen(source=self.source, timeout=4, phrase_time_limit=4)
                    text = self.recognizer.recognize_google(audio, language='ru_RU')
            else:
                with sr.Microphone() as self.source:
                    audio = self.recognizer.listen(source=self.source, timeout=4, phrase_time_limit=4)
                    text = self.recognizer.recognize_google(audio, language='ru_RU')
            self.phrases = self.phrases + [text]
            if objective == 'commands':
                return self.matchText(text)
            elif objective == 'service':
                return text
        # если ошибка неразборчивой речи
        except sr.UnknownValueError:
            return self.answer(random.choice(self.data['commands']["misunderstand"]['response']),
                               continue_target=continue_target)
        # если ошибка ожидания (молчание)
        except sr.WaitTimeoutError:
            return self.answer(random.choice(self.data['commands']['silence']['response']),
                               continue_target=continue_target)

    # поиск фразы в триггерах - ответ
    def matchText(self, phrase: str):   # распознает команды
        # проходимся по каждой команде из бд
        for command in self.data['commands']:
            # проверка на наличие слова-триггера в списке триггеров команды (триггер = спусковой крючок)
            if phrase.lower().strip() in self.data['commands'][command]["trigger"]:
                if command in FDM.commands_functions_dict:
                    response = FDM.commands_functions_dict[command]()
                else:
                    response = random.choice(self.data['commands'][command]['response'])
                continue_ = False if command == 'goodbye' else True
                return self.answer(response, continue_=continue_)     # вызов метода ответа с флагом продолжения
        return self.answer("Я вас не понимаю")

    def answer_text(self, response,  continue_target='commands', continue_=True,):
        # print(response.title())
        if continue_:   # если любая команда кроме goodbye
            if continue_target == 'commands':  # если слушаем команды
                self.listen(objective=continue_target)
            else: pass   # если слушаем служебные команды
        # else:   # если команда goodbye
        #     exit()
        self.phrases = self.phrases + [response]

    # отдельный метод ответа позволяет в будущем посылать ответ в динамик
    def answer(self, response, continue_target='commands', continue_=True,):
        # self.answer_text(response=response)
        audio_text = gTTS(text=response, lang='ru', slow=False)
        audio_text.save('response.mp3')
        playsound('response.mp3')
        self.phrases = self.phrases + [response]
        os.remove('response.mp3')
        # решение о продолжении прослушивания команд
        if continue_:
            if continue_target == 'commands':
                self.listen()
            else: pass
        else: self.threadAwait_flag = True

    def breakout(self):
        while True:
            if self.threadAwait_flag:
                self.execute()
            else:
                time.sleep(3)

    def change_breakout(self):
        self.threadAwait_flag = not self.threadAwait_flag

    # def __setattr__(self, key, value, function="show_messages"):
    #     print("assistseattr")
    #     if key == 'phrases':
    #         print('phr', value)
    #         # self.show_messages(value)
    #
    #     object.__setattr__(self, key, value)

# ass = Assistant()
# ass.execute()

