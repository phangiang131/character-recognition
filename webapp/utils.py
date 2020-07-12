


def get_anime_data(anime_name,anime_mapping,anime_database):
    for d in anime_database:
        if anime_mapping[anime_name] == d['href']:
            return d

def get_image_character_src(name,anime_data,image_mapping):
    data = anime_data
    anime = data['name']
    cha_name = name
    cha_name = cha_name.replace(' ver 2','')
    cha_name = cha_name.replace(' ver 3','')
    if cha_name == 'Bol':
        cha_name = 'Bols'
    if cha_name == 'C.C':
        cha_name = 'C.C.'
    if cha_name == 'Jean LOW':
        cha_name = 'Jean ROWE'
    if cha_name == 'Leila MALKAL':
        cha_name = 'Leila MALCAL'
    if cha_name == 'Second Grade Student Council':
        cha_name = 'Second Grade Student Council Member'
    if cha_name == 'Leila MALKAL':
        cha_name = 'Leila MALCAL'
    if cha_name == 'Shunsuke Otosaka':
        cha_name = 'Shunsuke OTOSAKA'
    if cha_name == 'V.V':
        cha_name = 'V.V.'
    if cha_name == 'Seryu UBIQUITIOUS':
        cha_name = 'Seryu UBIQUITOUS'
    if cha_name == 'kirito':
        cha_name = 'Kirito'
    if cha_name == 'klein':
        cha_name = 'Klein'
    if cha_name == 'yui':
        cha_name = 'Yui'
    if cha_name == 'Komekko' or cha_name == 'Yunyun' :
        return None 
    if anime == 'Angel Beats':
        return None
    if anime == 'date a live':
        return None
#     print(anime)
    character_href = data['character'][cha_name]
    if character_href not in image_mapping.keys():
        return None
    return image_mapping[character_href]