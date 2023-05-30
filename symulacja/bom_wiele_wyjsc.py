import gc

import data_recorder
import solver
from generatory import bom_generator
from generatory import data_generator
from generatory import mlclsp_model_generator
from datetime import datetime



def modyfikuj_dane_wejsciowe(bom, liczba_wyrobow, liczba_okresow, liczba_maszyn):
    dane_wejsciowe = data_generator.wygeneruj_dane(liczba_wyrobow, liczba_okresow, liczba_maszyn, bom)
    return dane_wejsciowe


def symulacja(dane_wejsciowe):
    # modele
    mlclsp_model = mlclsp_model_generator.mlclsp_model(dane_wejsciowe)
    mlclsp_partie_model = mlclsp_model_generator.mlclsp_partie_model(dane_wejsciowe)
    mlclsp_strumien_model = mlclsp_model_generator.mlclsp_strumien_model(dane_wejsciowe)

    # rozwiazanie
    rozwiazanie_mlclsp = solver.rozwiaz(mlclsp_model, 300)
    if not solver.czy_model_wykonalny_wynik_rozny_od_zera(rozwiazanie_mlclsp):
        print(datetime.now(), 'Model niewykonalny. Podjęcie kolejnej próby...')
        return [rozwiazanie_mlclsp]
    rozwiazanie_mlclsp_partie = solver.rozwiaz(mlclsp_partie_model, 3600)
    if not solver.czy_model_wykonalny_wynik_rozny_od_zera(rozwiazanie_mlclsp_partie):
        print(datetime.now(), 'Model niewykonalny. Podjęcie kolejnej próby...')
        return [rozwiazanie_mlclsp, rozwiazanie_mlclsp_partie]
    rozwiazanie_mlclsp_strumien = solver.rozwiaz(mlclsp_strumien_model, 7200)
    return [rozwiazanie_mlclsp, rozwiazanie_mlclsp_partie, rozwiazanie_mlclsp_strumien]


def czy_model_wykonalny(dane_wejsciowe, liczba_wyrobow, bom,
                        rozwiazane_modele, sciezka_zapisu, numer_modelu, nazwa_pliku_z_rozwiazaniem):
    if solver.czy_modele_wykonalne_wynik_rozny_od_zera(rozwiazane_modele):
        for model in rozwiazane_modele:
            data_recorder.zapisz_model(model, liczba_wyrobow, sciezka_zapisu, numer_modelu)
            data_recorder.zapisz_rozwiazanie(model, dane_wejsciowe, sciezka_zapisu, nazwa_pliku_z_rozwiazaniem,
                                             numer_modelu)
        data_recorder.zapisz_graf_bom(bom, sciezka_zapisu, liczba_wyrobow, numer_modelu)
        data_recorder.zapisz_dane_wejsciowe(dane_wejsciowe, sciezka_zapisu, liczba_wyrobow, numer_modelu)
        return True
    else:
        print(datetime.now(), 'Model niewykonalny. Podjęcie kolejnej próby...')
        return False


# DANE WEJSCIOWE

nazwa_pliku_z_rozwiazaniem = 'bom_wiele_wyjsc'
sciezka_zapisu = data_generator.__stworz_sciezke_zapisu(nazwa_pliku_z_rozwiazaniem)
zbior_liczba_wyrobow = [5, 10, 15, 20, 25]
maksymalna_ilosc_wyrobow_w_warstwie = 5
minimalna_ilosc_wyrobow_w_warstwie = 1
prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami = 25
liczba_okresow = 3
liczba_maszyn = 3
liczba_modeli = 10
powiekszanie_liczby_maszyn = 0

# DANE WEJSCIOWE

print('Rozpoczynam symulacje dla wyrobów z BOM dla wielu wyjść dla każdego produktu...')
for liczba_wyrobow in zbior_liczba_wyrobow:
    for numer_modelu in range(0, liczba_modeli):
        wykonalny = False
        while not wykonalny:
            gc.collect()

            bom = bom_generator.wygeneruj_bom(
                liczba_wyrobow,
                maksymalna_ilosc_wyrobow_w_warstwie,
                minimalna_ilosc_wyrobow_w_warstwie,
                prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami
            )

            dane_wejsciowe = modyfikuj_dane_wejsciowe(bom, liczba_wyrobow, liczba_okresow, liczba_maszyn)
            rozwiazane_modele = symulacja(dane_wejsciowe)
            wykonalny = czy_model_wykonalny(dane_wejsciowe, liczba_wyrobow, bom, rozwiazane_modele,
                                            sciezka_zapisu, numer_modelu, nazwa_pliku_z_rozwiazaniem)

        print(datetime.now(), 'Wygenerowano wyniki dla liczby wyrobów: ' + str(liczba_wyrobow)
              + ' Model: ' + str(numer_modelu + 1) + '/' + str(liczba_modeli))
    liczba_maszyn += powiekszanie_liczby_maszyn
