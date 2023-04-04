import pandas as pd
import numpy as np
from graphes import *


def read_file(file_path: str):
    # Ouverture du fichier
    # file = "./files/table 2.txt"
    f = open(file_path, 'r')

    graph = Graphe()  # Initialisation du graphe
    line = f.readline()  # Lecture du fichier

    while line:
        line = line.strip()  # Supprimer les espaces et retours à la ligne au début et à la fin
        column = line.split(' ')  # Découper la ligne en tableau à chaque espace

        # On vérifie si la tâche a déjà été ajoutée au graphe
        task_exists = False
        for tache in graph.taches:
            if tache.nom == column[0]:
                task_exists = True
                task = tache  # On récupère la tâche pour la modifier
                break  # On quitte la boucle
        if not task_exists:
            # La tâche n'a pas été ajoutée, donc on la crée :
            task = Tache()
            task.nom = column[0]
            # graph.taches = np.append(graph.taches, [t])  # On ajoute la tâche au graphe

        # On modifie la tâche en fonction de ce qu'on lit dans le fichier .txt :
        task.duree = column[1]

        # S'il existe des contraintes (prédécesseurs), on les ajoute :
        if len(column) > 2:
            for pre in column[2:]:  # Pour chaque contrainte...
                # On vérifie si elle a déjà été ajoutée au graphe
                pred_exists = False
                for tache in graph.taches:
                    if tache.nom == pre:
                        # Elle existe, donc on la récupère
                        predecesseur = tache
                        pred_exists = True
                        break
                if not pred_exists:  # Si elle n'a pas été ajoutée, on la crée :
                    predecesseur = Tache()
                    predecesseur.nom = pre
                    graph.taches = np.append(graph.taches, [predecesseur])  # On l'ajoute au graphe

                # On ajoute la contrainte à la liste des contraintes :
                task.predecesseurs = np.append(task.predecesseurs, [predecesseur])

        if not task_exists:
            graph.taches = np.append(graph.taches, [task])

        line = f.readline()
    return graph

# TODO: Ajouter les successeurs ???
def find_successors(graphe: Graphe):
    for tache in graphe.taches:
        if tache.predecesseurs is not None:
            for pred in tache.predecesseurs:
                if pred is not None:
                    if pred.successeurs is None:
                        pred.successeurs = np.array([])
                    if tache not in pred.successeurs:
                        pred.successeurs = np.append(pred.successeurs, [tache])


def create_alpha(graphe: Graphe):
    """
    Crée la tâche alpha et l'ajoute au tableau de tâches du graphe.

    :param graphe: Le graphe
    :return: Le graphe avec la tâche alpha (0).
    """
    # Regarder les tâches qui n'ont aucune contrainte
    alpha = Tache()
    alpha.nom = 0
    alpha.duree = 0

    for tache in graphe.taches:
        if tache.predecesseurs is None:
            tache.predecesseurs = np.array([alpha])

    graphe.taches = np.append(graphe.taches, [alpha])
    return graphe


def create_omega(graphe: Graphe):
    """
    Crée la tâche omega et l'ajoute au tableau de tâches du graphe.

    :param graphe: Le graphe
    :return: Le graphe avec la tâche omega (N+1)
    """
    # Regarder les tâches qui n'apparaissent pas dans les contraintes
    taches_sans_successeurs = []
    for tache in graphe.taches:
        taches_sans_successeurs.append(tache)

    for tache in graphe.taches:
        if tache.predecesseurs is not None:
            for pred in tache.predecesseurs:
                if pred in taches_sans_successeurs:
                    taches_sans_successeurs.remove(pred)

    omega = Tache()
    omega.nom = len(graphe.taches)
    omega.duree = 0

    omega.predecesseurs = taches_sans_successeurs

    graphe.taches = np.append(graphe.taches, [omega])
    return graphe


def contient_circuits(graphe : Graphe):
    """

    :rtype: bool Contient un ou plusieurs circuits
    """
    return trouver_circuit(graphe.taches[-2], np.array([]))


def trouver_circuit(tache, liste):
    if tache in liste:
        return True
    if tache.successeurs is not None:
        for successeur in tache.successeurs:
            if trouver_circuit(successeur, np.append(liste, tache)):
                return True
    return False


if __name__ == "__main__":
    graphe = read_file("./files/table 1.txt")
    graphe = create_alpha(graphe)
    graphe = create_omega(graphe)
    # Ajout des successeurs
    find_successors(graphe)

    # Est-ce que le graphe possède un circuit ?
    print(contient_circuits(graphe))
