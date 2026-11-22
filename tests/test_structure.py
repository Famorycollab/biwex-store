"""
============================================================
 TESTS DE SYNTAXE & CONFIGURATION — BIWEX STORE
 Auteur : Famory TOURE (famorytoure5@gmail.com)
 Branche : feature/famory-toure
 
 Teste la validité des fichiers clés sans dépendance externe.
============================================================
"""

import unittest
import os
import py_compile


class ProjectStructureTest(unittest.TestCase):
    """Vérifie l'intégrité de l'arborescence et des fichiers DevOps"""

    def setUp(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_required_files_exist(self):
        """Vérifie que tous les fichiers requis par le pipeline CI/CD existent"""
        required_files = [
            'app.py',
            'database.py',
            'requirements.txt',
            'Dockerfile',
            'Jenkinsfile',
            'Jenkinsfile-PR',
            'Jenkinsfile-Tag',
            '.dockerignore',
            '.gitignore',
            'scripts/smoke_test.py',
            'scripts/benchmark.py',
            'tests/test_business_logic.py'
        ]
        for rel_path in required_files:
            full_path = os.path.join(self.root_dir, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Fichier manquant: {rel_path}")

    def test_product_assets_exist(self):
        """Vérifie la présence des images vectorielles et photos réelles locales (mode hors-ligne garanti)"""
        categories = ['smartphones', 'laptops', 'audio', 'gaming', 'tablettes', 'tv', 'accessoires']
        for cat in categories:
            svg_path = os.path.join(self.root_dir, 'static', 'img', 'products', f"{cat}.svg")
            self.assertTrue(os.path.exists(svg_path), f"Image vectorielle manquante pour: {cat}")

        # Vérifie les photos réelles clés intégrées (téléchargées par Famory & Abdoul)
        real_photos = [
            'iphone_15_pro.jpg', 'macbook_pro_m3.jpg', 'sony_wh1000xm5.jpg',
            'ipad_pro.jpg', 'samsung_qled_tv.jpg', 'lg_oled_tv.jpg',
            'anker_powerbank.jpg', 'apple_watch_9.jpg', 'lenovo_legion.jpg',
            'galaxy_z_fold5.jpg', 'razer_blackwidow.jpg', 'gaming_monitor.jpg',
            'playstation_5.jpg', 'pixel_8_pro.jpg', 'bose_qc_ultra.jpg',
            'hp_omen_16.jpg', 'galaxy_a55.jpg', 'galaxy_watch_6.jpg',
            'asus_rog_ally.jpg', 'nintendo_switch_oled.jpg'
        ]
        for photo in real_photos:
            photo_path = os.path.join(self.root_dir, 'static', 'img', 'products', photo)
            self.assertTrue(os.path.exists(photo_path), f"Photo réelle manquante: {photo}")
            self.assertGreater(os.path.getsize(photo_path), 0, f"Photo réelle vide: {photo}")

    def test_python_syntax(self):
        """Compile les scripts Python pour détecter les erreurs de syntaxe"""
        python_files = [
            'app.py',
            'database.py',
            'scripts/smoke_test.py',
            'scripts/benchmark.py',
            'tests/test_business_logic.py'
        ]
        for rel_path in python_files:
            full_path = os.path.join(self.root_dir, rel_path)
            try:
                py_compile.compile(full_path, doraise=True)
            except py_compile.PyCompileError as e:
                self.fail(f"Erreur de syntaxe dans {rel_path}: {e}")


if __name__ == '__main__':
    unittest.main()
