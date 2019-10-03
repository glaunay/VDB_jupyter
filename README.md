# Visualisation de Données Biologiques à l'aide de Jupyter et matplotlib

## Série de travaux pratiques

### Etude de cas: Protéomique quantitative

* Contexte biologique: Effet de la Tetracycline sur le contenu protéomique d'*E. coli*

* Données tabulées de Spectrométrie de Masse
        * 3 mutants *E.Coli* dans 3 conditions
        * ~2000 protéines quantifiées.
    

<!---
    * Présentation protéomique de masse.
        * ciblée
        * label-free
    * MS data
        * Données de *E. coli* (3 mutants x 3 conditions)
        * ~2000 protéines quantifiées.
-->

### TP1

Lecture des données et manipulation avec la librairie [PANDAS](https://pandas.pydata.org/).

* Parcours de DataFrame
* Filtrage de DataFrame
* Conversion type Python

Statistiques descriptives des données

* Caractérisation des distributions
* Représentations graphiques des distributions

Modelisation statistique des données

* Manipulation de la bibliothèque [SciPy](https://www.scipy.org/)
* Représentations graphiques du modèle

### TP2

Analyse de l'enrichissement en termes GO

* Definitions de pathway fonctionels: modèle statistique
* Manipulation de l'ontologie GO
* Implémentation de l'analyse de l'enrichissement
* Mise forme des résultats adaptée au notebook
* Sérialisation des résultats

### TP3

Projection de données de types variées sur volcano plot

* Desérialisation de données
* Construction d'un scatter-plot élementaire
* Modéle d'évenement matplotlib
* Affichage des données point-spécifiques
* Intégration des données d'annotations

### TP4

Librairie [Widget Jupyter](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Basics.html)

* Le modèle de widget
* Association graphique widget avec interact
* Construction d'une interface de visualisation

### TP5

Utilisation de la librairie [ete3](http://etetoolkit.org/)

* Représentation en arbre de l'ontologie GO
* Projection des différents résultats de l'analyse d'enrichissement sur la représentation graphique des arbres
