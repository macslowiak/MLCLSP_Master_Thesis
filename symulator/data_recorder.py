import csv
import pickle

from generatory import bom_generator


def __zamien_kropke_na_przecinek(x):
    return (str(x).replace('.', ','))


def zapisz_model(model, liczba_wyrobow, sciezka_zapisu):
    nazwa_modelu = model.ModelName
    model.write(sciezka_zapisu + '\\modele\\' + nazwa_modelu + '_' + str(liczba_wyrobow) + '.lp')


def zapisz_graf_bom(bom, sciezka_zapisu, liczba_wyrobow):
    graf = bom_generator.narysuj_bom(bom)
    graf.savefig(sciezka_zapisu + '\\dane_wejsciowe\\' + str(liczba_wyrobow))


def zapisz_dane_wejsciowe(dane_wejsciowe, sciezka_zapisu, liczba_wyrobow):
    plik_z_danymi_wejsciowymi = sciezka_zapisu + '\\dane_wejsciowe\\' + str(liczba_wyrobow)
    with open(plik_z_danymi_wejsciowymi + '.pickle', 'wb') as plik:
        pickle.dump(dane_wejsciowe, plik, protocol=pickle.HIGHEST_PROTOCOL)
    with open(plik_z_danymi_wejsciowymi + '.txt', 'a') as plik:
        plik.write(dane_wejsciowe.__str__())


def zapisz_rozwiazanie(model, dane_wejsciowe, sciezka_zapisu, nazwa_pliku_z_rozwiazaniem):
    nazwa_modelu = model.ModelName
    liczba_wyrobow = str(dane_wejsciowe.zbior_wyrobow.size)

    plik_z_rozwiazaniem = sciezka_zapisu + '\\' + nazwa_pliku_z_rozwiazaniem + '.csv'

    with open(plik_z_rozwiazaniem, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
        writer.writerow(['Model', 'Liczba wyrobów', 'Zmienna', 'Wyrób i', 'Okres', 'Maszyna', 'Wyrób j', 'Wartość'])

        writer.writerow([nazwa_modelu, liczba_wyrobow, 'Liczba ograniczeń', '', '', '', '', model.NumConstrs])
        writer.writerow([nazwa_modelu, liczba_wyrobow, 'Liczba zmiennych', '', '', '', '', model.NumVars])
        writer.writerow([nazwa_modelu, liczba_wyrobow, 'Liczba zmiennych binarnych', '', '', '', '', model.NumBinVars])
        writer.writerow([nazwa_modelu, liczba_wyrobow, 'Czas rozwiązywania', '', '', '', '',
                         __zamien_kropke_na_przecinek(round(model.Runtime, 2))])
        writer.writerow([nazwa_modelu, liczba_wyrobow, 'Liczba iteracji', '', '', '', '', int(model.IterCount)])
        writer.writerow([nazwa_modelu, liczba_wyrobow, 'Rozwiązanie', '', '', '', '',
                         __zamien_kropke_na_przecinek(round(model.ObjBound, 2))])

        if nazwa_modelu == 'MLCLSP':
            __zapisz_rozwiazanie_dla_podstawowego_mlclsp(writer, model, dane_wejsciowe, nazwa_modelu, liczba_wyrobow)
        else:
            __zapisz_rozwiazanie_dla_rozszerzonego_mlclsp(writer, model, dane_wejsciowe, nazwa_modelu, liczba_wyrobow)


def __zapisz_rozwiazanie_dla_podstawowego_mlclsp(writer, model, dane_wejsciowe, nazwa_modelu, liczba_wyrobow):
    for wyrob_i in dane_wejsciowe.zbior_wyrobow:
        for okres in dane_wejsciowe.zbior_okresow:
            writer.writerow(
                [nazwa_modelu, liczba_wyrobow, 'x', wyrob_i, okres, '', '', __zamien_kropke_na_przecinek(round(
                    model.getVarByName('x(' + str(wyrob_i) + ',' + str(okres) + ')').x, 1
                ))])
            writer.writerow(
                [nazwa_modelu, liczba_wyrobow, 'I', wyrob_i, okres, '', '', __zamien_kropke_na_przecinek(round(
                    model.getVarByName('I(' + str(wyrob_i) + ',' + str(okres) + ')').x, 1
                ))])
            writer.writerow(
                [nazwa_modelu, liczba_wyrobow, 'y', wyrob_i, okres, '', '', __zamien_kropke_na_przecinek(round(
                    model.getVarByName('y(' + str(wyrob_i) + ',' + str(okres) + ')').x, 1
                ))])


def __zapisz_rozwiazanie_dla_rozszerzonego_mlclsp(writer, model, dane_wejsciowe, nazwa_modelu, liczba_wyrobow):
    for wyrob_i in dane_wejsciowe.zbior_wyrobow:
        for okres in dane_wejsciowe.zbior_okresow:
            writer.writerow(
                [nazwa_modelu, liczba_wyrobow, 'x', wyrob_i, okres, '', '', __zamien_kropke_na_przecinek(round(
                    model.getVarByName('x(' + str(wyrob_i) + ',' + str(okres) + ')').x, 1
                ))])
            writer.writerow(
                [nazwa_modelu, liczba_wyrobow, 'I', wyrob_i, okres, '', '', __zamien_kropke_na_przecinek(round(
                    model.getVarByName('I(' + str(wyrob_i) + ',' + str(okres) + ')').x, 1
                ))])
            for wyrob_j in dane_wejsciowe.zbior_wyrobow:
                for maszyna in dane_wejsciowe.zbior_maszyn:
                    writer.writerow(
                        [nazwa_modelu, liczba_wyrobow, 'T', wyrob_i, okres, maszyna, wyrob_j,
                         __zamien_kropke_na_przecinek(round(
                             model.getVarByName(
                                 'T(' + str(wyrob_i) + ',' + str(wyrob_j) + ',' + str(okres) + ',' + str(
                                     maszyna) + ')').x, 1
                         ))])
