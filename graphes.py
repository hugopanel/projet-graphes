import numpy as np


class Graphe:
    taches: np.ndarray
    taches = np.array([])


class Tache:
    duree: int
    duree = None

    nom: int
    nom = None

    rang: int
    rang = None

    predecesseurs: np.ndarray
    predecesseurs = np.array([])

    successeurs: np.ndarray
    successeurs = np.array([])
