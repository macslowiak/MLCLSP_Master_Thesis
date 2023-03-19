import random

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


def wygeneruj_dane(liczba_wyrobow, liczba_okresow, liczba_maszyn):
    # if liczba_wyrobow not in [5, 10, 15, 20, 25, 30]:
    #     raise Exception("Liczba wyrobów musi być równa jedenej z podanych liczb: [5,10,15,20,25,30]")
    zbior_wyrobow = numpy.array(list(range(0, liczba_wyrobow)))
    zbior_okresow = numpy.array(list(range(1, liczba_okresow + 1)))
    zbior_maszyn = numpy.array(list(range(0, liczba_maszyn)))

    jkuz = numpy.array([1] * liczba_wyrobow)
    zapas_pocz = numpy.array([0] * liczba_wyrobow)
    czas_realizacji = numpy.array([0] * liczba_wyrobow)

    zapotrzebowanie = wygeneruj_zapotrzebowanie(liczba_wyrobow, liczba_okresow)
    bom = wygeneruj_bom_dla_sekwencji_jeden_z_dwoch(liczba_wyrobow)

    zbior_maszyn_z_przypisanymi_wyrobami = przypisz_wyroby_do_maszyn(liczba_wyrobow, liczba_maszyn)

    czas_produkcji = wygeneruj_czas_produkcji(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami)

    czas_przezbrojenia = wygeneruj_czasy_przezbrajania(liczba_wyrobow, liczba_maszyn,
                                                       zbior_maszyn_z_przypisanymi_wyrobami)
    koszt_przezbrojenia = wygeneruj_koszty_przezbrajania(liczba_wyrobow, liczba_maszyn,
                                                         zbior_maszyn_z_przypisanymi_wyrobami)

    dostepnosc_maszyn = wygeneruj_dostepnosc_maszyn(liczba_wyrobow, liczba_okresow)

    print('zbior_wyrobow(i): \n', zbior_wyrobow)
    print('zbior_okresow(t): \n', zbior_okresow)
    print('zbior_maszyn(m): \n', zbior_maszyn)
    print('jkuz(i): \n', jkuz)
    print('zapas_pocz(t): \n', zapas_pocz)
    print('czas_realizacji(i): \n', czas_realizacji)
    print('zapotrzebowanie(t): \n', zapotrzebowanie)
    print('bom(i,j): \n', bom)
    print('czas_produkcji(i,m): \n', czas_produkcji)
    print('czas_przezbrojenia(i,j): \n', czas_przezbrojenia)
    print('koszt_przezbrojenia(i,j): \n', koszt_przezbrojenia)
    print('dostepnosc_maszyn(m,t): \n', dostepnosc_maszyn)

    return WejscieMlclsp(zbior_wyrobow, zbior_okresow, zbior_maszyn, zbior_maszyn_z_przypisanymi_wyrobami, jkuz,
                         zapas_pocz, czas_realizacji, zapotrzebowanie, bom, czas_produkcji, czas_przezbrojenia,
                         koszt_przezbrojenia, dostepnosc_maszyn)


# dziala na 3+ wyrobów
def wygeneruj_bom_dla_sekwencji_jeden_z_dwoch(liczba_wyrobow):
    bom = numpy.zeros((liczba_wyrobow, liczba_wyrobow), dtype=int)
    # podzespoly_bazowe = numpy.zeros((random.randint(2, liczba_wyrobow // 2)), dtype=int)
    # while True:
    #     for p in range(0, len(podzespoly_bazowe)):
    #         podzespoly_bazowe[p] = random.randint(0, liczba_wyrobow - 1)
    #     if len(podzespoly_bazowe) == len(set(podzespoly_bazowe)):
    #         break

    for j in range(0, liczba_wyrobow):
        # if j not in podzespoly_bazowe:
        podzespol = 10000000
        podzespol2 = 10000000
        for i in range(0, 2):
            while podzespol == podzespol2 or podzespol == j:
                podzespol = random.randint(0, liczba_wyrobow - 1)
            bom[j, podzespol] = 1
            podzespol2 = podzespol

    return numpy.transpose(bom)


def wygeneruj_zapotrzebowanie(liczba_wyrobow, liczba_okresow):
    zapotrzebowanie = numpy.zeros((liczba_wyrobow, liczba_okresow + 1), dtype=int)
    populacja = [0, 1, 2, 3, 4, 5]
    dystrybuanta = [0.5, 0.1, 0.1, 0.1, 0.1, 0.1]
    for i in range(0, liczba_wyrobow):
        zapotrzebowanie[i, 0] = i
    for i in range(0, liczba_wyrobow):
        for m in range(1, liczba_okresow + 1):
            zapotrzebowanie[i, m] = numpy.random.choice(populacja, p=dystrybuanta)

    return zapotrzebowanie


def wygeneruj_dostepnosc_maszyn(liczba_wyrobow, liczba_okresow):
    dostepnosc_maszyn = numpy.zeros((liczba_wyrobow, liczba_okresow + 1), dtype=int)

    for i in range(0, liczba_wyrobow):
        dostepnosc_maszyn[i, 0] = i
    for i in range(0, liczba_wyrobow):
        for m in range(1, liczba_okresow + 1):
            dostepnosc_maszyn[i, m] = 1

    return dostepnosc_maszyn


def wygeneruj_czasy_przezbrajania(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami):
    czas_przezbrojenia = numpy.zeros((liczba_wyrobow, liczba_wyrobow))
    for m in range(0, liczba_maszyn):
        if len(zbior_maszyn_z_przypisanymi_wyrobami[m]) > 1:
            wygenerowany_czas = round(random.uniform(0, 0.5), 2)
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        czas_przezbrojenia[i, j] = wygenerowany_czas

    return czas_przezbrojenia


def wygeneruj_koszty_przezbrajania(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami):
    koszt_przezbrojenia = numpy.zeros((liczba_wyrobow, liczba_wyrobow), dtype=int)
    for m in range(0, liczba_maszyn):
        if len(zbior_maszyn_z_przypisanymi_wyrobami[m]) > 1:
            koszt = 3
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        koszt_przezbrojenia[i, j] = koszt

    return koszt_przezbrojenia

def wygeneruj_czas_produkcji(liczba_wyrobow, liczba_maszyn, zbior_maszyn_z_przypisanymi_wyrobami):
    czas_produkcji = numpy.zeros((liczba_wyrobow, liczba_maszyn))
    for m in range(0, liczba_maszyn):
        for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
            czas_produkcji[i, m] = round(random.uniform(0, 0.5), 2)

    return czas_produkcji

def przypisz_wyroby_do_maszyn(liczba_wyrobow, liczba_maszyn):
    maszyny = list(range(0, liczba_maszyn))
    zbior_maszyn_z_przypisanymi_wyrobami = []
    wyroby_przypisane_do_maszyn = [0] * liczba_wyrobow

    # każda maszyna posiada wyrób produkowany na niej
    for i in range(0, liczba_wyrobow):
        if maszyny:
            maszyna = random.choice(maszyny)
            wyroby_przypisane_do_maszyn[i] = maszyna
            maszyny.remove(maszyna)
        else:
            wyroby_przypisane_do_maszyn[i] = random.randint(0, liczba_maszyn - 1)

    wyroby_przypisane_do_maszyn = numpy.array(wyroby_przypisane_do_maszyn)
    for i in range(0, liczba_maszyn):
        przypisane_wyroby = numpy.where(wyroby_przypisane_do_maszyn == i)[0].tolist()
        zbior_maszyn_z_przypisanymi_wyrobami.append(przypisane_wyroby)

    return zbior_maszyn_z_przypisanymi_wyrobami
