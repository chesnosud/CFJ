<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="static/logo.png" alt="Project logo"></a>
</p>

<h3 align="center">Відкриваємо дані: @chesnosud</h3>

---

## 📝 ЗМІСТ
- [Про репозиторій](#about)
- [Встановлення](#getting_started)
- [Використання](#usage)

## 🧐 Про репозиторій <a name = "about"></a>

Репозиторій містить скрипти, котрі допомагають в роботі аналітикам нашої команди.

З одного боку, це робота з арі проекту Канцелярської сотні — [«Декларації»](https://declarations.com.ua/).

*Під час створення профайлів ми збираємо та аналізуємо вміст майнових декларацій, і цей процес значно пришвидшується, якщо ми маємо короткі довідки з акутальними посиланнями та інформацією про кількість об'єктів (не)рухомого майна та наявність подарунків.*

З іншого боку, це отримання відкритої інформації, що публікується державними органами, та перетворення її в придатний до роботи формат.

Сподіваємося, що цей репозиторій стане в пригоді зацікавленим судовою реформою.  



## 🏁 Встановлення <a name = "getting_started"></a>

Для роботи слід встановити зовнішні бібліотеки (ми радимо використовувати віртуальні середовища): 

```
$ python -m venv chesnosud_venv
$ source chesnosud_venv/Scripts/activate
$ pip install -r requirements.txt
```

## 🎈 Використання <a name="usage"></a>

Кожен скрипт виконується з терміналу та має автоматично згенеровану сторінку --help:

```
$ python chesnosud/declarations.py --help
$ python chesnosud/assessments.py --help
$ python chesnosud/relatives.py --help
$ python chesnosud/fired.py --help
```

Приклад отримання декларацій:

```
$ python chesnosud/declarations.py -v data/raw/declarations.xlsx
```
