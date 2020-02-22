"""
Основна ідея полягає в тому, аби написати ф-цію, котра відмінюватиме 
жіночі та чоловічі ПІБ у родовому відмінку

Як відмінюється :
https://udhtu.edu.ua/wp-content/uploads/2017/08/b7ae096b1e5cedc59c9371524703b474.pdf
"""

# у цьому прикладі закінчення для чол. і жін. однакові,
# але належать до різних словаників; словники слід доповнювати
M_SURNAME_DICT = {
    "енко": "енка"
}

F_SURNAME_DICT = {
    "енко": "енко"
}

# Списки з чол іменами; припускаю, що тут винятковий перелік, 
# і що будь-яке інше ім'я є жіночим
M_NAMES = ["Іван", "Сергій"]
# F_NAMES = []


def _vidminuyvach_prizvyshch(surname, surname_dict):
    """ Внутрішня загальна ф-ція, котра відмінює прізвище """
    
    for zakinchennia in set(surname_dict.keys()):
        if surname.endswith(zakinchennia):
            return surname.replace(zakinchennia, surname_dict.get(zakinchennia))

def rodovyi(pib: str) -> str:
    """ Називний -> Родовий
    
    Examples
    --------
    >>> rodovyi("Іваненко Іван Іванович")
    Іваненка І. І.
    >>> rodovyi("Іваненко Анастасія Сергіївна")
    Іваненко А. С.
    """
    
    surname, name, patr = pib.strip().split(" ")
    
    if name.title() in set(M_NAMES):
        surname = _vidminuyvach_prizvyshch(surname, M_SURNAME_DICT)
    else:
        surname = _vidminuyvach_prizvyshch(surname, F_SURNAME_DICT)
    
    return " ".join([surname, name[0] + ".", patr[0] + "."]).title()