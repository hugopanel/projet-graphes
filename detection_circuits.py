# calcul de l amatrice transitive
import graphe as graphe


def hasCycle(graphe):

    Graphe = len(graphe)

    matriceAdjagence = graphe.copy()  

# Cette boucle permet de calculer la matrice transitive en parcourant tous les sommets pour vérifier s'il exiszte un chemin
    # j et k me permettent de parcourir tout le graphe en mettant à jour la matrice

    for i in range(graphe):         # intémediraire pour la recherche de chemin entre les sommets i et j
        for j in range(graphe):
            for k in range(Graphe):
                matriceAdjagence[j][k] = matriceAdjagence[j][k] or matriceAdjagence[j][i] and matriceAdjagence[k][j]

        if matriceAdjagence[i][i]:
            return True
    return False



