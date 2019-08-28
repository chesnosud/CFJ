# Автоматизація збору статичної інформації в профайлах суддів ЧФС.

## Крок 1. Майнові декларації
[`declarations.py`](https://github.com/hp0404/CFJ/blob/master/declarations.py) дозволяє отримати лінки на щорічні майнові декларації (використовуючи API declarations.com.ua). 
Отримані результати зберігаються в окремий файл в папці [results](https://github.com/hp0404/CFJ/tree/master/results).

[`declaration_salaries.py`](https://github.com/hp0404/CFJ/blob/master/declaration_salaries.py) дозволяє отримати зведену таблицю доходів з декларації НАЗК.

## Крок 2. Кваліфоцінювання
[`kvalif.py`](https://github.com/hp0404/CFJ/blob/master/kvalif.py) парсить новини з результатами кваліфу, оформлених в html таблички. Отримані відповіді узгоджує із `календарем оцінювання` та записує в ексель файл. 

[`kvalif_analysis.ipynb`](https://github.com/hp0404/CFJ/blob/master/kvalif_analysis.ipynb) містить низку функцій для підрахунку результатів моніторингу.

## Крок 3. Акти 
[`fired.py`](https://github.com/hp0404/CFJ/blob/master/fired.py) дозволяє автоматизувати оновлення інформації по звільнених працівниках. 

## Крок 4. Реєстр родинних зв'язків

[`родині звязки.ipynb`](https://github.com/hp0404/CFJ/blob/master/%D1%80%D0%BE%D0%B4%D0%B8%D0%BD%D1%96%20%D0%B7%D0%B2%D1%8F%D0%B7%D0%BA%D0%B8.ipynb) отримує таблицю родинних зв'язків
