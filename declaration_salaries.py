import requests, sys
import pandas as pd

def salary(url: str, fname: str):
    """
    Отримую зведену таблицю доходів з декларації НАЗК, 
    результат зберігаю в ексель-файл.
    """
    
    r = requests.get(url).json()
    results = []
    
    # step_11 містить інформацію про доходи
    for k in r['data']['step_11'].keys():
        records = [
            r['data']['step_11'][k]['person'], # декларант має знач. '1'
            r['data']['step_11'][k]['objectType'], # вид доходу
            r['data']['step_11'][k]['sizeIncome'] # розмір (вартість)            
        ]
        results.append(records)

    df = pd.DataFrame(data=results, columns=['Декларант', 'Вид доходу', 'Розмір'])
    df['Розмір'] = df['Розмір'].astype(int)
    
    # якщо цікавить саме гроші саме судді
    df = df.loc[df['Декларант'] == '1']

    final_table = df.pivot_table(
        index='Вид доходу',
        margins=True,
        margins_name='Загалом',
        aggfunc=sum
    )

    final_table.to_excel(f'{fname}.xlsx')

if __name__ == "__main__":
    argv = sys.argv[1:]
    url, fname = (argv[0], argv[1])
    salary(url, fname)