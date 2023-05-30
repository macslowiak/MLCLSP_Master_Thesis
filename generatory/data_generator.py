import random
from pathlib import Path

import numpy


class WejscieMlclsp:
    def __init__(self, zbior_wyrobow, zbior_okresow, zbior_maszyn, zbior_maszyn_z_przypisanymi_wyrobami, jkuz,
                 zapas_pocz, czas_realizacji, zapotrzebowanie, bom, czas_produkcji, czas_przezbrojenia,
                 koszt_przezbrojenia, dostepnosc_maszyn):
        self.zbior_wyrobow = zbior_wyrobow
        self.zbior_okresow = zbior_okresow
        self.zbior_maszyn = zbior_maszyn
        self.jkuz = jkuz
        self.zapas_pocz = zapas_pocz
        self.czas_realizacji = czas_realizacji
        self.zapotrzebowanie = zapotrzebowanie
        self.bom = bom
        self.czas_produkcji = czas_produkcji
        self.czas_przezbrojenia = czas_przezbrojenia
        self.koszt_przezbrojenia = koszt_przezbrojenia
        self.dostepnosc_maszyn = dostepnosc_maszyn
        self.zbior_maszyn_z_przypisanymi_wyrobami = zbior_maszyn_z_przypisanymi_wyrobami

    def __str__(self):
        return (f'zbior_wyrobow:\n{self.zbior_wyrobow}\n'
                f'zbior_okresow:\n{self.zbior_okresow}\n'
                f'zbior_maszyn:\n{self.zbior_maszyn}\n'
                f'jkuz:\n{self.jkuz}\n'
                f'zapas_pocz:\n{self.zapas_pocz}\n'
                f'czas_realizacji:\n{self.czas_realizacji}\n'
                f'zapotrzebowanie:\n{self.zapotrzebowanie}\n'
                f'bom:\n{self.bom}\n'
                f'czas_produkcji:\n{self.czas_produkcji}\n'
                f'czas_przezbrojenia:\n{self.czas_przezbrojenia}\n'
                f'koszt_przezbrojenia:\n{self.koszt_przezbrojenia}\n'
                f'dostepnosc_maszyn:\n{self.dostepnosc_maszyn}\n'
                f'zbior_maszyn_z_przypisanymi_wyrobami:\n{self.zbior_maszyn_z_przypisanymi_wyrobami}')


def wygeneruj_dane(liczba_wyrobow, liczba_okresow, liczba_maszyn, bom):
    if liczba_wyrobow not in [5, 10, 15, 20, 25]:
        raise Exception("Liczba wyrobów musi być równa jedenej z podanych liczb: [5,10,15,20,25]")
    zbior_wyrobow = numpy.array(list(range(0, liczba_wyrobow)))
    zbior_okresow = numpy.array(list(range(1, liczba_okresow + 1)))
    zbior_maszyn = numpy.array(list(range(0, liczba_maszyn)))

    jkuz = numpy.array([1] * liczba_wyrobow)
    zapas_pocz = numpy.array([0] * liczba_wyrobow)
    czas_realizacji = numpy.array([0] * liczba_wyrobow)

    zapotrzebowanie = wygeneruj_zapotrzebowanie(liczba_wyrobow, liczba_okresow, [0, 1], [0.8, 0.2])
    bom = bom.macierz

    zbior_maszyn_z_przypisanymi_wyrobami = przypisz_wyroby_do_maszyn_uwzgledniajac_zapotrzebowanie(
        liczba_wyrobow, liczba_maszyn, bom, zapotrzebowanie)

    czas_produkcji = wygeneruj_czas_produkcji_dla_czasu(liczba_wyrobow, liczba_maszyn,
                                                        zbior_maszyn_z_przypisanymi_wyrobami, 0.1)

    czas_przezbrojenia = wygeneruj_czasy_przezbrajania_dla_czasu(liczba_wyrobow, liczba_maszyn,
                                                                 zbior_maszyn_z_przypisanymi_wyrobami, 0.2)
    koszt_przezbrojenia = wygeneruj_koszty_przezbrajania(liczba_wyrobow, liczba_maszyn,
                                                         zbior_maszyn_z_przypisanymi_wyrobami, 3)

    dostepnosc_maszyn = wygeneruj_dostepnosc_maszyn(liczba_maszyn, liczba_okresow)

    return WejscieMlclsp(zbior_wyrobow, zbior_okresow, zbior_maszyn, zbior_maszyn_z_przypisanymi_wyrobami, jkuz,
                         zapas_pocz, czas_realizacji, zapotrzebowanie, bom, czas_produkcji, czas_przezbrojenia,
                         koszt_przezbrojenia, dostepnosc_maszyn)


def wygeneruj_zapotrzebowanie(liczba_wyrobow, liczba_okresow, populacja, dystrybuanta):
    zapotrzebowanie = numpy.zeros((liczba_wyrobow, liczba_okresow + 1), dtype=int)
    for i in range(0, liczba_wyrobow):
        zapotrzebowanie[i, 0] = i
    for i in range(0, liczba_wyrobow):
        for m in range(1, liczba_okresow + 1):
            zapotrzebowanie[i, m] = numpy.random.choice(populacja, p=dystrybuanta)

    return zapotrzebowanie


def wygeneruj_zapotrzebowanie_dla_produkcji_seryjnej(liczba_wyrobow, liczba_okresow,
                                                     liczba_wyrobow_koncowych):
    zapotrzebowanie = numpy.zeros((liczba_wyrobow, liczba_okresow + 1), dtype=int)
    for i in range(0, liczba_wyrobow):
        zapotrzebowanie[i, 0] = i
    for i in range(0, liczba_wyrobow):
        for m in range(1, liczba_okresow + 1):
            zapotrzebowanie[i, m] = 0
    for m in range(1, liczba_okresow + 1):
        zapotrzebowanie[liczba_wyrobow - 1, m] = liczba_wyrobow_koncowych

    return zapotrzebowanie


def wygeneruj_dostepnosc_maszyn(liczba_maszyn, liczba_okresow):
    dostepnosc_maszyn = numpy.zeros((liczba_maszyn, liczba_okresow + 1), dtype=int)

    for i in range(0, liczba_maszyn):
        dostepnosc_maszyn[i, 0] = i
    for i in range(0, liczba_maszyn):
        for m in range(1, liczba_okresow + 1):
            dostepnosc_maszyn[i, m] = 1

    return dostepnosc_maszyn


def wygeneruj_czasy_przezbrajania(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami):
    czas_przezbrojenia = numpy.zeros((liczba_wyrobow, liczba_wyrobow))
    for m in range(0, liczba_maszyn):
        if len(zbior_maszyn_z_przypisanymi_wyrobami[m]) > 1:
            wygenerowany_czas = round(random.uniform(0.01, 0.5), 2)
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        czas_przezbrojenia[i, j] = wygenerowany_czas

    return czas_przezbrojenia


def wygeneruj_czasy_przezbrajania_dla_czasu(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami, czas):
    czas_przezbrojenia = numpy.zeros((liczba_wyrobow, liczba_wyrobow))
    for m in range(0, liczba_maszyn):
        if len(zbior_maszyn_z_przypisanymi_wyrobami[m]) > 1:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        czas_przezbrojenia[i, j] = czas

    return czas_przezbrojenia


def wygeneruj_koszty_przezbrajania(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami, koszt):
    koszt_przezbrojenia = numpy.zeros((liczba_wyrobow, liczba_wyrobow), dtype=int)
    for m in range(0, liczba_maszyn):
        if len(zbior_maszyn_z_przypisanymi_wyrobami[m]) > 1:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        koszt_przezbrojenia[i, j] = koszt

    return koszt_przezbrojenia


def wygeneruj_czas_produkcji(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami):
    czas_produkcji = numpy.zeros((liczba_wyrobow, liczba_maszyn))
    for m in range(0, liczba_maszyn):
        for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
            czas_produkcji[i, m] = round(random.uniform(0.01, 0.5), 2)

    return czas_produkcji


def wygeneruj_czas_produkcji_dla_czasu(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami, czas):
    czas_produkcji = numpy.zeros((liczba_wyrobow, liczba_maszyn))
    for m in range(0, liczba_maszyn):
        for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
            czas_produkcji[i, m] = czas

    return czas_produkcji


def przypisz_wyroby_do_maszyn_uwzgledniajac_zapotrzebowanie(liczba_wyrobow, liczba_maszyn, bom, zapotrzebowanie):
    maszyny = list(range(0, liczba_maszyn))
    zbior_maszyn_z_przypisanymi_wyrobami = []
    wyroby_przypisane_do_maszyn = [0] * liczba_wyrobow

    obciazenie_maszyn = numpy.zeros(liczba_maszyn, dtype=int)
    zapotrzebowanie = numpy.delete(zapotrzebowanie, 0, 1)
    zapotrzebowanie_na_wyrob_w_okresach = zapotrzebowanie.sum(axis=1)
    zapotrzebowanie_bom = numpy.transpose(bom) * zapotrzebowanie_na_wyrob_w_okresach.reshape(
        (zapotrzebowanie_na_wyrob_w_okresach.size, 1)
    )
    zapotrzebowanie_bom = numpy.transpose(zapotrzebowanie_bom)
    zapotrzebowanie_na_wyrob_bom = numpy.sum(zapotrzebowanie_bom, axis=1)
    zapotrzebowanie_na_wyrob = numpy.add(zapotrzebowanie_na_wyrob_bom, zapotrzebowanie_na_wyrob_w_okresach)

    # każda maszyna posiada wyrób produkowany na niej
    for i in range(0, liczba_wyrobow):
        if maszyny:
            maszyna = random.choice(maszyny)
            wyroby_przypisane_do_maszyn[i] = maszyna
            obciazenie_maszyn[maszyna] = obciazenie_maszyn[maszyna] + zapotrzebowanie_na_wyrob[i]
            maszyny.remove(maszyna)
        else:
            if wyroby_przypisane_do_maszyn[i] == 0:
                wyroby_przypisane_do_maszyn[i] = random.randint(0, liczba_maszyn - 1)
            else:
                maszyna = numpy.argmin(obciazenie_maszyn)
                wyroby_przypisane_do_maszyn[i] = maszyna
                obciazenie_maszyn[maszyna] = obciazenie_maszyn[maszyna] + zapotrzebowanie_na_wyrob[i]

    wyroby_przypisane_do_maszyn = numpy.array(wyroby_przypisane_do_maszyn)
    for i in range(0, liczba_maszyn):
        przypisane_wyroby = numpy.where(wyroby_przypisane_do_maszyn == i)[0].tolist()
        zbior_maszyn_z_przypisanymi_wyrobami.append(przypisane_wyroby)

    return zbior_maszyn_z_przypisanymi_wyrobami


def przypisz_wyroby_do_maszyn_zgodnie_z_warstwami_bom(liczba_wyrobow, bom):
    liczba_maszyn = bom.poziomy.size
    zbior_maszyn_z_przypisanymi_wyrobami = []
    wyroby_przypisane_do_maszyn = [0] * liczba_wyrobow
    wyrob = 0
    numer_maszyny = 0

    # każda maszyna posiada wyrób produkowany na niej
    for maszyna in bom.poziomy:
        for i in range(0, maszyna):
            wyroby_przypisane_do_maszyn[wyrob] = numer_maszyny
            wyrob += 1
        numer_maszyny += 1

    wyroby_przypisane_do_maszyn = numpy.array(wyroby_przypisane_do_maszyn)
    for i in range(0, liczba_maszyn):
        przypisane_wyroby = numpy.where(wyroby_przypisane_do_maszyn == i)[0].tolist()
        zbior_maszyn_z_przypisanymi_wyrobami.append(przypisane_wyroby)

    return zbior_maszyn_z_przypisanymi_wyrobami


def __stworz_sciezke_zapisu(nazwa_pliku):
    sciezka_zapisu = str(Path(__file__).parent.parent) + '\\wyniki\\' + nazwa_pliku
    return sciezka_zapisu
