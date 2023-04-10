import pandas as pd
import numpy as np
from graphes import *
from os import listdir


def lire_fichier(chemin_fichier: str):
    """
    Met un graphe en mémoire à partir d'un chemin vers un  fichier de contraintes.

    :param chemin_fichier: Chemin vers le fichier à mettre en mémoire
    :return: Le graphe de type Graphe.
    """
    # Ouverture du fichier
    fichier = open(chemin_fichier, 'r')

    graphe = Graphe()  # Initialisation du graphe
    ligne = fichier.readline()  # Lecture du fichier

    while ligne:
        ligne = ligne.strip()  # Supprimer les espaces et retours à la ligne au début et à la fin
        colonne = ligne.split(' ')  # Découper la ligne en tableau à chaque espace

        # On vérifie si la tâche a déjà été ajoutée au graphe
        b_tache_existe = False
        for tache in graphe.taches:
            if tache.nom == colonne[0]:
                b_tache_existe = True
                sommet = tache  # On récupère la tâche pour la modifier
                break  # On quitte la boucle
        if not b_tache_existe:
            # La tâche n'a pas été ajoutée, donc on la crée :
            sommet = Tache()
            sommet.nom = colonne[0]
            # graph.taches = np.append(graph.taches, [t])  # On ajoute la tâche au graphe

        # On modifie la tâche en fonction de ce qu'on lit dans le fichier .txt :
        sommet.duree = int(colonne[1])

        # S'il existe des contraintes (prédécesseurs), on les ajoute :
        if len(colonne) > 2:
            for predecesseur in colonne[2:]:  # Pour chaque contrainte...
                # On vérifie si elle a déjà été ajoutée au graphe
                b_predecesseur_existe = False
                for tache in graphe.taches:
                    if tache.nom == predecesseur:
                        # Elle existe, donc on la récupère
                        pred = tache
                        b_predecesseur_existe = True
                        break
                if not b_predecesseur_existe:  # Si elle n'a pas été ajoutée, on la crée :
                    pred = Tache()
                    pred.nom = predecesseur
                    graphe.taches = np.append(graphe.taches, [pred])  # On l'ajoute au graphe

                # On ajoute la contrainte à la liste des contraintes :
                sommet.predecesseurs = np.append(sommet.predecesseurs, [pred])

        if not b_tache_existe:
            graphe.taches = np.append(graphe.taches, [sommet])

        ligne = fichier.readline()
    return graphe


def trouver_successeurs(graphe: Graphe):
    """
    Ajoute les successeurs de chaque tâche à un graphe.

    Le graphe passé en paramètres est modifié directement. La fonction ne retourne rien.

    :param graphe: Le graphe contenant les tâches à modifier.
    """
    for tache in graphe.taches:
        if tache.predecesseurs is not None:
            for pred in tache.predecesseurs:
                if pred is not None:
                    if pred.successeurs is None:
                        pred.successeurs = np.array([])
                    if tache not in pred.successeurs:
                        pred.successeurs = np.append(pred.successeurs, [tache])


def trier_graphe(graphe: Graphe):
    """
    Trie un graphe dans l'ordre croissant en fonction du nom des tâches.

    :param graphe: Le graphe à trier.
    :return: Le graphe trié.
    """
    nouveau_graphe = Graphe()
    for i in range(len(graphe.taches)):
        for tache in graphe.taches:
            if int(tache.nom) == i:
                nouveau_graphe.taches = np.append(nouveau_graphe.taches, tache)
    return nouveau_graphe


def afficher_arcs(graphe: Graphe):
    """
    Affiche les arcs d'un graphe et leurs valeurs sous la forme :
    0 -> 1 = 2

    :param graphe: Le graphe.
    """
    nb_arcs = 0
    for tache in graphe.taches:
        for successeur in tache.successeurs:
            nb_arcs += 1
            print(tache.nom, "->", successeur.nom, "=", tache.duree)
    print(graphe.taches.size, "sommets")
    print(nb_arcs, "arcs")


def afficher_matrice_adjacence(graphe: Graphe):
    """
    Affiche le graphe sous forme matricielle.

    :param graphe: Le graphe à afficher.
    """
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


def ajouter_alpha(graphe: Graphe):
    """
    Crée la tâche alpha et l'ajoute au tableau de tâches du graphe.

    :param graphe: Le graphe
    :return: Le graphe avec la tâche alpha (0).
    """
    # Regarder les tâches qui n'ont aucune contrainte
    alpha = Tache()
    alpha.nom = 0
    alpha.duree = 0

    alpha_devrait_exister = False
    for tache in graphe.taches:
        if tache.predecesseurs.size == 0:
            alpha_devrait_exister = True
            tache.predecesseurs = np.array([alpha])

    if alpha_devrait_exister:
        graphe.taches = np.append(graphe.taches, [alpha])
    else:
        raise Exception("Le graphe ne contient aucun sommet sans prédécesseur.")

    return graphe


def ajouter_omega(graphe: Graphe):
    """
    Crée la tâche omega et l'ajoute au tableau de tâches du graphe.

    :param graphe: Le graphe
    :return: Le graphe avec la tâche omega (N+1)
    """
    # Regarder les tâches qui n'apparaissent pas dans les contraintes
    taches_sans_successeurs = []

    for tache in graphe.taches:
        taches_sans_successeurs.append(tache)

    omega_devrait_exister = False
    for tache in graphe.taches:
        if tache.predecesseurs is not None:
            for pred in tache.predecesseurs:
                if pred in taches_sans_successeurs:
                    omega_devrait_exister = True
                    taches_sans_successeurs.remove(pred)

    if omega_devrait_exister:
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
    Retourne vrai si le graphe contient un ou plusieurs circuits, faux sinon.

    :param graphe: Le graphe à tester.
    :rtype: bool Contient un ou plusieurs circuits
    """
    return trouver_circuit(graphe.taches[0], np.array([]))


def trouver_circuit(tache, liste):
    """
    Fonction récursive pour trouver les circuits d'un graphe.

    Préférer la fonction `contient_circuits` qui est plus simple à utiliser.
    """
    if tache in liste:
        return True
    if tache.successeurs.size != 0:
        for successeur in tache.successeurs:
            if trouver_circuit(successeur, np.append(liste, tache)):
                return True
    return False


def contient_arcs_negatifs(graphe : Graphe):
    """
    Retourne vrai si le graphe contient une tâche dont la durée est négative, faux sinon.

    :param graphe: Le graphe.
    :return: bool Contient un arc négatif.
    """
    for tache in graphe.taches:
        if tache.duree < 0:
            return True
    return False


def calculer_rangs(graphe: Graphe, afficher_sortie=True):
    """
    Calcule les rangs de chaque tâche d'un graphe et les ajoute dans la propriété `rang` des tâches.

    :param graphe: Le graphe contenant les tâches.
    :param afficher_sortie: Si vrai, affiche les étapes de l'algorithme.
    """
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
    # TODO: Créer une solution propre pour ne pas modifier le graphe de base et ne pas avoir à retrouver les
    # prédécesseurs après !
    retrouver_predecesseurs(graphe)  # Patch temporaire


def retrouver_predecesseurs(graphe: Graphe):
    """
    Permet d'ajouter les prédécesseurs dans un graphe possédant déjà les successeurs.

    Le graphe d'origine est modifié. Cette fonction ne retourne rien.

    :param graphe: Le graphe possédant les successeurs.
    """
    for tache in graphe.taches:
        for successeur in tache.successeurs:
            successeur.predecesseurs = np.append(successeur.predecesseurs, tache)


def calculer_calendriers(graphe: Graphe):
    """
    Calcule les dates au plus tôt et plus tard d'un graphe.

    :param graphe: Le graphe.
    :return: Array contenant des dictionnaires des dates au plus tôt en indice 0 et des dates au plus tard en indice 1.
    """
    calendrier_plus_tot = {}
    calendrier_plus_tard = {}

    # Calcul des dates au plus tôt :
    for tache in graphe.taches:
        calculer_date_tot(calendrier_plus_tot, tache)

    # Calcul des dates au plus tard :
    calendrier_plus_tard[int(graphe.taches[-1].nom)] = calendrier_plus_tot[int(graphe.taches[-1].nom)]
    for tache in graphe.taches:
        calculer_date_tard(calendrier_plus_tard, tache)

    # On retourne le tout
    return [calendrier_plus_tot, calendrier_plus_tard]


def calculer_date_tot(calendrier_plus_tot: dict, sommet: Tache):
    """
    Fonction récursive pour trouver les dates au plus tôt d'un graphe.

    Préférer la fonction `calculer_calendriers` qui est plus simple à utiliser.
    """
    if int(sommet.nom) in calendrier_plus_tot.keys():  # Si on a déjà calculé la date :
        return calendrier_plus_tot

    # Sinon, on la calcule.
    # Pour ça, on prend la date + duree la plus haute parmi les prédécesseurs
    duree = 0
    for predecesseur in sommet.predecesseurs:
        if int(predecesseur.nom) not in calendrier_plus_tot.keys():
            # Calcul de la date du prédécesseur :
            calendrier_plus_tot = calculer_date_tot(calendrier_plus_tot, predecesseur)
        date_pred = calendrier_plus_tot[int(predecesseur.nom)] + predecesseur.duree
        duree = date_pred if date_pred > duree else duree
    calendrier_plus_tot[int(sommet.nom)] = duree
    return calendrier_plus_tot


def calculer_date_tard(calendrier_plus_tard: dict, sommet: Tache):
    """
    Fonction récursive pour trouver les dates au plus tard d'un graphe.

    Préférer la fonction `calculer_calendriers` qui est plus simple à utiliser.
    """
    if int(sommet.nom) in calendrier_plus_tard.keys():  # Si on a déjà calculé la date :
        return calendrier_plus_tard

    # Sinon, on la calcule.
    # Pour ça, on prend la date - duree la plus petite parmi les successeurs
    duree = -1
    for successeur in sommet.successeurs:
        if int(successeur.nom) not in calendrier_plus_tard.keys():
            # Calcul de la date du successeur :
            calendrier_plus_tard = calculer_date_tard(calendrier_plus_tard, successeur)
        date_succ = calendrier_plus_tard[int(successeur.nom)] - sommet.duree
        if duree == -1:
            duree = date_succ
        else:
            duree = date_succ if date_succ < duree else duree
    calendrier_plus_tard[int(sommet.nom)] = duree
    return calendrier_plus_tard


def calculer_marges(calendriers):
    """
    Calcule les marges d'un graphe à partir des dates au plus tôt et au plus tard.

    :param calendriers: Calendrier obtenur grâce à la fonction `calculer_calendriers`.
    :return: Array contenant les marges.
    """
    marges = []
    for i in range(len(calendriers[0])):
        marges.append(calendriers[1][i] - calendriers[0][i])
    return marges


def trouver_chemins_critiques(graphe: Graphe, marges: [int]):
    """
    Retourne une liste de tous les chemins critiques d'un graphe.

    :param graphe: Le graphe contenant les chemins critiques à trouver.
    :param marges: Les marges calculées grâce à la fonction `calculer_marges`.
    :return: Une liste des chemins critiques.
    """
    return chemins_critiques(graphe.taches[0], marges)


def chemins_critiques(tache: Tache, marges: [int]):
    """
    Fonction récursive pour trouver les chemins critiques.

    Préférer la fonction `trouver_chemins_critiques` qui est plus simple à utiliser.
    """
    if tache.successeurs.size == 0:
        return [[tache]]
    chemins = []
    for successeur in tache.successeurs:
        if marges[int(successeur.nom)] == 0:
            for chemin in chemins_critiques(successeur, marges):
                chemins.append([tache] + chemin)
    return chemins


if __name__ == "__main__":
    # try:
    choice = 'y'
    while choice == 'y':
        fichiers = sorted([f for f in listdir("./files/") if f.endswith('.txt')])
        print("Choisissez un fichier à lire :")
        for i in range(len(fichiers)):
            print(i, "-", fichiers[i])
        selection = int(input())
        if selection not in range(len(fichiers)):
            print("Choix invalide. Appuyez sur une touche pour recommencer la sélection.")
            input()
            continue

        print("Construction du graphe d'ordonnancement :")
        graphe = lire_fichier("./files/" + fichiers[selection])
        graphe = ajouter_alpha(graphe)
        graphe = ajouter_omega(graphe)
        # Ajout des successeurs
        trouver_successeurs(graphe)
        graphe = trier_graphe(graphe)

        print("================== Arcs")
        afficher_arcs(graphe)
        print("================== Graphe sous forme matricielle")
        afficher_matrice_adjacence(graphe)
        print("================== Vérifications des conditions pour être un graphe d'ordonnancement")

        # Est-ce que le graphe possède un circuit ?
        b_contient_circuits = contient_circuits(graphe)
        b_contient_arcs_negatifs = contient_arcs_negatifs(graphe)
        print("Contient un ou plusieurs circuits :", b_contient_circuits)
        print("Contient des arcs négatifs :", b_contient_arcs_negatifs)

        if not b_contient_circuits and not b_contient_arcs_negatifs:
            print("Le graphe remplit les contraintes. On peut continuer.")
            print("================== Calcul des rangs")
            calculer_rangs(graphe)

            # Affichage des rangs
            print("================== Résultat rangs")
            print("On trouve que :")
            for tache in graphe.taches:
                print(tache.nom, "a pour rang", tache.rang)

            print("================== Calendriers")
            calendriers = calculer_calendriers(graphe)

            print("Dates au plus tôt :")
            for i in range(len(calendriers[0])):
                print(i, ":", calendriers[0][i])
            print("Dates au plus tard :")
            for i in range(len(calendriers[1])):
                print(i, ":", calendriers[1][i])

            marges = calculer_marges(calendriers)
            print("Marges :")
            for i in range(len(marges)):
                print(i, ":", marges[i])

            print("================== Chemins critiques")
            critiques = trouver_chemins_critiques(graphe, marges)
            for i in range(len(critiques)):
                print("Chemin critique", i, ":")
                chemin = []
                for sommet in critiques[i]:
                    chemin.append(str(sommet.nom))
                print(str.join(" -> ", chemin))
        else:
            print("Le graphe ne remplit pas les contraintes pour être un graphe d'ordonnancement. "
                  "On ne peut pas continuer.")

        choice = input("Souhaitez-vous lire un autre graphe ? (y/n) ")
    # except Exception as e:
    #     print("Une erreur est survenue.")
    #     print(e)
