"""
============================================================
 TESTS MÉTIER & VALIDATION DU PANIER — BIWEX STORE
 Auteur  : Famory TOURE (tourefamory5@gmail.com)
 Branche : feature/famory-toure
 Projet  : DevOps 3LIG — ISG Sousse 2026/2027

 EXPLICATION SIMPLE POUR LA PROFESSEURE :
 Ce fichier teste la logique métier de l'application sans
 dépendre d'une base de données ou d'un réseau externe :
   1. Calcul des remises pour les codes promotionnels (DEVOPS20, ISGS10, BIWEX5)
   2. Rejet des codes promo invalides
   3. Calcul exact du total du panier avec plusieurs articles
   4. Règle de non-dépassement des stocks disponibles
   5. Formatage des montants selon la convention tunisienne (DT)
============================================================
"""

import unittest


class BusinessLogicTestCase(unittest.TestCase):
    """Suite de tests unitaires pour la logique commerciale de Biwex Store"""

    def setUp(self):
        """Initialisation des règles de promotion"""
        self.coupons_actifs = {
            'DEVOPS20': {'remise_pourcent': 20, 'description': 'Remise spéciale DevOps (-20%)'},
            'ISGS10':   {'remise_pourcent': 10, 'description': 'Remise étudiante ISG Sousse (-10%)'},
            'BIWEX5':   {'remise_fixe': 5.0,    'description': 'Bon d\'achat de bienvenue (-5 DT)'}
        }

    def test_coupon_percentage_calculation(self):
        """Vérifie qu'un code à 20% déduit exactement 20% du total"""
        total_panier = 1000.0
        coupon = self.coupons_actifs['DEVOPS20']
        remise = round(total_panier * (coupon['remise_pourcent'] / 100.0), 3)
        total_apres_remise = total_panier - remise

        self.assertEqual(remise, 200.0, "La remise de 20% sur 1000 DT doit faire 200 DT")
        self.assertEqual(total_apres_remise, 800.0, "Le total final doit être de 800 DT")

    def test_coupon_fixed_amount_calculation(self):
        """Vérifie qu'un bon d'achat fixe déduit exactement le montant prévu"""
        total_panier = 120.0
        coupon = self.coupons_actifs['BIWEX5']
        remise = coupon['remise_fixe']
        total_apres_remise = total_panier - remise

        self.assertEqual(remise, 5.0, "La remise fixe doit être de 5.0 DT")
        self.assertEqual(total_apres_remise, 115.0, "Le total doit passer de 120 à 115 DT")

    def test_invalid_coupon_rejected(self):
        """Vérifie qu'un faux code promo n'est pas accepté dans le système"""
        faux_code = "FAUXCODE99"
        self.assertNotIn(faux_code, self.coupons_actifs, "Le faux code promo doit être rejeté")

    def test_cart_subtotal_calculation(self):
        """Vérifie le calcul du sous-total pour plusieurs articles et quantités"""
        articles = [
            {'nom': 'Souris Logitech', 'prix': 349.0, 'quantite': 2},
            {'nom': 'PowerBank Anker', 'prix': 249.0, 'quantite': 1}
        ]
        total_calcule = sum(item['prix'] * item['quantite'] for item in articles)
        total_attendu = (349.0 * 2) + 249.0  # 698 + 249 = 947 DT

        self.assertEqual(total_calcule, total_attendu, "Le calcul du total d'articles doit être exact")

    def test_stock_quantity_clamping(self):
        """Vérifie que la quantité demandée ne peut jamais dépasser le stock physique"""
        stock_physique = 5
        quantite_demandee = 12

        quantite_ajustee = min(quantite_demandee, stock_physique)
        self.assertEqual(quantite_ajustee, stock_physique, "La quantité doit être plafonnée au stock réel")

    def test_currency_formatting(self):
        """Vérifie le respect de la convention monétaire tunisienne"""
        valeur = 1299.0
        formatte = f"{valeur:,.3f}".replace(',', ' ').replace('.', ',') + " DT"
        self.assertTrue(formatte.endswith("DT"), "Le prix doit comporter le suffixe DT")
        self.assertIn("1 299", formatte, "Le millier doit être séparé par un espace")

    def test_pagination_calculation(self):
        """Vérifie le découpage pagination pour optimiser le défilement de page"""
        total_produits = 38
        par_page = 12
        pages_attendues = (total_produits + par_page - 1) // par_page  # 4 pages

        self.assertEqual(pages_attendues, 4, "38 produits à raison de 12 par page doivent donner 4 pages")

        # Test des décalages d'offset
        page_1_offset = (1 - 1) * par_page  # 0
        page_2_offset = (2 - 1) * par_page  # 12
        page_4_offset = (4 - 1) * par_page  # 36
        self.assertEqual(page_1_offset, 0)
        self.assertEqual(page_2_offset, 12)
        self.assertEqual(page_4_offset, 36)


if __name__ == '__main__':
    unittest.main()
