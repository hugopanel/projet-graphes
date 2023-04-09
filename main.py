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
        task.duree = int(column[1])

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


def find_successors(graphe: Graphe):
    for tache in graphe.taches:
        if tache.predecesseurs is not None:
            for pred in tache.predecesseurs:
                if pred is not None:
                    if pred.successeurs is None:
                        pred.successeurs = np.array([])
                    if tache not in pred.successeurs:
                        pred.successeurs = np.append(pred.successeurs, [tache])


def trier_graphe(graphe: Graphe):
    nouveau_graphe = Graphe()
    for i in range(len(graphe.taches)):
        for tache in graphe.taches:
            if int(tache.nom) == i:
                nouveau_graphe.taches = np.append(nouveau_graphe.taches, tache)
    return nouveau_graphe


def afficher_arcs(graphe: Graphe):
    nb_arcs = 0
    for tache in graphe.taches:
        for successeur in tache.successeurs:
            nb_arcs += 1
            print(tache.nom, "->", successeur.nom, "=", tache.duree)
    print(graphe.taches.size, "sommets")
    print(nb_arcs, "arcs")


def afficher_matrice_adjacence(graphe: Graphe):
    mat = []

    for tache in graphe.taches:
        ligne = []
        for successeur in graphe.taches:
            if successeur in tache.successeurs:
                ligne.append(tache.duree)
            else:
                ligne.append('*')
        mat.append(ligne)

    col1 = range(len(mat[0]))
    col2 = range(len(mat))
    df = pd.DataFrame(mat, index=col2, columns=col1)
    print(df)


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

    alpha_exists = False  # Est-ce que alpha DEVRAIT exister # TODO: changer le nom
    for tache in graphe.taches:
        if tache.predecesseurs.size == 0:
            alpha_exists = True
            tache.predecesseurs = np.array([alpha])

    if alpha_exists:
        graphe.taches = np.append(graphe.taches, [alpha])
    else:
        raise Exception("Le graphe ne contient aucun sommet sans prédécesseur.")

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

    omega_exists = False
    for tache in graphe.taches:
        if tache.predecesseurs is not None:
            for pred in tache.predecesseurs:
                if pred in taches_sans_successeurs:
                    omega_exists = True
                    taches_sans_successeurs.remove(pred)

    if omega_exists:
        omega = Tache()
        omega.nom = len(graphe.taches)
        omega.duree = 0
        omega.predecesseurs = taches_sans_successeurs
        graphe.taches = np.append(graphe.taches, [omega])
    else:
        raise Exception("Le graphe ne contient aucun sommet sans successeur.")

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


def contient_arcs_negatifs(graphe : Graphe):
    """
    Retourne vrai si le graphe contient une tâche dont la durée est négative.

    :param graphe: Le graphe
    :return: bool Contient un arc négatif
    """
    for tache in graphe.taches:
        if tache.duree < 0:
            return True
    return False


def calculer_rangs(graphe: Graphe, afficher_sortie=True):
    taches = graphe.taches.copy()
    taches: np.ndarray
    taches_a_supprimer = []
    k = 0
    while taches.size > 0:
        if afficher_sortie:
            print("==== Itération", k)
        for tache in taches:
            if len(tache.predecesseurs) == 0:
                # On ajoute le rang à la tâche :
                graphe.taches[np.argwhere(graphe.taches == tache).flatten()][0].rang = k
                # On ajoute la tâche à la liste des tâches à supprimer
                taches_a_supprimer.append(tache)

        if afficher_sortie:
            # Mettre la liste des tâches sous forme de chaîne de caractères :
            liste = []
            for tache in taches_a_supprimer:
                liste.append(str(tache.nom))
            chaine = str.join(', ', liste)
            print("Points d'entrée :", chaine)

        if afficher_sortie:
            print("Suppression des points d'entrée...")
        for tache in taches_a_supprimer:
            # On supprime la tâche des prédécesseurs de ses successeurs :
            for successeur in taches:
                if tache in successeur.predecesseurs:
                    successeur.predecesseurs = np.delete(successeur.predecesseurs,
                       np.argwhere(np.array(successeur.predecesseurs) == tache).flatten())

            # On supprime la tâche de la liste des tâches
            taches = np.delete(taches, np.argwhere(taches == tache).flatten())

        if afficher_sortie:
            # Mettre la liste des tâches sous forme de chaîne de caractères :
            liste = []
            for tache in taches:
                liste.append(str(tache.nom))
            chaine = str.join(', ', liste)
            print("Sommets restants :", chaine)
        k += 1
        taches_a_supprimer.clear()


if __name__ == "__main__":
    try:
        print("Construction du graphe d'ordonnancement :")
        graphe = read_file("./files/table 13 test.txt")
        graphe = create_alpha(graphe)
        graphe = create_omega(graphe)
        # Ajout des successeurs
        find_successors(graphe)

        graphe = trier_graphe(graphe)
        afficher_arcs(graphe)
        afficher_matrice_adjacence(graphe)

        # Est-ce que le graphe possède un circuit ?
        contient_circuits = contient_circuits(graphe)
        print("Contient un ou plusieurs circuits :", contient_circuits)

        print("Contient des arcs négatifs :", contient_arcs_negatifs(graphe))

        if not contient_circuits:
            calculer_rangs(graphe)
    except Exception as e:
        # TODO: Créer des exceptions spécifiques pour ces précis pour retrouver le type d'exception.
        # Si le graphe ne possède aucun sommet sans prédécesseur ou sans successeurs (alpha ou omega pas possible)
        # on a une erreur :
        print("Une erreur est survenue.")
        print(e)
