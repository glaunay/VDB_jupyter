# Visualisation de Données Biologiques à l'aide de Jupyter et matplotlib
## Mise en place de jupyter dans un environnement 

### CONDA ou VIRTUALENV

#### [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

Créez puis activez l'environnement

```bash
conda create --name <my_env_name>
conda activate <my_env_name>
```

#### [virtualenv (python>3.7)](https://docs.python.org/3/library/venv.html)


Créez puis activez l'environnement

```bash
python -m venv <my_env_name>
source <my_env_path>/bin/activate
```

#### Options et vérification
L'argument `-p <path_python_bin>` permet d'initialiser votre environnement avec n'importe quelle version de python disponible sur votre systeme.ex:`-p /usr/bin/python3.10`

Verifier les chemins de pip et python après activation:
* `which python`
* `which pip`

#### Ajout de l'environnement au notebook jupyter

```bash 
python -m ipykernel install --user --name=<my_env_name>
```

### [poetry](https://python-poetry.org/docs)

Poetry est un gestionnaire de paquets et d'environnement moderne. Attention, contrairement à **pip**, **poetry** ne supporte pas l'utilisation directe d'un fichier `requirements.txt`.
Il faudrait donc installer les dépendances de ces TP manuellement
```bash
poetry init --name <my_env>
poetry add "pendulum>=2.0.5" # libraries you want to use
poetry add -D jupyter # libraries for development use only
```

Pour lancer Jupyter dans l'environnement ainsi créé
```bash
poetry run jupyter notebook
````

Ou alors, si vous avez une instance globale de Jupyter, ajoutez-y l'environnement créé précedemment ainsi

```bash
poetry run ipython kernel install --user --name=<my_env>
```

## Série de travaux pratiques

### Etude de cas: Protéomique quantitative

* Contexte biologique: Effet de la Tetracycline sur le contenu protéomique d'*E. coli*

* Données tabulées de Spectrométrie de Masse
        * 3 mutants *E.Coli* dans 3 conditions
        * ~2000 protéines quantifiées.

### Mise en place de l'environnement
* Telecharger le jeu de données auxilliare [ici](https://filesender.renater.fr/?s=download&token=9069cb84-ef8a-4253-9a6f-9cfe7559108f)

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

Deux jeux de dépendances sont requis:
1. hebergées sur pipy, à installer via `pip install -r requirements.txt`.
2. locales au répertoire `lib`, à déclarer dans le notebook.

### TP0
 - Introduction à matplotlib
### TP1

- Lecture des données et manipulation avec la librairie [PANDAS](https://pandas.pydata.org/).
- Manipulation des bibliothèques SciPy et Numpy
- Production de figures matplotlib

### TP2

- Scatter-plot simple et avancé
- Mise en forme riche d'objet dans le notebook

### TP3

- Un premier volcano plot interactif
- Rappel sur les palettes de couleurs
- Implémentation d'un volcano plot complexe


### TP4
- widgets Jupyter
- layout Jupyter
- exemple basé sur volcano-plot
- projet libre

