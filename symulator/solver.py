import gurobipy as gb


def rozwiaz(model):
    model.update()
    model.optimize()

    return model


def czy_modele_wykonalne(lista_modeli):
    for model in lista_modeli:
        if model.status == gb.GRB.INFEASIBLE or model.ObjBound == 0:
            return False
    return True
