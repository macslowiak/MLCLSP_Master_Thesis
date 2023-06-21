import os

def __wygeneruj_folder(sciezka_folderu):
    try:
        os.makedirs(sciezka_folderu)
        print("Utworzono folder o nazwie: " , sciezka_folderu)
    except FileExistsError:
        print("Folder o nazwie: " , sciezka_folderu ,  " istnieje")


sciezki_folderow = [
    'struktura_z_montazem',
    'struktura_ogolna',
    'zmiana_liczby_maszyn',
    'bom_struktura_seryjna'
    'bom_struktura_seryjna_ciezki_przypadek'
]

for sciezka_folderu in sciezki_folderow:
    __wygeneruj_folder(sciezka_folderu + '/dane_wejsciowe')
    __wygeneruj_folder(sciezka_folderu + '/modele')