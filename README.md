# Visualisation de Données Biologiques à l'aide de Jupyter et matplotlib

## Série de travaux pratiques

### Etude de cas: Protéomique quantitative

* Contexte biologique: Effet de la Tetracycline sur le contenu protéomique d'*E. coli*

* Données tabulées de Spectrométrie de Masse
        * 3 mutants *E.Coli* dans 3 conditions
        * ~2000 protéines quantifiées.

### Mise en place de l'environnement
* Telecharger le jeu de données auxilliare [ici](https://filesender.renater.fr/?s=download&token=13923b9f-94fa-47f8-8641-34afc781cb12)

* Vous l'extrairez dans ce repository `tar -xjf data_2021.tar.bz`

* L'organisation suivante est la plus simple 
```
-VDB_jupyter/
        |_lib/
        |_data/
        |_exercices/
        |_TCL_wt1.tsv
        |_requirements.txt
```

Deux jeux de dépendances sont requises:
1. hebergées sur pipy, à installez via `pip install -r requirements.txt`.
2. locales au répertoire `lib`, à déclarer dans le notebook.

### TP1a

- Lecture des données et manipulation avec la librairie [PANDAS](https://pandas.pydata.org/).
- Manipulation des bibliothèques SciPy et Numpy
- Production de figures matplotlib

### TP1b

- Scatter-plot simple et avancé
- Mise en forme riche d'objet dans le notebook