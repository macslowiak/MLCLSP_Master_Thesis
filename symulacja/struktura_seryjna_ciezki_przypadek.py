import gc
from datetime import datetime

import data_recorder
import solver
from generatory import bom_generator
from generatory import data_generator
from generatory import mlclsp_model_generator


def modyfikuj_dane_wejsciowe(bom, liczba_wyrobow, liczba_okresow, liczba_maszyn, liczba_wyrobow_koncowych,
                             ilosc_okresow_poczatkowych):
    dane_wejsciowe = data_generator.wygeneruj_dane(liczba_wyrobow, liczba_okresow, liczba_maszyn, bom)
    zapotrzebowanie = data_generator.wygeneruj_zapotrzebowanie_dla_produkcji_seryjnej(liczba_wyrobow,
                                                                                      liczba_okresow,
                                                                                      liczba_wyrobow_koncowych)
    for i in range(1, ilosc_okresow_poczatkowych + 1):
        zapotrzebowanie[liczba_wyrobow - 1, i] = 0
    setattr(dane_wejsciowe, 'zapotrzebowanie', zapotrzebowanie)
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
    return dane_wejsciowe


def rozwiaz_mlclsp(dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, numer_modelu, nazwa_pliku_z_rozwiazaniem):
    mlclsp_model = mlclsp_model_generator.mlclsp_model(dane_wejsciowe)
    rozwiazanie_mlclsp = solver.rozwiaz_bez_limitu_czasu(mlclsp_model)
    if not solver.czy_model_wykonalny_wynik_rozny_od_zera(rozwiazanie_mlclsp):
        print(datetime.now(), 'Model niewykonalny (mlclsp).')
    data_recorder.zapisz_model(rozwiazanie_mlclsp, liczba_wyrobow, sciezka_zapisu, numer_modelu)
    data_recorder.zapisz_rozwiazanie(rozwiazanie_mlclsp, dane_wejsciowe, sciezka_zapisu,
                                     nazwa_pliku_z_rozwiazaniem,
                                     numer_modelu)


def rozwiaz_mlclsp_partie(dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, numer_modelu, nazwa_pliku_z_rozwiazaniem):
    mlclsp_partie_model = mlclsp_model_generator.mlclsp_partie_model(dane_wejsciowe)
    rozwiazanie_mlclsp_partie = solver.rozwiaz_bez_limitu_czasu(mlclsp_partie_model)
    if not solver.czy_model_wykonalny_wynik_rozny_od_zera(rozwiazanie_mlclsp_partie):
        print(datetime.now(), 'Model niewykonalny (mlclsp-partie).')
    data_recorder.zapisz_model(rozwiazanie_mlclsp_partie, liczba_wyrobow, sciezka_zapisu, numer_modelu)
    data_recorder.zapisz_rozwiazanie(rozwiazanie_mlclsp_partie, dane_wejsciowe, sciezka_zapisu,
                                     nazwa_pliku_z_rozwiazaniem,
                                     numer_modelu)


def rozwiaz_mlclsp_strumien(dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, numer_modelu, nazwa_pliku_z_rozwiazaniem):
    mlclsp_strumien_model = mlclsp_model_generator.mlclsp_strumien_model(dane_wejsciowe)
    rozwiazanie_mlclsp_strumien = solver.rozwiaz_bez_limitu_czasu(mlclsp_strumien_model)
    if not solver.czy_model_wykonalny_wynik_rozny_od_zera(rozwiazanie_mlclsp_strumien):
        print(datetime.now(), 'Model niewykonalny (mlclsp-strumień).')
    data_recorder.zapisz_model(rozwiazanie_mlclsp_strumien, liczba_wyrobow, sciezka_zapisu, numer_modelu)
    data_recorder.zapisz_rozwiazanie(rozwiazanie_mlclsp_strumien, dane_wejsciowe, sciezka_zapisu,
                                     nazwa_pliku_z_rozwiazaniem,
                                     numer_modelu)


def zapisz_wynik(dane_wejsciowe, liczba_wyrobow, bom, sciezka_zapisu, numer_modelu):
    data_recorder.zapisz_graf_bom(bom, sciezka_zapisu, liczba_wyrobow, numer_modelu)
    data_recorder.zapisz_dane_wejsciowe(dane_wejsciowe, sciezka_zapisu, liczba_wyrobow, numer_modelu)


# DANE WEJSCIOWE

nazwa_pliku_z_rozwiazaniem = 'bom_struktura_seryjna_ciezki_przypadek'
sciezka_zapisu = data_generator.__stworz_sciezke_zapisu(nazwa_pliku_z_rozwiazaniem)
zbior_liczba_wyrobow = [5, 10, 15, 20, 25]
liczba_okresow = 10
liczba_maszyn = 3
liczba_modeli = 1
powiekszanie_liczby_maszyn = 3
liczba_wyrobow_koncowych = 1
ilosc_okresow_poczatkowych = 1

# DANE WEJSCIOWE

print('Rozpoczynam symulacje dla wyrobów z BOM dla struktury seryjnej...')
for liczba_wyrobow in zbior_liczba_wyrobow:
    for numer_modelu in range(0, liczba_modeli):
        bom = bom_generator.wygeneruj_bom_dla_struktury_seryjnej(liczba_wyrobow)
        dane_wejsciowe = modyfikuj_dane_wejsciowe(bom, liczba_wyrobow, liczba_okresow, liczba_maszyn,
                                                  liczba_wyrobow_koncowych, ilosc_okresow_poczatkowych)
        rozwiaz_mlclsp(dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, numer_modelu,
                       nazwa_pliku_z_rozwiazaniem)
        gc.collect()
        rozwiaz_mlclsp_partie(dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, numer_modelu,
                              nazwa_pliku_z_rozwiazaniem)
        gc.collect()
        rozwiaz_mlclsp_strumien(dane_wejsciowe, liczba_wyrobow, sciezka_zapisu, numer_modelu,
                                nazwa_pliku_z_rozwiazaniem)
        gc.collect()
        zapisz_wynik(dane_wejsciowe, liczba_wyrobow, bom, sciezka_zapisu, numer_modelu)

        print(datetime.now(), 'Wygenerowano wyniki dla liczby wyrobów: ' + str(liczba_wyrobow)
              + ' Model: ' + str(numer_modelu + 1) + '/' + str(liczba_modeli))
    liczba_maszyn += powiekszanie_liczby_maszyn