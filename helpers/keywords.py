keywords_list = {
  "27": {
    "Assassinato": 9826,
    "Filme independente": 281237,
    "Violência": 281405,
    "Fantasma": 162846,
    "Zumbi": 12377,
    "Sobrenatural": 6152,
    "Monstro": 1299,
    "Vampiro": 3133,
    "Assassino em série": 10714,
    "Filme cult": 34117,
    "Psicopata": 6259,
    "Floresta": 9720,
    "Halloween": 3335,
    "Possessão": 9712,
    "Maldição": 10541
  },
  "28": {
    "Violência": 281405,
    "Explosão": 14601,
    "Artes Marciais": 779,
    "Polícia": 6149,
    "Seqüestro": 1930,
    "Super-herói": 9715,
    "Soldado": 13065,
    "Traição": 10085,
    "Guerreiro": 192913,
    "Gangster": 3149,
    "Carro": 33885,
    "Espião": 470,
    "Robô": 14544
  },
  "35": {
    "Amor": 9673,
    "Amizade": 6054,
    "Sátira": 8201,
    "Festa": 8508,
    "Musical": 12990,
    "Sexo": 267122,
    "Natal": 207317,
    "Stand-Up": 9716,
    "Paródia": 9755,
    "Adolescente": 14643,
    "Casamento": 13027,
    "Praia": 966,
    "Escola": 10873,
    "Embriaguez": 188991,
    "Dinheiro": 10594
  },
  "18": {
    "Baseado em livro": 818,
    "Assassinato": 9826,
    "Filme independente": 281237,
    "Amor": 9673,
    "Americano": 14638,
    "Adolescente": 14643,
    "Família": 18035,
    "Vingança": 9748,
    "Sequestro": 1930,
    "Baseado em história real": 9672,
    "Infidelidade": 1326,
    "Prisão": 378,
    "Gay": 264384,
    "Gravidez": 3725,
    "Suicídio": 236
  },
  "878": {
    "Alien": 9951,
    "Super-herói": 9715,
    "Robô": 14544,
    "Espaço": 252634,
    "Ciêntista": 14760,
    "Monstro": 1299,
    "Viagem no tempo": 4379,
    "Nave Espacial": 252937,
    "Futurista": 9685,
    "Baseado em livro": 818,
    "Pós apocalíptico": 272793,
    "Filme cult": 34117,
    "Deserto": 18034,
    "Zumbi": 12377,
    "Militar": 162365
  },
  "14": {
    "Magia": 2343,
    "Baseado em livro": 818,
    "Monstro": 1299,
    "Sobrenatural": 6152,
    "Super-herói": 9715,
    "Floresta": 5774,
    "Bruxa": 616,
    "Conto de fadas": 3205,
    "Bem x Mal": 269233,
    "Espada e Feitiçaria": 234213,
    "Dragão": 12554,
    "Vampiro": 3133,
    "Caçador": 414,
    "Caverna": 1964,
    "Maldição": 10541
  },
  "16": {
    "Amizade": 6054,
    "Super-herói": 9715,
    "Violência": 281405,
    "Robô": 14544,
    "Monstro": 1299,
    "Baseado em quadrinhos": 9717,
    "Magia": 2343,
    "Baseado em mangá": 13141,
    "Animal": 267848,
    "Cartoon": 6513,
    "Escola": 10873,
    "Adolescente": 14643,
    "Batalha": 14643,
    "Crianças": 249094,
    "Fábulas": 161757
  },
  "53": {
    "Assassinato": 9826,
    "Polícia": 6149,
    "Seqüestro": 1930,
    "Tortura": 13006,
    "Traição": 10085,
    "Detetive": 703,
    "Psicopata": 6259,
    "Chantagem": 1936,
    "Resgate": 10084,
    "Criminoso": 15009
  }
}

keywords_unique = [6149, 6152, 8201, 252937, 9748, 9755, 162846, 3133, 162365, 188991, 267848, 3149, 12377, 33885, 9826, 616, 18034, 6259, 18035, 10873, 3205, 3725, 5774, 281237, 15009, 12990, 703, 264384, 13006, 14544, 252634, 9951, 13027, 234213, 236, 249094, 3335, 14601, 13065, 779, 12554, 1299, 4379, 2343, 10541, 14638, 1326, 818, 14643, 8508, 281405, 34117, 13141, 10594, 10084, 10085, 6513, 267122, 378, 1930, 1936, 192913, 272793, 414, 6054, 14760, 1964, 269233, 966, 9672, 9673, 207317, 470, 9685, 10714, 161757, 9712, 9715, 9716, 9717, 9720]


def get_keyword_name(genre, val):
    for key, value in keywords_list.get(str(genre)).items():
        if int(val) == value:
            return key
