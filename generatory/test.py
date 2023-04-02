import numpy as np

import data_generator as dg
import mlclsp_model_generator as mlclspgen


def przyklad_z_artykulu():
    zbior_wyrobow = np.array([0, 1, 2, 3])
    zbior_okresow = np.array([1, 2])
    zbior_maszyn = np.array([0, 1, 2])
    jkuz = np.array([3, 2, 2, 1])
    zapas_pocz = np.array([0, 0, 0, 0])
    czas_realizacji = np.array([0, 0, 0, 0])
    czas_produkcji = np.array([[0.1, 0., 0.],
                               [0., 0.4, 0.],
                               [0., 0., 0.1],
                               [0., 0., 0.1]])
    zapotrzebowanie = np.array([[0, 3, 0],
                                [1, 0, 2],
                                [2, 0, 0],
                                [3, 0, 0]])
    bom = np.array([[0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [1, 0, 0, 0],
                    [0, 1, 1, 0]])
    zbior_maszyn_z_przypisanymi_wyrobami = np.array([[0], [1], [2, 3]], dtype=object)
    czas_przezbrojenia = np.array([[0., 0., 0., 0.],
                                   [0., 0., 0., 0.],
                                   [0., 0., 0., 0.05],
                                   [0., 0., 0.05, 0.]])
    koszt_przezbrojenia = np.array([[0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 5],
                                    [0, 0, 5, 0]])
    dostepnosc_maszyn = np.array([[0, 1, 1],
                                  [1, 1, 1],
                                  [2, 1, 1]])
    return dg.WejscieMlclsp(zbior_wyrobow, zbior_okresow, zbior_maszyn, zbior_maszyn_z_przypisanymi_wyrobami,
                            jkuz, zapas_pocz, czas_realizacji, zapotrzebowanie, bom, czas_produkcji,
                            czas_przezbrojenia, koszt_przezbrojenia, dostepnosc_maszyn)


mlclsp_wejscie = przyklad_z_artykulu()
#
# mlclsp
mlclsp = mlclspgen.mlclsp_model(mlclsp_wejscie)
mlclsp.update()
mlclsp.optimize()

# mlclsp partie
mlclsp = mlclspgen.mlclsp_partie_model(mlclsp_wejscie)
mlclsp.update()
mlclsp.optimize()

# mlclsp partie
mlclsp = mlclspgen.mlclsp_strumien_model(mlclsp_wejscie)
mlclsp.update()
mlclsp.optimize()

# # Wynik dla mlclsp - 12, mlclsp_partie - 10, mlclsp_strumień - 7. 12 dla mlclsp, ponieważ
# # zmapowane zostały realne przezbrojenia tj. tylko te, które są możliwe dla wyrobów

