<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://scontent.fiev22-1.fna.fbcdn.net/v/t31.0-8/13417008_1756934504552318_310776707786659683_o.png?_nc_cat=100&_nc_sid=09cbfe&_nc_ohc=AnPIwUfczt0AX8ZzNIv&_nc_ht=scontent.fiev22-1.fna&oh=40a63081ffd38fb2f62d6b806a5843ea&oe=5EF7EC70" alt="Project logo"></a>
</p>

<h3 align="center">Відкриваємо дані: @chesnosud</h3>

<div align="center">

  [![Status](https://img.shields.io/badge/status-active-success.svg)]() 

</div>

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