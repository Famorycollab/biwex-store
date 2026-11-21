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
