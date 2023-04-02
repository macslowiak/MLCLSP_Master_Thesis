import os

def __wygeneruj_folder(sciezka_folderu):
    try:
        os.makedirs(sciezka_folderu)
        print("Utworzono folder o nazwie: " , sciezka_folderu)
    except FileExistsError:
        print("Folder o nazwie: " , sciezka_folderu ,  " istnieje")


sciezki_folderow = [
    'bom_jedno_wyjscie',
    'bom_wiele_wyjsc'
]

for sciezka_folderu in sciezki_folderow:
    __wygeneruj_folder(sciezka_folderu + '/dane_wejsciowe')
    __wygeneruj_folder(sciezka_folderu + '/modele')