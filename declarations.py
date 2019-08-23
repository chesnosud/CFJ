# Лінки з майнових декларацій

import requests
import pandas as pd


def get_links(person):
    """ Лінки з сайтів nazk, declarations 
    person: ПІБ
    """
    r = requests.get(f"https://declarations.com.ua/search?q={person}&format=opendata", timeout=30).json()
    count = int(r['results']['paginator']['count'])

    container = []
    for i in range(count):
        position = r['results']['object_list'][i]['infocard']['position']
        declaration_year = r['results']['object_list'][i]['infocard']['declaration_year']
        document_type = r['results']['object_list'][i]['infocard']['document_type']
        created_date = r['results']['object_list'][i]['infocard']['created_date']
        is_corrected = r['results']['object_list'][i]['infocard']['is_corrected']
        try:
            raw_source = r['results']['object_list'][i]['raw_source']['url']
        except:
            raw_source = r['results']['object_list'][i]['raw_source']['declaration']['url']

        resulting_string = f'{position}|{declaration_year}|{document_type}|{is_corrected}|{created_date}|{raw_source}'
        container.append(resulting_string)

    new_list = [tuple(i.split('|')) for i in reversed(container)]

    df = pd.DataFrame.from_records(new_list, columns=['position', 'declaration_year','document_type','is_corrected', 'created_date', 'url'])
    new_df = df.copy()
    new_df = new_df.loc[new_df['position'].str.contains('суддя|голова', case=False)]
    new_df = new_df.loc[~new_df['document_type'].str.contains("форма змін", case=False)]

    table1 = new_df.loc[new_df.created_date == 'None']
    table2 = new_df.loc[new_df.created_date != 'None']

    table2[['date', 'time']] = table2['created_date'].str.split('T', expand=True)
    table2.drop(['created_date', 'time'], axis=1, inplace=True)
    table2 = table2.sort_values('date').drop_duplicates('date',keep='last')
    table2 = table2.sort_values('declaration_year').drop_duplicates('declaration_year',keep='last')

    final_result = table1.append(table2)
    final_result = final_result.sort_values('declaration_year').drop_duplicates('declaration_year',keep='last')
    final_result.drop(['created_date', 'date', 'document_type', 'is_corrected', 'position'], axis=1, inplace=True)
    final_result['url'] = final_result['url'].str.replace('https://public-api.nazk.gov.ua/v1/declaration/', 'https://public.nazk.gov.ua/declaration/')
    final_result['PIK| LINK'] = final_result[['declaration_year', 'url']].apply(lambda x: '| '.join(x), axis=1)
    final_result.drop(['declaration_year', 'url'],axis=1,inplace=True)
    final_result.to_csv(f"results/{person}.csv", index=False)
    final_result.to_csv()

if __name__ == "__main__":    
    with open('names.txt', encoding='utf-8') as file:
            for person in file.read().splitlines():
                try:
                    get_links(person=person)
                except:
                    with open('results/fails.txt', 'a', encoding='utf-8') as fails:
                        fails.write(f"{person}\n")