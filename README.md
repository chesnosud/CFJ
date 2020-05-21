# Збір даних. - Чесно. Фільтруй суд!

TO-DO
--------
1. структурувати репо за `scripts`, `illustrations`, `data`
2. всякі штуки типу `concat_files` і їм подібні - в `tools.py`
3. для скриптів що викликаються через термінал - click. 
4. загальний рефактор старих файлів
5. зокрема в деклараціях - площа об'єктів, кількість родичів тощо, чи є хоча б одна квартира/будинок

Репозиторій містить файли, що стосуються збору даних для поточної активності ЧФС. 

Тематично їх можна поділити за джерелами:
* Сайти Вищої Ради Правосуддя (старий vrp і тепер вже новий - hcj)
* Сайт Вищої кваліфікаційної комісії суддів України
* Реєстр declarations.com.ua

---

### Акти:
#### Попередній аналіз рішень
* [`hcj_texts.py`](https://github.com/hp0404/CFJ/blob/master/hcj_texts.py) 

#### Звільнення
* [`hcj_fired.py`](https://github.com/hp0404/CFJ/blob/master/hcj_fired.py)
* [`vrp_fired.py`](https://github.com/hp0404/CFJ/blob/master/vrp_fired.py) 

### Декларації: 

* [`declarations_illustration.ipynb`](https://nbviewer.jupyter.org/github/hp0404/CFJ/blob/master/declarations_illustration.ipynb) 
* [`declarations.py`](https://github.com/hp0404/CFJ/blob/master/declarations.py) 

### Кваліфоцінювання
* [`kvalif_analysis.ipynb`](https://nbviewer.jupyter.org/github/hp0404/CFJ/blob/master/kvalif_analysis.ipynb)
* [`kvalif_analysis_prep.py`](https://github.com/hp0404/CFJ/blob/master/kvalif_analysis_prep.py)
* [`kvalif_news.py`](https://github.com/hp0404/CFJ/blob/master/kvalif_news.py)
* [`kvalif_rz.py`](https://github.com/hp0404/CFJ/blob/master/kvalif_rz.py)
