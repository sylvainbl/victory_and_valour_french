"""
Gestionnaire de cartes Victory & Valour
=======================================

Ce programme permet de :
- Charger les cartes extraites du PDF (cards.ipynb)
- Mélanger la pioche de manière secrète
- Distribuer une main au joueur
- Gérer la pioche et la défausse
- Permettre au joueur de piocher ou se défausser
- Organiser les cartes dans 3 dossiers : main, défausse, pioche

Usage:
    python gestionnaire_cartes.py
"""

import os
import random
import json
import shutil
from typing import List, Optional


class Carte:
    """Représente une carte individuelle"""

    def __init__(self, numero: int, nom_fichier: str):
        self.numero = numero
        self.nom_fichier = nom_fichier
        self.chemin = None

    def __str__(self):
        return f"Carte {self.numero}"

    def __repr__(self):
        return f"Carte({self.numero}, '{self.nom_fichier}')"


class GestionnaireCartes:
    """Gestionnaire principal pour les cartes Victory & Valour"""

    def __init__(self, dossier_cartes: str = "cartes_individuelles"):
        self.dossier_cartes = dossier_cartes
        self.dossier_main = "main"
        self.dossier_defausse = "defausse"
        self.dossier_pioche = "pioche"

        self.toutes_cartes: List[Carte] = []
        self.pioche: List[Carte] = []
        self.main_joueur: List[Carte] = []
        self.defausse: List[Carte] = []
        self.seed_melange: Optional[int] = None

    def creer_dossiers_jeu(self) -> None:
        """Crée les dossiers pour organiser les cartes"""
        dossiers = [self.dossier_main, self.dossier_defausse, self.dossier_pioche]

        for dossier in dossiers:
            if os.path.exists(dossier):
                shutil.rmtree(dossier)
            os.makedirs(dossier)

        print("📁 Dossiers de jeu créés : main, défausse, pioche")

    def copier_carte_vers_dossier(self, carte: Carte, dossier_destination: str) -> bool:
        """
        Copie une carte vers un dossier spécifique

        Args:
            carte: La carte à copier
            dossier_destination: Le dossier de destination

        Returns:
            bool: True si la copie s'est bien passée
        """
        if not carte.chemin or not os.path.exists(carte.chemin):
            print(f"⚠️  Fichier source introuvable pour {carte}")
            return False

        chemin_destination = os.path.join(dossier_destination, carte.nom_fichier)

        try:
            shutil.copy2(carte.chemin, chemin_destination)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la copie de {carte} : {e}")
            return False

    def organiser_cartes_dans_dossiers(self) -> None:
        """Organise toutes les cartes dans leurs dossiers respectifs"""
        print("🗂️  Organisation des cartes dans les dossiers...")

        # Vider les dossiers
        for dossier in [self.dossier_main, self.dossier_defausse, self.dossier_pioche]:
            if os.path.exists(dossier):
                for fichier in os.listdir(dossier):
                    os.remove(os.path.join(dossier, fichier))

        # Copier les cartes de la pioche
        for carte in self.pioche:
            self.copier_carte_vers_dossier(carte, self.dossier_pioche)

        # Copier les cartes de la main
        for carte in self.main_joueur:
            self.copier_carte_vers_dossier(carte, self.dossier_main)

        # Copier les cartes de la défausse
        for carte in self.defausse:
            self.copier_carte_vers_dossier(carte, self.dossier_defausse)

        print(f"  ✅ {len(self.pioche)} cartes copiées dans '{self.dossier_pioche}'")
        print(f"  ✅ {len(self.main_joueur)} cartes copiées dans '{self.dossier_main}'")
        print(
            f"  ✅ {len(self.defausse)} cartes copiées dans '{self.dossier_defausse}'"
        )

    def charger_cartes(self) -> bool:
        """
        Charge toutes les cartes depuis le dossier.

        Returns:
            bool: True si le chargement s'est bien passé
        """
        if not os.path.exists(self.dossier_cartes):
            print(f"❌ Erreur : Le dossier '{self.dossier_cartes}' n'existe pas.")
            print("   Exécutez d'abord l'extracteur de cartes.")
            return False

        print(f"📁 Chargement des cartes depuis '{self.dossier_cartes}'...")

        cartes_trouvees = []

        # Chercher les cartes numérotées de 1 à 54
        for numero in range(1, 55):
            nom_fichier = f"{numero}.png"
            chemin_complet = os.path.join(self.dossier_cartes, nom_fichier)

            if os.path.exists(chemin_complet):
                carte = Carte(numero, nom_fichier)
                carte.chemin = chemin_complet
                cartes_trouvees.append(carte)
            else:
                print(f"⚠️  Carte {numero} manquante : {nom_fichier}")

        self.toutes_cartes = cartes_trouvees
        print(f"✅ {len(self.toutes_cartes)} cartes chargées sur 54 attendues")

        if len(self.toutes_cartes) == 0:
            print(
                "❌ Aucune carte trouvée. Vérifiez que l'extraction s'est bien passée."
            )
            return False

        # Créer les dossiers de jeu
        self.creer_dossiers_jeu()

        return True

    def melanger_pioche(self, seed: Optional[int] = None) -> None:
        """
        Mélange secrètement toutes les cartes pour créer la pioche.

        Args:
            seed: Graine pour le mélange (optionnel, pour reproductibilité)
        """
        if seed is None:
            seed = random.randint(1, 1000000)

        self.seed_melange = seed

        # Copier toutes les cartes dans la pioche
        self.pioche = self.toutes_cartes.copy()

        # Mélanger avec la graine
        random.seed(seed)
        random.shuffle(self.pioche)

        print(f"🔀 Pioche mélangée secrètement ({len(self.pioche)} cartes)")
        print(f"   Seed de mélange : {seed} (gardé secret)")

        # Organiser les cartes dans les dossiers
        self.organiser_cartes_dans_dossiers()

    def distribuer_main_initiale(self, nombre_cartes: int = 7) -> bool:
        """
        Distribue une main initiale au joueur.

        Args:
            nombre_cartes: Nombre de cartes à distribuer

        Returns:
            bool: True si la distribution s'est bien passée
        """
        if len(self.pioche) < nombre_cartes:
            print(
                f"❌ Pas assez de cartes dans la pioche pour distribuer {nombre_cartes} cartes"
            )
            return False

        self.main_joueur = []

        for _ in range(nombre_cartes):
            carte = self.pioche.pop(0)  # Piocher du dessus
            self.main_joueur.append(carte)

        # Trier la main par numéro pour faciliter la visualisation
        self.main_joueur.sort(key=lambda c: c.numero)

        print(f"🎴 Main initiale distribuée : {nombre_cartes} cartes")

        # Réorganiser les cartes dans les dossiers
        self.organiser_cartes_dans_dossiers()

        return True

    def afficher_main(self) -> None:
        """Affiche la main du joueur"""
        if not self.main_joueur:
            print("🎴 Main vide")
            return

        print(f"\n🎴 Main du joueur ({len(self.main_joueur)} cartes):")
        for i, carte in enumerate(self.main_joueur):
            print(f"  {i + 1}. {carte}")

    def afficher_statuts(self) -> None:
        """Affiche l'état général du jeu"""
        print(f"\n📊 État du jeu:")
        print(
            f"  📚 Pioche: {len(self.pioche)} cartes (dossier: {self.dossier_pioche})"
        )
        print(
            f"  🎴 Main: {len(self.main_joueur)} cartes (dossier: {self.dossier_main})"
        )
        print(
            f"  🗑️  Défausse: {len(self.defausse)} cartes (dossier: {self.dossier_defausse})"
        )

        if self.defausse:
            print(f"     Dessus de la défausse: {self.defausse[-1]}")

    def piocher_carte(self) -> bool:
        """
        Le joueur pioche une carte du dessus de la pioche.

        Returns:
            bool: True si la pioche s'est bien passée
        """
        if not self.pioche:
            print("❌ La pioche est vide !")
            return False

        carte_piochee = self.pioche.pop(0)  # Prendre le dessus de la pioche
        self.main_joueur.append(carte_piochee)

        # Trier la main
        self.main_joueur.sort(key=lambda c: c.numero)

        print(f"✅ Vous avez pioché : {carte_piochee}")

        # Réorganiser les cartes dans les dossiers
        self.organiser_cartes_dans_dossiers()

        return True

    def defausser_carte(self, index_carte: int) -> bool:
        """
        Le joueur se défausse d'une carte de sa main.

        Args:
            index_carte: Index de la carte dans la main (1-based)

        Returns:
            bool: True si la défausse s'est bien passée
        """
        if not self.main_joueur:
            print("❌ Votre main est vide !")
            return False

        if index_carte < 1 or index_carte > len(self.main_joueur):
            print(f"❌ Index invalide. Choisissez entre 1 et {len(self.main_joueur)}")
            return False

        carte_defaussee = self.main_joueur.pop(index_carte - 1)  # Convertir en 0-based
        self.defausse.append(carte_defaussee)  # Ajouter au dessus de la défausse

        print(f"🗑️  Vous avez défaussé : {carte_defaussee}")

        # Réorganiser les cartes dans les dossiers
        self.organiser_cartes_dans_dossiers()

        return True

    def sauvegarder_partie(self, nom_fichier: str = "sauvegarde_partie.json") -> bool:
        """
        Sauvegarde l'état de la partie.

        Args:
            nom_fichier: Nom du fichier de sauvegarde

        Returns:
            bool: True si la sauvegarde s'est bien passée
        """
        try:
            etat = {
                "seed_melange": self.seed_melange,
                "pioche": [carte.numero for carte in self.pioche],
                "main_joueur": [carte.numero for carte in self.main_joueur],
                "defausse": [carte.numero for carte in self.defausse],
            }

            with open(nom_fichier, "w", encoding="utf-8") as f:
                json.dump(etat, f, indent=2, ensure_ascii=False)

            print(f"💾 Partie sauvegardée dans '{nom_fichier}'")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return False

    def charger_partie(self, nom_fichier: str = "sauvegarde_partie.json") -> bool:
        """
        Charge une partie sauvegardée.

        Args:
            nom_fichier: Nom du fichier de sauvegarde

        Returns:
            bool: True si le chargement s'est bien passé
        """
        if not os.path.exists(nom_fichier):
            print(f"❌ Fichier de sauvegarde '{nom_fichier}' introuvable")
            return False

        try:
            with open(nom_fichier, "r", encoding="utf-8") as f:
                etat = json.load(f)

            # Reconstruire les listes de cartes
            self.seed_melange = etat.get("seed_melange")

            self.pioche = [self.trouver_carte(num) for num in etat["pioche"]]
            self.main_joueur = [self.trouver_carte(num) for num in etat["main_joueur"]]
            self.defausse = [self.trouver_carte(num) for num in etat["defausse"]]

            print(f"📂 Partie chargée depuis '{nom_fichier}'")

            # Réorganiser les cartes dans les dossiers
            self.organiser_cartes_dans_dossiers()

            return True

        except Exception as e:
            print(f"❌ Erreur lors du chargement : {e}")
            return False

    def trouver_carte(self, numero: int) -> Carte:
        """Trouve une carte par son numéro"""
        for carte in self.toutes_cartes:
            if carte.numero == numero:
                return carte
        # Si pas trouvée, créer une carte temporaire
        return Carte(numero, f"{numero}.png")


def menu_principal(gestionnaire: GestionnaireCartes) -> None:
    """Interface utilisateur en mode texte"""

    while True:
        print("\n" + "=" * 50)
        print("🎴 GESTIONNAIRE DE CARTES VICTORY & VALOUR")
        print("=" * 50)

        gestionnaire.afficher_statuts()
        gestionnaire.afficher_main()

        print("\n🎯 Actions disponibles:")
        print("  1. Piocher une carte")
        print("  2. Se défausser d'une carte")
        print("  3. Sauvegarder la partie")
        print("  4. Charger une partie")
        print("  5. Recommencer (nouveau mélange)")
        print("  6. Réorganiser les cartes dans les dossiers")
        print("  0. Quitter")

        try:
            choix = input("\n👉 Votre choix : ").strip()

            if choix == "0":
                print("👋 Au revoir !")
                break

            elif choix == "1":
                gestionnaire.piocher_carte()

            elif choix == "2":
                if gestionnaire.main_joueur:
                    try:
                        index = int(
                            input(
                                f"Quelle carte défausser ? (1-{len(gestionnaire.main_joueur)}) : "
                            )
                        )
                        gestionnaire.defausser_carte(index)
                    except ValueError:
                        print("❌ Veuillez entrer un nombre valide")
                else:
                    print("❌ Votre main est vide !")

            elif choix == "3":
                gestionnaire.sauvegarder_partie()

            elif choix == "4":
                if gestionnaire.charger_partie():
                    print("✅ Partie chargée avec succès !")

            elif choix == "5":
                print("🔄 Nouveau mélange...")
                gestionnaire.melanger_pioche()
                gestionnaire.main_joueur = []
                gestionnaire.defausse = []
                gestionnaire.distribuer_main_initiale()

            elif choix == "6":
                print("🗂️  Réorganisation des cartes...")
                gestionnaire.organiser_cartes_dans_dossiers()
                print("✅ Cartes réorganisées dans les dossiers !")

            else:
                print("❌ Choix invalide")

        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur : {e}")


def main():
    """Fonction principale"""
    print("🎮 Démarrage du gestionnaire de cartes Victory & Valour")

    # Créer le gestionnaire
    gestionnaire = GestionnaireCartes()

    # Charger les cartes
    if not gestionnaire.charger_cartes():
        return

    # Mélanger et distribuer
    gestionnaire.melanger_pioche()

    if not gestionnaire.distribuer_main_initiale():
        return

    # Lancer l'interface
    menu_principal(gestionnaire)


if __name__ == "__main__":
    main()
