import gurobipy as gb


def rozwiaz(model, time_limit_in_seconds):
    model.Params.TimeLimit = time_limit_in_seconds
    model.update()
    model.optimize()

    return model


def rozwiaz_bez_limitu_czasu(model):
    model.update()
    model.optimize()

    return model


def czy_modele_wykonalne(lista_modeli):
    for model in lista_modeli:
        if model.status == gb.GRB.INFEASIBLE or model.status == gb.GRB.TIME_LIMIT:
            return False
    return True


def czy_model_wykonalny(model):
    if model.status == gb.GRB.INFEASIBLE or model.status == gb.GRB.TIME_LIMIT:
        return False
    return True


def czy_modele_wykonalne_wynik_rozny_od_zera(lista_modeli):
    for model in lista_modeli:
        if model.status == gb.GRB.INFEASIBLE or model.status == gb.GRB.TIME_LIMIT or model.ObjBound == 0:
            return False
    return True


def czy_model_wykonalny_wynik_rozny_od_zera(model):
    if model.status == gb.GRB.INFEASIBLE or model.status == gb.GRB.TIME_LIMIT or model.ObjBound == 0:
        return False
    return True


def czy_modele_zlozone_niewykonalne(lista_modeli):
    model_podstawowy_mlclsp = lista_modeli[0]
    if model_podstawowy_mlclsp.status == gb.GRB.INFEASIBLE or model_podstawowy_mlclsp.status == gb.GRB.TIME_LIMIT or model_podstawowy_mlclsp.ObjBound == 0:
        return False
    for model in lista_modeli[1:]:
        if not (model.status == gb.GRB.INFEASIBLE or model.status == gb.GRB.TIME_LIMIT or model.ObjBound == 0):
            return False
    return True
