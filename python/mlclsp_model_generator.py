import gurobipy as gb
import numpy as np


def mlclsp_model(wejscie_mlclsp_model):
    # -------- WEJŚCIE -------- #
    zbior_wyrobow = wejscie_mlclsp_model.zbior_wyrobow
    zbior_okresow = wejscie_mlclsp_model.zbior_okresow
    zbior_maszyn = wejscie_mlclsp_model.zbior_maszyn
    h = wejscie_mlclsp_model.jkuz
    l = wejscie_mlclsp_model.czas_realizacji
    I_0 = wejscie_mlclsp_model.zapas_pocz
    a = wejscie_mlclsp_model.bom
    p = wejscie_mlclsp_model.czas_produkcji
    E = wejscie_mlclsp_model.zapotrzebowanie
    L = wejscie_mlclsp_model.dostepnosc_maszyn

    # -------- UTWORZENIE WYMAGANYCH DANYCH -------- #
    G = 1000000
    zbior_okresow_wraz_z_poczatkowym = np.append(0, zbior_okresow)

    c = wejscie_mlclsp_model.koszt_przezbrojenia
    c = np.apply_along_axis(lambda e: e[(e != 0).argmax()], 0, c)

    sij = wejscie_mlclsp_model.czas_przezbrojenia
    s = np.zeros((len(zbior_wyrobow), len(zbior_maszyn)))
    for m in range(0, len(zbior_maszyn)):
        for i in wejscie_mlclsp_model.zbior_maszyn_z_przypisanymi_wyrobami[m]:
            s[i, m] = np.max(sij[i])

    # -------- ZMIENNE DECYZYJNE -------- #
    model = gb.Model('MLCLSP')

    x = {}
    y = {}
    I = {}
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            x[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='x(' + str(i) + ',' + str(t) + ')')
            y[i, t] = model.addVar(vtype=gb.GRB.BINARY, name='y(' + str(i) + ',' + str(t) + ')')

    print('Nazwa zmiennej:', 'x(' + str(1) + ',' + str(3) + ')')
    for i in zbior_wyrobow:
        for t in zbior_okresow_wraz_z_poczatkowym:
            I[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='I(' + str(i) + ',' + str(t) + ')')

    # -------- FUNKCJA CELU -------- #
    model.setObjective(gb.quicksum(h[i] * I[i, t] + c[i] * y[i, t] for i in zbior_wyrobow for t in zbior_okresow))

    # -------- OGRANICZENIA -------- #

    # -- 01 -- #
    model.addConstrs((I[i, 0] == I_0[i] for i in zbior_wyrobow), name='zapas-poczatkowy')
    model.update()

    # -- O2 -- #
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            model.addConstr(
                I[i, t] == I[i, t - 1] + x[i, t - l[i]] - sum(a[i, j] * x[j, t] for j in zbior_wyrobow) - E[i, t],
                name='bilans_zapasow(' + str(i) + ',' + str(t) + ')'
            )

    # -- O3 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            model.addConstr(sum(p[i, m] * x[i, t] + s[i, m] * y[i, t] for i in zbior_wyrobow) <= L[m, t],
                            name='czas_pracy_maszyny(' + str(m) + ',' + str(t) + ')'
                            )

    # -- O4 -- #
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            model.addConstr(
                x[i, t] - G * y[i, t] <= 0,
                name='produkcja_wyrobu(' + str(i) + ',' + str(t) + ')'
            )

    return model


def mlclsp_partie_model(wejscie_mlclsp_model):
    # -------- WEJŚCIE -------- #
    zbior_wyrobow = wejscie_mlclsp_model.zbior_wyrobow
    zbior_okresow = wejscie_mlclsp_model.zbior_okresow
    zbior_maszyn = wejscie_mlclsp_model.zbior_maszyn
    h = wejscie_mlclsp_model.jkuz
    c = wejscie_mlclsp_model.koszt_przezbrojenia
    I_0 = wejscie_mlclsp_model.zapas_pocz
    a = wejscie_mlclsp_model.bom
    E = wejscie_mlclsp_model.zapotrzebowanie
    s = wejscie_mlclsp_model.czas_przezbrojenia
    L = wejscie_mlclsp_model.dostepnosc_maszyn

    # -------- UTWORZENIE WYMAGANYCH DANYCH -------- #
    zbior_maszyn_z_przypisanymi_wyrobami = wejscie_mlclsp_model.zbior_maszyn_z_przypisanymi_wyrobami
    zbior_okresow_wraz_z_poczatkowym = np.append(0, zbior_okresow)
    zbior_okresow_dla_przezbrojen_poczatkowych = np.append(zbior_okresow,
                                                           zbior_okresow[-1] + 1)

    p = wejscie_mlclsp_model.czas_produkcji
    p = np.apply_along_axis(lambda e: e[(e != 0).argmax()], 1, p)

    # -------- ZMIENNE DECYZYJNE -------- #
    model = gb.Model('MLCLSP_PARTIE')

    x = {}
    x_ijt = {}
    alfa = {}
    T = {}
    W = {}
    u = {}
    I = {}

    for i in zbior_wyrobow:
        for j in zbior_wyrobow:
            for t in zbior_okresow:
                W[i, j, t] = model.addVar(vtype=gb.GRB.BINARY, name='W(' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                x_ijt[i, j, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0,
                                              name='x_ijt(' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                for m in zbior_maszyn:
                    T[i, j, t, m] = model.addVar(vtype=gb.GRB.BINARY,
                                                 name='T(' + str(i) + ',' + str(j) + ',' + str(t) + ',' + str(m) + ')')
        for t in zbior_okresow:
            x[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='x(' + str(i) + ',' + str(t) + ')')
            u[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='u(' + str(i) + ',' + str(t) + ')')

    for i in zbior_wyrobow:
        for t in zbior_okresow_wraz_z_poczatkowym:
            I[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='I(' + str(i) + ',' + str(t) + ')')
        for t in zbior_okresow_dla_przezbrojen_poczatkowych:
            for m in zbior_maszyn:
                alfa[i, t, m] = model.addVar(vtype=gb.GRB.BINARY,
                                             name='alfa(' + str(i) + ',' + str(t) + ',' + str(m) + ')')

    # -------- FUNKCJA CELU -------- #
    model.setObjective(gb.quicksum(h[i] * I[i, t] for i in zbior_wyrobow for t in zbior_okresow) +
                       gb.quicksum(c[i, j] * T[i, j, t, m] for i in zbior_wyrobow for j in zbior_wyrobow
                                   for t in zbior_okresow for m in zbior_maszyn))

    # -------- OGRANICZENIA -------- #

    # -- O1 -- #
    model.addConstrs((I[i, 0] == I_0[i] for i in zbior_wyrobow), name='zapas-poczatkowy')
    model.update()

    # -- O2 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_wyrobow:
                for j in zbior_wyrobow:
                    if i == j or i not in zbior_maszyn_z_przypisanymi_wyrobami[m] or j not in \
                            zbior_maszyn_z_przypisanymi_wyrobami[m]:
                        model.addConstr(T[i, j, t, m] == 0,
                                        name='t_limit[i,j,t,m](' + str(i) + ',' + str(j) + ',' + str(t) + ',' + str(
                                            m) + ')')
                if i not in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    model.addConstr(alfa[i, t, m] == 0,
                                    name='alfa_limit[i,t,m](' + str(i) + ',' + str(t) + ',' + str(m) + ')')

    # -- O3 -- #
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            model.addConstr(
                I[i, t] - I[i, t - 1] - x[i, t] + gb.quicksum(a[i, j] * x[j, t] for j in zbior_wyrobow) + E[i, t] == 0,
                name='bilans_zapasow[i,t](' + str(i) + ',' + str(t) + ')'
            )

    # -- O4 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(
                    p[i] * x[i, t] <= gb.quicksum(T[j, i, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) +
                    alfa[i, t, m],
                    name='produkcja_gdy_przezbrojona[m,i,t](' + str(m) + ',' + str(i) + ',' + str(t) + ')'
                )

    # -- O5 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            model.addConstr(gb.quicksum(alfa[i, t, m] for i in zbior_maszyn_z_przypisanymi_wyrobami[m]) == 1,
                            name='przezbrojenie_wstepne_limit[m,t](' + str(m) + ',' + str(t) + ')'
                            )

    # -- O6 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(gb.quicksum(T[j, i, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) + alfa[
                    i, t, m] == gb.quicksum(
                    T[i, j, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) + alfa[i, t + 1, m],
                                name='przezbrojenie_zapewnienie_stanu[m,i,t](' + str(m) + ',' + str(i) + ',' + str(
                                    t) + ')'
                                )

    # -- O7 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(gb.quicksum(T[j, i, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) <= 1,
                                name='przezbrojenie_raz_na_okres[m,i,t](' + str(m) + ',' + str(i) + ',' + str(t) + ')'
                                )

    # -- O8 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        model.addConstr(
                            u[i, t] + p[i] * x[i, t] + s[i, j] * T[i, j, t, m] + T[i, j, t, m] - 1 - alfa[
                                j, t + 1, m] <= u[
                                j, t],
                            name='start_produkcji_wyrobu[i,j,m,t](' + str(i) + ',' + str(j) + ',' + str(m) + ',' + str(
                                t) + ')'
                        )
                        model.addConstr(
                            u[i, t] + p[i] * x[i, t] + s[i, j] * T[i, j, t, m] + alfa[j, t + 1, m] - 1 - alfa[
                                j, t, m] <= u[
                                j, t],
                            name='start_produkcji_ostatniego_wyrobu[i,j,m,t](' + str(i) + ',' + str(j) + ',' + str(
                                m) + ',' + str(t) + ')'
                        )

    # -- O9 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(
                    u[i, t] + p[i] * x[i, t] + gb.quicksum(
                        s[i, j] * T[i, j, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) <= L[m, t],
                    name='limit_czasu_pracy_maszyny[m,t,i](' + str(m) + ',' + str(t) + ',' + str(i) + ')'
                )

    # -- 10 -- #
    for i in zbior_wyrobow:
        for j in zbior_wyrobow:
            for t in zbior_okresow:
                model.addConstr(
                    (u[i, t] + p[i] * x[i, t]) - u[j, t] <= 1 - W[i, j, t],
                    name='rozpoczecie_produkcji_po_partii[i,j,t](' + str(i) + ',' + str(j) + ',' + str(t) + ')'
                )

    # -- 11 -- #
    for i in zbior_wyrobow:
        for j in zbior_wyrobow:
            for t in zbior_okresow:
                model.addConstr(
                    x_ijt[i, j, t] >= x[j, t] - (1 / p[j]) * W[i, j, t],
                    name='produkcja_wyrobu_w_okresie[i,j,t](' + str(i) + str(j) + ',' + str(t) + ')'
                )

    # -- 12 -- #
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            model.addConstr(
                I[i, t - 1] >= gb.quicksum(a[i, j] * x_ijt[i, j, t] for j in zbior_wyrobow),
                name='produkcja_z_zapasow_poczatkowych[i,t](' + str(i) + ',' + str(t) + ')'
            )

    return model


def mlclsp_strumien_model(wejscie_mlclsp_model):
    # -------- WEJŚCIE -------- #
    zbior_wyrobow = wejscie_mlclsp_model.zbior_wyrobow
    zbior_okresow = wejscie_mlclsp_model.zbior_okresow
    zbior_maszyn = wejscie_mlclsp_model.zbior_maszyn
    h = wejscie_mlclsp_model.jkuz
    c = wejscie_mlclsp_model.koszt_przezbrojenia
    I_0 = wejscie_mlclsp_model.zapas_pocz
    a = wejscie_mlclsp_model.bom
    E = wejscie_mlclsp_model.zapotrzebowanie
    s = wejscie_mlclsp_model.czas_przezbrojenia
    L = wejscie_mlclsp_model.dostepnosc_maszyn

    # -------- UTWORZENIE WYMAGANYCH DANYCH -------- #
    zbior_maszyn_z_przypisanymi_wyrobami = wejscie_mlclsp_model.zbior_maszyn_z_przypisanymi_wyrobami
    zbior_okresow_wraz_z_poczatkowym = np.append(0, zbior_okresow)
    zbior_okresow_dla_przezbrojen_poczatkowych = np.append(zbior_okresow,
                                                           zbior_okresow[-1] + 1)

    p = wejscie_mlclsp_model.czas_produkcji
    p = np.apply_along_axis(lambda e: e[(e != 0).argmax()], 1, p)

    # -------- ZMIENNE DECYZYJNE -------- #
    model = gb.Model('MLCLSP_STRUMIEN')

    x = {}
    alfa = {}
    T = {}
    u = {}
    I = {}

    for i in zbior_wyrobow:
        for j in zbior_wyrobow:
            for t in zbior_okresow:
                for m in zbior_maszyn:
                    T[i, j, t, m] = model.addVar(vtype=gb.GRB.BINARY,
                                                 name='T(' + str(i) + ',' + str(j) + ',' + str(t) + ',' + str(m) + ')')
        for t in zbior_okresow:
            x[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='x(' + str(i) + ',' + str(t) + ')')
            u[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='u(' + str(i) + ',' + str(t) + ')')

    for i in zbior_wyrobow:
        for t in zbior_okresow_wraz_z_poczatkowym:
            I[i, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, name='I(' + str(i) + ',' + str(t) + ')')
        for t in zbior_okresow_dla_przezbrojen_poczatkowych:
            for m in zbior_maszyn:
                alfa[i, t, m] = model.addVar(vtype=gb.GRB.BINARY,
                                             name='alfa(' + str(i) + ',' + str(t) + ',' + str(m) + ')')

    # -------- FUNKCJA CELU -------- #
    model.setObjective(gb.quicksum(h[i] * I[i, t] for i in zbior_wyrobow for t in zbior_okresow) +
                       gb.quicksum(
                           c[i, j] * T[i, j, t, m] for i in zbior_wyrobow for j in zbior_wyrobow for t in zbior_okresow
                           for
                           m in zbior_maszyn))

    # -------- OGRANICZENIA -------- #

    # -- O1 -- #
    model.addConstrs((I[i, 0] == I_0[i] for i in zbior_wyrobow), name='zapas-poczatkowy')
    model.update()

    # -- O2 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_wyrobow:
                for j in zbior_wyrobow:
                    if i == j or i not in zbior_maszyn_z_przypisanymi_wyrobami[m] or j not in \
                            zbior_maszyn_z_przypisanymi_wyrobami[m]:
                        model.addConstr(T[i, j, t, m] == 0,
                                        name='t_limit[i,j,t,m](' + str(i) + ',' + str(j) + ',' + str(t) + ',' + str(
                                            m) + ')')
                if i not in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    model.addConstr(alfa[i, t, m] == 0,
                                    name='alfa_limit[i,t,m](' + str(i) + ',' + str(t) + ',' + str(m) + ')')

    # -- O3 -- #
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            model.addConstr(
                I[i, t] - I[i, t - 1] - x[i, t] + gb.quicksum(a[i, j] * x[j, t] for j in zbior_wyrobow) + E[i, t] == 0,
                name='bilans_zapasow[i,t](' + str(i) + ',' + str(t) + ')'
            )

    # -- O4 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(
                    p[i] * x[i, t] <= gb.quicksum(T[j, i, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) +
                    alfa[i, t, m],
                    name='produkcja_gdy_przezbrojona[m,i,t](' + str(m) + ',' + str(i) + ',' + str(t) + ')'
                )

    # -- O5 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            model.addConstr(gb.quicksum(alfa[i, t, m] for i in zbior_maszyn_z_przypisanymi_wyrobami[m]) == 1,
                            name='przezbrojenie_wstepne_limit[m,t](' + str(m) + ',' + str(t) + ')'
                            )

    # -- O6 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(gb.quicksum(T[j, i, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) + alfa[
                    i, t, m] == gb.quicksum(
                    T[i, j, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) + alfa[i, t + 1, m],
                                name='przezbrojenie_zapewnienie_stanu[m,i,t](' + str(m) + ',' + str(i) + ',' + str(
                                    t) + ')'
                                )

    # -- O7 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(gb.quicksum(T[j, i, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) <= 1,
                                name='przezbrojenie_raz_na_okres[m,i,t](' + str(m) + ',' + str(i) + ',' + str(t) + ')'
                                )

    # -- O8 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                for j in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                    if i != j:
                        model.addConstr(
                            u[i, t] + p[i] * x[i, t] + s[i, j] * T[i, j, t, m] + T[i, j, t, m] - 1 - alfa[
                                j, t + 1, m] <= u[
                                j, t],
                            name='start_produkcji_wyrobu[i,j,m,t](' + str(i) + ',' + str(j) + ',' + str(m) + ',' + str(
                                t) + ')'
                        )
                        model.addConstr(
                            u[i, t] + p[i] * x[i, t] + s[i, j] * T[i, j, t, m] + alfa[j, t + 1, m] - 1 - alfa[
                                j, t, m] <= u[
                                j, t],
                            name='start_produkcji_ostatniego_wyrobu[i,j,m,t](' + str(i) + ',' + str(j) + ',' + str(
                                m) + ',' + str(t) + ')'
                        )

    # -- O9 -- #
    for m in zbior_maszyn:
        for t in zbior_okresow:
            for i in zbior_maszyn_z_przypisanymi_wyrobami[m]:
                model.addConstr(
                    u[i, t] + p[i] * x[i, t] + gb.quicksum(
                        s[i, j] * T[i, j, t, m] for j in zbior_maszyn_z_przypisanymi_wyrobami[m]) <= L[m, t],
                    name='limit_czasu_pracy_maszyny[m,t,i](' + str(m) + ',' + str(t) + ',' + str(i) + ')'
                )

    # -- 10 -- #
    aux1 = {}
    aux2 = {}
    aux3 = {}
    aux4 = {}
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            for j in zbior_wyrobow:
                aux1[i, j, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=-gb.GRB.INFINITY,
                                             name='aux1(' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                aux2[i, j, t] = model.addVar(vtype=gb.GRB.CONTINUOUS,
                                             name='aux2(' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                aux3[i, j, t] = model.addVar(vtype=gb.GRB.CONTINUOUS,
                                             name='aux3(' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                aux4[i, j, t] = model.addVar(vtype=gb.GRB.CONTINUOUS,
                                             name='aux4(' + str(i) + ',' + str(j) + ',' + str(t) + ')')
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            for j in zbior_wyrobow:
                model.addConstr(aux1[i, j, t] == u[i, t] - u[j, t],
                                name='aux1[i,j,t](' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                model.addConstr(aux2[i, j, t] == gb.max_([0, aux1[i, j, t]]),
                                name='aux2[i,j,t](' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                model.addConstr(aux3[i, j, t] == aux2[i, j, t] * (1 / p[j]),
                                name='aux3[i,j,t](' + str(i) + ',' + str(j) + ',' + str(t) + ')')
                model.addConstr(aux4[i, j, t] == gb.min_([x[j, t], aux3[i, j, t]]),
                                name='aux4[i,j,t](' + str(i) + ',' + str(j) + ',' + str(t) + ')')

    for i in zbior_wyrobow:
        for t in zbior_okresow:
            model.addConstr(
                I[i, t - 1] >= sum(a[i, j] * aux4[i, j, t] for j in zbior_wyrobow),
                name='zapewnienie_zapasu_poczatkowego[i,t](' + str(i) + ',' + str(t) + ')'
            )

    # -- 11 -- #
    aux5 = {}
    aux6 = {}
    aux7 = {}
    aux8 = {}
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            for k in zbior_wyrobow:
                aux5[i, k, t] = model.addVar(vtype=gb.GRB.CONTINUOUS, lb=-gb.GRB.INFINITY,
                                             name='aux5(' + str(i) + ',' + str(k) + ',' + str(t) + ')')
                aux6[i, k, t] = model.addVar(vtype=gb.GRB.CONTINUOUS,
                                             name='aux6(' + str(i) + ',' + str(k) + ',' + str(t) + ')')
                aux7[i, k, t] = model.addVar(vtype=gb.GRB.CONTINUOUS,
                                             name='aux7(' + str(i) + ',' + str(k) + ',' + str(t) + ')')
                aux8[i, k, t] = model.addVar(vtype=gb.GRB.CONTINUOUS,
                                             name='aux8(' + str(i) + ',' + str(k) + ',' + str(t) + ')')
    for i in zbior_wyrobow:
        for t in zbior_okresow:
            for k in zbior_wyrobow:
                model.addConstr(aux5[i, k, t] == u[k, t] + p[k] * x[k, t] - u[i, t],
                                name='aux5[i,k,t](' + str(i) + ',' + str(k) + ',' + str(t) + ')')
                model.addConstr(aux6[i, k, t] == gb.max_([0, aux5[i, k, t]]),
                                name='aux6[i,k,t](' + str(i) + ',' + str(k) + ',' + str(t) + ')')
                model.addConstr(aux7[i, k, t] == aux6[i, k, t] * (1 / p[i]),
                                name='aux7[i,k,t](' + str(i) + ',' + str(k) + ',' + str(t) + ')')
                model.addConstr(aux8[i, k, t] == gb.min_([x[i, t], aux7[i, k, t]]),
                                name='aux8[i,k,t](' + str(i) + ',' + str(k) + ',' + str(t) + ')')

    for i in zbior_wyrobow:
        for k in zbior_wyrobow:
            for t in zbior_okresow:
                model.addConstr(
                    I[i, t - 1] + aux8[i, k, t] >= sum(a[i, j] * aux8[j, k, t] for j in zbior_wyrobow),
                    name='zapewnienie_zapasu[i,k,t](' + str(i) + ',' + str(k) + ',' + str(t) + ')'
                )

    return model


def sprawdz_poprawnosc_dla(tabela, nazwa_arkusza):
    for kolumna in tabela:
        if np.count_nonzero(kolumna) != 1:
            raise Exception(
                'Każdy wyrób może być produkowany tylko na jednej maszynie. Należy poprawić dane w arkuszu ' + nazwa_arkusza)
