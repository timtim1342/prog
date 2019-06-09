import markovify  # эту хрень должны зачесть, может лучше спросить + heroku?
import urllib.request
import json
import re
from flask import Flask, render_template, request

def wall_requst(offset):  # запрос к VK. тебе надо зарегать приложение и поменять токен
    token = '3cf3970a3cf3970a3cf3970a053c989f7833cf33cf3970a600f9270722177de2420aab4'
    version = '5.92'
    group = '-28122932'
    count = '100'
    posts = ''
    req = urllib.request.Request(
        'https://api.vk.com/method/wall.get?owner_id=%s&offset=%s&count=%s&v=%s&access_token=%s'
        % (group, offset, count, version, token))
    response = urllib.request.urlopen(req)
    result = response.read().decode('utf-8')
    data = json.loads(result)  # немножко jsonа, может быть зачтут как отдельную тему
    #print(data)
    for i in range(len(data['response']['items'])):
        posts = posts + '\n' + data['response']['items'][i]['text']
    return posts

def wr():  # это первая тема API (если без jsona). выкачивает много постов, пишет в один текстовый файл, немного чистит
    with open('p.txt', 'w', encoding='utf-8') as f:
        pass
    for i in range(1, 2001, 100):
        perawki = wall_requst(i)
        result = re.sub(r'[©\[].*','', perawki)  # не нужны авторы
        perawki = re.sub(r'\n{2,5}', '\n', result)  # и много переносов строки.
        with open('p.txt', 'a', encoding='utf-8') as f:
            f.write(perawki)
        with open('p.txt', 'r', encoding='utf-8') as f:
            newtxt = ''
            for line in f:
                if len(line.split()) <= 9 and len(re.findall(r'[\d\\]', line)) == 0:  # не нужны строки длинее 9 и с цифрами
                    newtxt = newtxt + line
        with open('p.txt', 'w', encoding='utf-8') as f:
            f.write(newtxt)

def check_syl(st, num):  # считает слоги по гласным. Князев плак плак
    vow = ['а', 'о', 'э', 'ы', 'и', 'ю', 'я', 'е', 'ё', 'у']
    v = 0
    if st != None:
        for letter in st:
            if letter in vow:
                v += 1
        if v == num:
            return 'OK'  # можно было бы и True
    else:
        return 'NO'  # можно было бы и False

def wr_str():  # из одного делает два txt. в первом только 1 и 3 строчки, во втором 2 и 4. так он лучше следить за ударениями потом
    first_third = ''
    second_last = ''
    with open('p.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if check_syl(line, 9) == 'OK':  # оставляет только с 9 слогами
                first_third = first_third + line
            elif check_syl(line, 8) == 'OK':  # а тут тольско с 8... так что можно было бы и не чистить в начале...
                second_last = second_last + line
    with open('first.txt', 'w', encoding='utf-8') as f:
        f.write(first_third)
    with open('second.txt', 'w', encoding='utf-8') as f:
        f.write(second_last)

def make_model():  # делает модельки для генерации
    with open('first.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    model_1_3 = markovify.NewlineText(text)
    with open('second.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    model_2_4 = markovify.NewlineText(text)
    return model_1_3, model_2_4

def gen_str(word, m, s2='', isWord=False, syl=9, turns=1000):  # тут все сложно я сам не оч. turns и tries вроде бы про одно
    t = 0
    s1 = ''
    if not isWord:  # есть ли слово пользователя в стишке или еще нет
        while check_syl(s1, syl) != 'OK' or s1 == s2:  # проверяет слоги в созданном предл + чтобы оно не повторялось
            s1 = m.make_sentence_with_start(word, strict=False, tries=30)  # пытается создать строчки с word, почему то только в начале
            t += 1
            if t == turns:  # чтобы выходить из бесконечного цикла. для этого turns
                break
        if t == turns:  # если лимит превышен, а слова нет в строчке
            word = ' ' + word
            t = 0
            while check_syl(s1, syl) != 'OK' or word not in s1 or s1 == s2:  # создает любое предложение с 9 или 8 слогами и проверяет есть ли в нем слово
                s1 = m.make_sentence(tries=30)  # ищет только в начале, хотя должен везде
                t += 1
                if t == turns:
                    break
            if t == turns:  # закончились ходы
                while check_syl(s1, syl) != 'OK' or s1 == s2:  # если слова нет, делает просто предложение
                    s1 = m.make_sentence(tries=30)
                return s1, isWord
            else:  # слово оказалось где-то не в начале
                isWord = True
                return s1, isWord
        else:  # слово оказалось в начале
            isWord = True
            return s1, isWord
    else:  # слово уже в какой то строчке раньше, поэтому делает просто строку
        while check_syl(s1, syl) != 'OK' or s1 == s2:
            s1 = m.make_sentence(tries=30)
        return s1, isWord

def gen_pir(word):  # делает пирожок
    m1, m2 = make_model()
    isWord = False
    so, isWord = gen_str(word, m1, isWord=isWord)
    ss, isWord = gen_str(word, m2, isWord=isWord, syl=8)
    st, isWord = gen_str(word, m1, s2=so, isWord=isWord)  # слово пользователя, модель, с какой строчкой не должно повторяться, слово уже есть или нет
    sf, isWord = gen_str(word, m2, s2=ss, isWord=isWord, syl=8)
    pirow = so + '\n' + ss + '\n' + st + '\n' + sf
    return pirow, isWord

def main():
    wr()
    wr_str()

app = Flask(__name__)  # +1 тема

@app.route('/')
def index():
    main()
    if request.args:
        wrd = str(request.args['word'])
        resp, isWord = gen_pir(wrd)
        resp = resp.split('\n')
        return render_template('result.html',isWord=isWord, resp=resp)
    return render_template('index.html')

if __name__ == ('__main__'):
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
