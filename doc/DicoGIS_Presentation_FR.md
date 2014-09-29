DicoGIS : le dictionnaire de données SIG
====

Ou comment se créer un Petit Robert de l’information géographique en 5 minutes et 3 clics.
Je vous présente un petit utilitaire sans prétention sinon d'être bien pratique pour la gestion de données.

![DicoGIS - Animated demonstration](https://raw.githubusercontent.com/Guts/DicoGIS/master/doc/DicoGIS_demo.gif "DicoGIS - Animated demonstration")

# Présentation de l’outil

[DicoGIS](https://github.com/Guts/DicoGIS) est un petit utilitaire qui produit un dictionnaire de données au format Excel 2003 (.xls). Disponible sous forme d’exécutable Windows (.exe) sans installation ou sous forme de script (voir les pré-requis) il peut donc s’utiliser directement sur une clé USB par exemple.

DicoGIS - Logo

Il est particulièrement utile dans certains cas de figure :

- on vous refile une base de données fichiers ou PostGIS dans laquelle vous aimeriez savoir ce qu’il peut bien y avoir dedans ;
- dans le cadre de votre travail ou d’un projet, vous souhaitez fournir facilement un dictionnaire des données fournies, que ce soit à vos collègues, partenaires ou clients.

J’ai commencé à le développer en complément de [Metadator](https://github.com/Guts/Metadator) et je m’en sers aujourd’hui régulièrement, notamment pour réaliser un rapide audit des données et un support utile pour la conception des thésaurus internes dans la phase d’accompagnement des projets avec Isogeo (link is external).


# Caractéristiques techniques

## Côté développement

- développé en Python 2.7.8 (link is external) ;
- librairie GDAL/OGR 1.11.0-2 ;
- librairie python-excel/xlwt (link is external) pour écrire les fichiers Excel 2003 (.xls) ;
- librairie Tkinter / ttk (link is external) pour l'interface graphique (par défaut avec Python sur Windows mais non incluse par défaut dans les distributions Debian) ;
- librairie py2exe (link is external) pour générer facilement l'exécutable Windows.

Le code est disponible sur GitHub en licence GPL 3 (link is external), c’est-à-dire que chacun est tout à fait libre de réutiliser ou modifier le code.

## Côté utilisation

Les formats pris en compte sont potentiellement tous ceux de GDAL (link is external) et OGR (link is external) mais pour l'instant voici ceux qui sont implémentés :

- vecteurs : shapefile, tables MapInfo, GeoJSON, GML, KML
- rasters : ECW, GeoTIFF, JPEG
- bases de données "plates" (fichiers) : Esri File GDB
- CAO : DXF (+ listing des DWG)
- Documents cartos : Geospatial PDF

En mode script Python, c'est (a priori...) multiplateformes et a été testé sur:

- Ubuntu 12/14.04
- Windows 7/8.1
- Mac OS X (merci à GIS Blog Fr (link is external))

DicoGIS est disponible en 3 langues (Français, Anglais et Espagnol) (link is external) mais il est facile de personnaliser et/ou d'ajouter les traductions.

En ce qui concerne les performances, cela dépend surtout de la machine sur laquelle DicoGIS est lancé. De mon côté, le traitement met environ 30 secondes pour :

- une quarantaine de vecteurs,
- une dizaine de rasters ( qui pèsent environ 90 Mo au total),
- 7 FileGDB contenant une soixantaine de vecteurs
- et quelques DXF.

# Comment l'utiliser

1. Télécharger la dernière version :

    soit de l’exécutable Windows (link is external),
    soit du code source (link is external).

2. Dézipper et lancer DicoGIS.exe / le script DicoGIS.py

DicoGIS - Launch

3. Changer la langue au besoin

DicoGIS - Switch language

4.a Pour des données organisées en fichiers :

    Choisir le dossier parent : l’exploration commence et la barre de progression tourne jusqu’à la fin du listing
    Choisir les formats désirés

DicoGIS- Listing

4.b. Pour des données stockées dans une base PostgreSQL / PostGIS, c'est le même principe sauf qu'il faut entrer les paramètres de connexion :

 DicoGIS - Processing PostGIS

5. Lancer et attendre la fin du traitement : sauvegarder le fichier Excel généré.

DicoGIS - Processing files
6. Consulter le fichier en sortie et le fichier DicoGIS.log (dans lequel il y a un paquet d'informations ^^).
Et au final, quelles informations sur quels formats

En sortie, vous obtenez un fichier Excel (2003 = .xls) dans lequel les métadonnées sont organisées en différents onglets correspondant au type de donnée. J'ai fait une matrice des informations disponibles selon le format (link is external).


# A venir (ou pas)

Voici les quelques évolutions que j'envisage, mais vu que je ne suis pas mère Thérésa, que j'ai pas non plus beaucoup de temps disponible et que j'ai la flemme :), il ne faut pas y voir un quelconque engagement :

- prendre en compte de nouveaux formats : DGN, Spatialite, MXD, QGS, Geoconcept
- ajouter un onglet de statistiques globales avec de jolis graphiques ;
- basculer de python-xlwt vers xlsxwriter.
- un jour sur Python 3.x mais il faudrait déjà que py2exe soit stable de ce côté-là.
- travailler sur les performances en basculant les traitements en multiprocessing (mais je crois que ça coince avec py2exe).
