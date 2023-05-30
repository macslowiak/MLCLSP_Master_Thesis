import gc
from pathlib import Path

import numpy
import pandas

import data_recorder
import solver
from generatory import data_generator
from generatory import mlclsp_model_generator
from datetime import datetime


def symulacja(liczba_wyrobow, liczba_maszyn, dane_wejsciowe):
    setattr(dane_wejsciowe, 'zbior_maszyn', numpy.array(list(range(0, liczba_maszyn))))
    setattr(dane_wejsciowe, 'zbior_maszyn_z_przypisanymi_wyrobami',
            data_generator.przypisz_wyroby_do_maszyn_uwzgledniajac_zapotrzebowanie(
                liczba_wyrobow, liczba_maszyn, dane_wejsciowe.bom, dane_wejsciowe.zapotrzebowanie
            ))
    setattr(dane_wejsciowe, 'czas_produkcji',
            data_generator.wygeneruj_czas_produkcji_dla_czasu(
                liczba_wyrobow, liczba_maszyn, dane_wejsciowe.zbior_maszyn_z_przypisanymi_wyrobami, 0.1
            ))
    setattr(dane_wejsciowe, 'czas_przezbrojenia',
            data_generator.wygeneruj_czasy_przezbrajania_dla_czasu(
                liczba_wyrobow, liczba_maszyn, dane_wejsciowe.zbior_maszyn_z_przypisanymi_wyrobami, 0.2
            ))
    setattr(dane_wejsciowe, 'koszt_przezbrojenia',
            data_generator.wygeneruj_koszty_przezbrajania(
                liczba_wyrobow, liczba_maszyn, dane_wejsciowe.zbior_maszyn_z_przypisanymi_wyrobami, 3
            ))
    setattr(dane_wejsciowe, 'dostepnosc_maszyn',
            data_generator.wygeneruj_dostepnosc_maszyn(liczba_maszyn, dane_wejsciowe.zbior_okresow.size))

    # modele
    mlclsp_model = mlclsp_model_generator.mlclsp_model(dane_wejsciowe)
    mlclsp_partie_model = mlclsp_model_generator.mlclsp_partie_model(dane_wejsciowe)
    mlclsp_strumien_model = mlclsp_model_generator.mlclsp_strumien_model(dane_wejsciowe)

    # rozwiazanie
    rozwiazanie_mlclsp = solver.rozwiaz(mlclsp_model, 1000)
    if not solver.czy_model_wykonalny(rozwiazanie_mlclsp):
        return [rozwiazanie_mlclsp]
    rozwiazanie_mlclsp_partie = solver.rozwiaz(mlclsp_partie_model, 1000)
    if not solver.czy_model_wykonalny(rozwiazanie_mlclsp_partie):
        return [rozwiazanie_mlclsp, rozwiazanie_mlclsp_partie]
    rozwiazanie_mlclsp_strumien = solver.rozwiaz(mlclsp_strumien_model, 1000)
    return [rozwiazanie_mlclsp, rozwiazanie_mlclsp_partie, rozwiazanie_mlclsp_strumien]


def czy_model_wykonalny(rozwiazane_modele, dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, nazwa_pliku_z_rozwiazaniem,
                        liczba_prob):
    if solver.czy_modele_wykonalne(rozwiazane_modele):
        for model in rozwiazane_modele:
            data_recorder.zapisz_model(model, liczba_wyrobow, sciezka_zapisu, numer_modelu)
            data_recorder.zapisz_rozwiazanie(model, dane_wejsciowe, sciezka_zapisu, nazwa_pliku_z_rozwiazaniem,
                                             numer_modelu)
        data_recorder.zapisz_dane_wejsciowe(dane_wejsciowe, sciezka_zapisu, liczba_wyrobow, numer_modelu)
        return True
    else:
        print(datetime.now(), 'Nie można rozwiązać modelu po zmianie liczby maszyn dla danych z pliku: ' + nazwa_pliku_z_modelem +
              ' Pozostała ilośc prób: ' + str(liczba_prob))
        return False


# DANE WEJSCIOWE

katalog_z_modelami = str(Path(__file__).parent.parent) + '\\wyniki\\bom_jedno_wyjscie\\dane_wejsciowe\\'

zbior_liczba_wyrobow = [5, 10, 15, 20, 25]  # Zgodne ze schematem 'liczbaWyrobow_numerModelu.pickle'
liczba_modeli = 10

nazwa_pliku_z_rozwiazaniem = 'zmiana_liczby_maszyn'
sciezka_zapisu = data_generator.__stworz_sciezke_zapisu(nazwa_pliku_z_rozwiazaniem)
liczba_maszyn = 3
powiekszanie_liczby_maszyn = 3
liczba_prob_dla_pojedynczego_rozwiazania = 1000

# DANE WEJSCIOWE

print('Rozpoczynam symulacje zmiany liczby maszyn dla danych z katalogu: ' + katalog_z_modelami)

for liczba_wyrobow in zbior_liczba_wyrobow:
    for numer_modelu in range(0, liczba_modeli):
        wykonalny = False
        liczba_prob = liczba_prob_dla_pojedynczego_rozwiazania
        nazwa_pliku_z_modelem = katalog_z_modelami + str(liczba_wyrobow) + '_' + str(numer_modelu) + '.pickle'
        dane_wejsciowe = pandas.read_pickle(nazwa_pliku_z_modelem)
        while not wykonalny:
            gc.collect()
            liczba_prob -= 1
            rozwiazane_modele = symulacja(liczba_wyrobow, liczba_maszyn, dane_wejsciowe)
            wykonalny = czy_model_wykonalny(rozwiazane_modele, dane_wejsciowe, liczba_wyrobow, sciezka_zapisu,
                                            nazwa_pliku_z_rozwiazaniem, liczba_prob)
            if liczba_prob <= 0:
                raise Exception('Przekroczono liczbę prób dla symulacji modelu: ' + nazwa_pliku_z_modelem)

        print(datetime.now(), 'Wygenerowano wyniki dla liczby wyrobów: ' + str(liczba_wyrobow)
              + ' Model: ' + str(numer_modelu + 1) + '/' + str(liczba_modeli))
    liczba_maszyn += powiekszanie_liczby_maszyn
