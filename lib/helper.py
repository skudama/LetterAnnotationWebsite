# -*- coding: utf-8 -*-

def get_annotator_url():
    url = u'http://monster.dlsi.uji.es:8081/query/hpo/q='
    url = u'http://localhost:8081/query/hpo/q='

    return url

def get_legends():
    legends = {
        1: {'name': 'Persons and personal relations',
            'color': '#81BEF7'},
        2: {'name': 'Observations', 'color': '#FA5858'},
        3: {'name': 'HPO', 'color': '#BD7AFF'},
        4: {'name': 'Shifters', 'color': '#A9F5A9'},
        5: {'name': 'Modifiers', 'color': '#F4FA58'},
        6: {'name': 'Genes/Anatomy', 'color': '#FF9900'}
    }

    return legends


def get_id_by_color(color):
    legends = {
        '#81BEF7': 1,
        '#FA5858': 2,
        '#BD7AFF': 3,
        '#A9F5A9': 4,
        '#F4FA58': 5,
        '#FF9900': 6,
    }

    return legends[color]


def get_hpo_elements(matches):
    hpo_matches = []
    for match_collection in matches:
        collection = match_collection[1]
        for elem in collection:
            if elem[3] == '#BD7AFF':
                name = elem[2]
                source = elem[4]
                element_type = elem[5]
                score = elem[6]
                CUI = elem[7]

                hpo_matches.append([name, source, element_type, score,
                                   CUI])

    return hpo_matches
