import itertools
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


# ------- FUNKCJE POMOCNICZE -------
# Źródło: https://networkx.org/documentation/stable/auto_examples/drawing/plot_multipartite_graph.html
def __multilayered_graph(*subset_sizes):
    extents = nx.utils.pairwise(itertools.accumulate((0,) + subset_sizes))
    layers = [range(start, end) for start, end in extents]
    G = nx.Graph()
    for (i, layer) in enumerate(layers):
        G.add_nodes_from(layer, layer=i)
    for layer1, layer2 in nx.utils.pairwise(layers):
        G.add_edges_from(itertools.product(layer1, layer2))
    return G


def narysuj_bom(bom):
    graf = plt.figure(figsize=(10, 6))
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    stworzone_poziomy = __multilayered_graph(*bom.poziomy)
    diagram = nx.from_numpy_matrix(bom.macierz, create_using=nx.DiGraph)
    pozycja = nx.multipartite_layout(stworzone_poziomy, subset_key="layer")

    nx.draw(diagram, pozycja, node_size=650, node_color='#E6E6FA', with_labels=True)
    return graf


# ------------------------------------

class Bom:
    def __init__(self, macierz, poziomy):
        self.macierz = macierz
        self.poziomy = np.array(poziomy)


def wygeneruj_bom(liczba_wyrobow, maksymalna_ilosc_wyrobow_w_warstwie,
                  minimalna_ilosc_wyrobow_w_warstwie, prawdopodobienstwo_stworzenia_polaczenia):
    iteracja = 0

    while True:
        bom = np.zeros((liczba_wyrobow, liczba_wyrobow), dtype=int)
        poziomy = []
        produkty = 0

        while produkty < liczba_wyrobow:

            while True:
                nowe_produkty = random.randint(minimalna_ilosc_wyrobow_w_warstwie, maksymalna_ilosc_wyrobow_w_warstwie)
                if nowe_produkty + produkty <= liczba_wyrobow:
                    break
                if liczba_wyrobow - produkty < minimalna_ilosc_wyrobow_w_warstwie:
                    return wygeneruj_bom(liczba_wyrobow, maksymalna_ilosc_wyrobow_w_warstwie,
                                         minimalna_ilosc_wyrobow_w_warstwie, prawdopodobienstwo_stworzenia_polaczenia)

            for produkt_poprzednia_warstwa in range(produkty):
                for produkt_nowa_warstwa in range(nowe_produkty):
                    if random.randint(0, 99) < prawdopodobienstwo_stworzenia_polaczenia:
                        bom[produkt_nowa_warstwa + produkty, produkt_poprzednia_warstwa] = 1

            poziomy.append(nowe_produkty)
            produkty += nowe_produkty

        if not __czy_produkt_bez_polaczen(bom):
            break
        iteracja += 1
        __przerwij_generowanie_jezeli_ilosc_iteracji_przekroczona(iteracja)

    bom = np.transpose(bom)
    return Bom(bom, poziomy)


# Należy odpowiednio dobrać prawdopodobieństwo do liczby polaczen wychodzacych
def wygeneruj_bom_dla_struktury_wyrobow_z_montazem(liczba_wyrobow, maksymalna_ilosc_wyrobow_w_warstwie,
                                                                minimalna_ilosc_wyrobow_w_warstwie,
                                                                prawdopodobienstwo_stworzenia_polaczenia):
    iteracja = 0
    liczba_polaczen_wychodzacych = 1
    while True:
        bom = np.zeros((liczba_wyrobow, liczba_wyrobow), dtype=int)
        produkty_z_polaczeniami_wychodzacymi = np.zeros(liczba_wyrobow, dtype=int)
        poziomy = []
        produkty = 0

        while produkty < liczba_wyrobow:

            while True:
                nowe_produkty = random.randint(minimalna_ilosc_wyrobow_w_warstwie, maksymalna_ilosc_wyrobow_w_warstwie)
                if nowe_produkty + produkty <= liczba_wyrobow:
                    break
                if liczba_wyrobow - produkty < minimalna_ilosc_wyrobow_w_warstwie:
                    return wygeneruj_bom_dla_struktury_wyrobow_z_montazem(liczba_wyrobow,
                                                                                       maksymalna_ilosc_wyrobow_w_warstwie,
                                                                                       minimalna_ilosc_wyrobow_w_warstwie,
                                                                                       prawdopodobienstwo_stworzenia_polaczenia)

            for produkt_poprzednia_warstwa in range(produkty):
                for produkt_nowa_warstwa in range(nowe_produkty):
                    if random.randint(0, 99) < prawdopodobienstwo_stworzenia_polaczenia:
                        while True:
                            if produkty_z_polaczeniami_wychodzacymi[
                                produkt_poprzednia_warstwa] == liczba_polaczen_wychodzacych:
                                break
                            bom[produkt_nowa_warstwa + produkty, produkt_poprzednia_warstwa] = 1
                            produkty_z_polaczeniami_wychodzacymi[produkt_poprzednia_warstwa] += 1
                            break

            poziomy.append(nowe_produkty)
            produkty += nowe_produkty

        if not __czy_produkt_bez_polaczen(bom):
            break
        iteracja += 1
        __przerwij_generowanie_jezeli_ilosc_iteracji_przekroczona(iteracja)

    bom = np.transpose(bom)
    return Bom(bom, poziomy)


def wygeneruj_bom_dla_struktury_seryjnej(liczba_wyrobow):
    bom = np.zeros((liczba_wyrobow, liczba_wyrobow), dtype=int)
    poziomy = []
    produkt_poprzednia_warstwa = 0

    while produkt_poprzednia_warstwa < liczba_wyrobow - 1:
        nowy_produkt = 1
        bom[nowy_produkt + produkt_poprzednia_warstwa, produkt_poprzednia_warstwa] = 1

        poziomy.append(nowy_produkt)
        produkt_poprzednia_warstwa += nowy_produkt
    poziomy.append(1)
    bom = np.transpose(bom)
    return Bom(bom, poziomy)


def __czy_produkt_bez_polaczen(bom_macierz):
    kolumny_suma = __suma_kolumny(bom_macierz)
    wiersze_suma = __suma_wiersze(bom_macierz)
    for produkt in range(len(bom_macierz)):
        if kolumny_suma[produkt] == 0 and wiersze_suma[produkt] == 0:
            return True
    return False


def __suma_kolumny(bom_macierz):
    return np.sum(bom_macierz, axis=0)


def __suma_wiersze(bom_macierz):
    return np.sum(bom_macierz, axis=1)


def __przerwij_generowanie_jezeli_ilosc_iteracji_przekroczona(obecna_iteracja):
    maksymalna_ilosc_prob = 10000
    if obecna_iteracja > maksymalna_ilosc_prob:
        raise Exception("Błąd generowania bom'u. Przekroczono ilość prób. Należy zweryfikować argumenty wejściowe.")
