import data_recorder
import solver
from generatory import bom_generator
from generatory import data_generator
from generatory import mlclsp_model_generator


def symulacja(nazwa_pliku_z_rozwiazaniem, sciezka_zapisu, liczba_wyrobow,
              maksymalna_ilosc_wyrobow_w_warstwie, minimalna_ilosc_wyrobow_w_warstwie,
              prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami, liczba_okresow, liczba_maszyn, iteracja):
    bom = bom_generator.wygeneruj_bom_dla_liczby_polaczen_wychodzacych_rownej_jeden(
        liczba_wyrobow,
        maksymalna_ilosc_wyrobow_w_warstwie,
        minimalna_ilosc_wyrobow_w_warstwie,
        prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami
    )

    dane_wejsciowe = data_generator.wygeneruj_dane(liczba_wyrobow, liczba_okresow, liczba_maszyn, bom)

    dane_wejsciowe.zapotrzebowanie = data_generator.wygeneruj_zapotrzebowanie(liczba_wyrobow, liczba_okresow, [0, 1], [0.85, 0.15])
    dane_wejsciowe.czas_przezbrojenia = data_generator.wygeneruj_czasy_przezbrajania_dla_czasu(
        liczba_wyrobow, liczba_maszyn, dane_wejsciowe.zbior_maszyn_z_przypisanymi_wyrobami, 0.2
    )
    dane_wejsciowe.czas_produkcji = data_generator.wygeneruj_czas_produkcji_dla_czasu(
        liczba_wyrobow, liczba_maszyn, dane_wejsciowe.zbior_maszyn_z_przypisanymi_wyrobami, 0.1
    )

    # modele
    mlclsp_model = mlclsp_model_generator.mlclsp_model(dane_wejsciowe)
    mlclsp_partie_model = mlclsp_model_generator.mlclsp_partie_model(dane_wejsciowe)
    mlclsp_strumien_model = mlclsp_model_generator.mlclsp_strumien_model(dane_wejsciowe)

    # rozwiazanie
    rozwiazanie_mlclsp = solver.rozwiaz(mlclsp_model)
    rozwiazanie_mlclsp_partie = solver.rozwiaz(mlclsp_partie_model)
    rozwiazanie_mlclsp_strumien = solver.rozwiaz(mlclsp_strumien_model)
    rozwiazane_modele = [rozwiazanie_mlclsp, rozwiazanie_mlclsp_partie, rozwiazanie_mlclsp_strumien]

    if (solver.czy_modele_wykonalne(rozwiazane_modele)):
        for model in rozwiazane_modele:
            data_recorder.zapisz_model(model, liczba_wyrobow, sciezka_zapisu)
            data_recorder.zapisz_rozwiazanie(model, dane_wejsciowe, sciezka_zapisu, nazwa_pliku_z_rozwiazaniem)
        data_recorder.zapisz_graf_bom(bom, sciezka_zapisu, liczba_wyrobow)
        data_recorder.zapisz_dane_wejsciowe(dane_wejsciowe, sciezka_zapisu, liczba_wyrobow)
    else:
        iteracja += 1
        print('Nie udało się odnaleźć rozwiązania. Obecna iteracja: ' + str(iteracja), end='\r')
        return symulacja(nazwa_pliku_z_rozwiazaniem, sciezka_zapisu, liczba_wyrobow,
                  maksymalna_ilosc_wyrobow_w_warstwie, minimalna_ilosc_wyrobow_w_warstwie,
                  prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami, liczba_okresow, liczba_maszyn, iteracja)

print('Rozpoczynam symulacje dla wyrobów z BOM dla jednego wyjścia dla każdego produktu...')

nazwa_pliku_z_rozwiazaniem = 'bom_jedno_wyjscie'
sciezka_zapisu = data_generator.__stworz_sciezke_zapisu(nazwa_pliku_z_rozwiazaniem)
zbior_liczba_wyrobow = [5, 10, 15, 20, 25, 30]
maksymalna_ilosc_wyrobow_w_warstwie = 5
minimalna_ilosc_wyrobow_w_warstwie = 1
prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami = 60
liczba_okresow = 4
liczba_maszyn = 3

for liczba_wyrobow in zbior_liczba_wyrobow:
    symulacja(nazwa_pliku_z_rozwiazaniem, sciezka_zapisu, liczba_wyrobow,
              maksymalna_ilosc_wyrobow_w_warstwie, minimalna_ilosc_wyrobow_w_warstwie,
              prawdopodobienstwo_utworzenia_polaczenia_miedzy_wyrobami, liczba_okresow, liczba_maszyn, 0)
    print('Wygenerowano wyniki dla liczby wyrobów: ' + str(liczba_wyrobow))
    liczba_maszyn += 3