""" Перевірка відстані між містами. 

# TO DO: 
* визначити на основі декларацій міста реєстрації/фактичного проживання
* перевірити, чи є задеклароване майно з адресою у вказаних містах
* якщо ні, знайти lat, long задекларованих об'єктів та місця реєст/прожив.
* перевірити, чи різниця в межах 100 км.

@hp0404, 23.06.2019
"""

from geopy.distance import great_circle

def distance_great_circle(pow, pol):
    pow_centre = (pow[0], pow[1])
    accommodation = (pol[0], pol[1])
    return great_circle(pow_centre, accommodation).km

def distance_evaluation(dist):
    if dist >= 100:
        print(f'На {dist-100} км. перевищує допустиму межу')
    else:
        print(f'Відстань між точками -- {dist}, що на {100-dist} км. менше від крайньої точки')
        

if __name__ == "__main__":

    pow, pol = (50.4501, 30.5234), (50.4025, 33.3847)
    dist = distance_great_circle(pow, pol)
    distance_evaluation(dist)