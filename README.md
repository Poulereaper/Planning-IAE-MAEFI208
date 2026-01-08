# 📅 Planning IAE Paris - MAE FI 208

Ce projet permet de récupérer automatiquement l'emploi du temps du **Master MAE (Groupe 208)** de l'IAE Paris-Sorbonne et de le convertir en un format compatible avec tous les agendas (iPhone, Google Agenda, Outlook).

Contrairement au planning officiel, cette version est **enrichie** avec les détails du programme pédagogique (noms complets des matières, modalités d'examens, noms des intervenants).

## Comment s'abonner au calendrier ?

Pour avoir votre emploi du temps toujours à jour sur votre téléphone ou ordinateur, ajoutez l'URL suivante via la fonction "S'abonner à un calendrier" (ou "Ajouter un calendrier par URL") :

**Lien du calendrier (.ics) :**

```
https://raw.githubusercontent.com/Poulereaper/Planning-IAE-MAEFI208/refs/heads/main/planning.ics
```

### Via QR Code
Scannez ce code pour ajouter directement le calendrier à votre calendrier :

<img width="490" height="490" alt="image" src="planningicsIAE.png" />

---

## ✨ Fonctionnalités

* **Synchronisation automatique** : Le planning est mis à jour tous les jours (matin et soir) via GitHub Actions.
* **Données enrichies** :
    * Ajout du nom complet des UE et des professeurs (basé sur le programme officiel).
    * Détails sur les modalités d'évaluation dans la description de l'événement.
* **Détection intelligente** :
    * 🚨 Identification automatique des **Examens** (notamment ceux à la Maison des Examens à Arcueil).
    * ℹ️ Repérage probable des amphis d'**ouverture** et de **clôture**.
* **Gestion des fuseaux horaires** : Conversion correcte des heures (Paris Time) pour éviter les décalages.

## 🛠 Installation locale (pour les devs)

Si vous souhaitez modifier le script ou le lancer manuellement :

1.  Clonez le repo :
    ```bash
    git clone [https://github.com/Poulereaper/Planning-IAE-MAEFI208.git](https://github.com/Poulereaper/Planning-IAE-MAEFI208.git)
    cd Planning-IAE-MAEFI208
    ```

2.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3.  Lancez le scraper :
    ```bash
    python scraper.py
    ```

Le fichier `planning.ics` sera généré à la racine.

## ⚙️ Automatisation

Le workflow GitHub Actions `.github/workflows/update.yml` exécute le script automatiquement :
* Tous les jours à 7h00 et 16h00 (UTC).
* Met à jour le fichier `planning.ics` et le pousse sur le repo si des changements sont détectés.


