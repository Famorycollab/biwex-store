# ============================================================
#  GÉNÉRATEUR DE PRÉSENTATION POWERPOINT - BIWEX STORE CI/CD & DEVSECOPS
#  Projet DevOps 3LIG - ISG Sousse 2026/2027
#  Binôme : Famory TOURE & Abdoul TRAORE
# ============================================================

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# ── Palette couleurs Biwex ──────────────────────────────────
RED      = RGBColor(0xE0, 0x1E, 0x22)   # Rouge Biwex
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
DARK     = RGBColor(0x1E, 0x29, 0x3B)   # Gris foncé
LIGHT    = RGBColor(0xF8, 0xF9, 0xFA)   # Fond clair
ACCENT   = RGBColor(0xFF, 0x6B, 0x6B)   # Rouge doux
GREEN    = RGBColor(0x22, 0xC5, 0x5E)   # Vert succès
BLUE     = RGBColor(0x2D, 0x9C, 0xDB)   # Bleu info
GRAY     = RGBColor(0x64, 0x74, 0x8B)   # Gris neutre
PURPLE   = RGBColor(0x8B, 0x5C, 0xF6)   # Violet DevSecOps

# ── Dimensions diapo 16:9 ──────────────────────────────────
W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]  # layout vide

TOTAL_SLIDES = 16

# ── Helpers ────────────────────────────────────────────────

def add_rect(slide, x, y, w, h, fill_color, border_color=None, border_pt=0):
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color and border_pt > 0:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, x, y, w, h, font_size=18, bold=False,
             color=WHITE, align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return txBox


def header_bar(slide, title, subtitle=""):
    add_rect(slide, 0, 0, W, Inches(1.3), RED)
    add_text(slide, title, Inches(0.4), Inches(0.08), W - Inches(0.8), Inches(0.75),
             font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, Inches(0.4), Inches(0.75), W - Inches(0.8), Inches(0.45),
                 font_size=13, bold=False, color=RGBColor(0xFF, 0xCC, 0xCC), align=PP_ALIGN.LEFT)


def footer_bar(slide, page_num, total=TOTAL_SLIDES):
    add_rect(slide, 0, H - Inches(0.42), W, Inches(0.42), DARK)
    add_text(slide, "Biwex Store — Pipeline CI/CD & DevSecOps | ISG Sousse 2026/2027 | Famory TOURÉ & Abdoul TRAORÉ",
             Inches(0.3), H - Inches(0.42), Inches(10), Inches(0.42),
             font_size=9, color=GRAY, align=PP_ALIGN.LEFT)
    add_text(slide, f"{page_num}/{total}",
             W - Inches(1.2), H - Inches(0.42), Inches(1.0), Inches(0.42),
             font_size=10, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)


def bullet_block(slide, items, x, y, w, h, item_color=DARK, marker_color=RED,
                 font_size=14, marker="▶"):
    item_h = h / len(items) if items else h
    for i, item in enumerate(items):
        iy = y + i * item_h
        add_text(slide, marker, x, iy, Inches(0.3), item_h,
                 font_size=font_size, bold=True, color=marker_color, align=PP_ALIGN.LEFT)
        add_text(slide, item, x + Inches(0.32), iy, w - Inches(0.35), item_h,
                 font_size=font_size, color=item_color, align=PP_ALIGN.LEFT)


# ════════════════════════════════════════════════════════════
#  SLIDE 1 - TITRE
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, DARK)
add_rect(slide, 0, Inches(2.4), W, Inches(2.8), RED)
add_rect(slide, 0, Inches(2.4), W, Inches(0.06), WHITE)
add_rect(slide, 0, Inches(5.14), W, Inches(0.06), WHITE)

add_text(slide, "Pipeline CI/CD & DevSecOps", Inches(0.5), Inches(2.55), W - Inches(1), Inches(1.1),
         font_size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text(slide, "Biwex Store — Projet DevOps & Qualité Continue (4 Pipelines Jenkins)", Inches(0.5), Inches(3.65), W - Inches(1), Inches(0.8),
         font_size=24, bold=False, color=RGBColor(0xFF, 0xE0, 0xE0), align=PP_ALIGN.CENTER)

add_rect(slide, Inches(1.5), Inches(5.5), Inches(2.5), Inches(0.55), RGBColor(0x2D, 0x3D, 0x55))
add_text(slide, "📍 ISG Sousse", Inches(1.5), Inches(5.5), Inches(2.5), Inches(0.55),
         font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(4.4), Inches(5.5), Inches(2.8), Inches(0.55), RGBColor(0x2D, 0x3D, 0x55))
add_text(slide, "👨‍💻 Famory TOURÉ & Abdoul TRAORÉ", Inches(4.4), Inches(5.5), Inches(2.8), Inches(0.55),
         font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(7.6), Inches(5.5), Inches(2.0), Inches(0.55), RGBColor(0x2D, 0x3D, 0x55))
add_text(slide, "🎓 Module DevOps", Inches(7.6), Inches(5.5), Inches(2.0), Inches(0.55),
         font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(10.0), Inches(5.5), Inches(1.8), Inches(0.55), RGBColor(0x2D, 0x3D, 0x55))
add_text(slide, "📅 Nov. 2026", Inches(10.0), Inches(5.5), Inches(1.8), Inches(0.55),
         font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

footer_bar(slide, 1)

# ════════════════════════════════════════════════════════════
#  SLIDE 2 - SOMMAIRE
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Sommaire", "Plan de la présentation")

items_col1 = [
    ("01", "Présentation du Projet Biwex Store"),
    ("02", "Architecture Globale CI/CD"),
    ("03", "Stratégie de Branches Git"),
    ("04", "Les 4 Pipelines Jenkins (CI/CD + DevSecOps)"),
    ("05", "Pipeline Principal (Jenkinsfile)"),
    ("06", "Pipeline Pull Request (Jenkinsfile-PR)"),
    ("07", "Pipeline Tag/Release (Jenkinsfile-Tag)"),
    ("08", "Pipeline Nightly DevSecOps (Jenkinsfile-Nightly)"),
]
items_col2 = [
    ("09", "Tests Automatisés & Benchmark"),
    ("10", "Docker & Multi-Stage Build"),
    ("11", "Déploiement Continu & Versioning"),
    ("12", "Répartition des Contributions"),
    ("13", "Métriques & Résultats"),
    ("14", "Démonstration Live"),
    ("15", "Conclusion"),
]

for i, (num, text) in enumerate(items_col1):
    y = Inches(1.45) + i * Inches(0.64)
    add_rect(slide, Inches(0.4), y, Inches(0.5), Inches(0.48), RED)
    add_text(slide, num, Inches(0.4), y, Inches(0.5), Inches(0.48),
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, text, Inches(1.05), y, Inches(5.5), Inches(0.48),
             font_size=12, color=DARK, align=PP_ALIGN.LEFT)

for i, (num, text) in enumerate(items_col2):
    y = Inches(1.45) + i * Inches(0.64)
    add_rect(slide, Inches(7.0), y, Inches(0.5), Inches(0.48), DARK)
    add_text(slide, num, Inches(7.0), y, Inches(0.5), Inches(0.48),
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, text, Inches(7.65), y, Inches(5.4), Inches(0.48),
             font_size=12, color=DARK, align=PP_ALIGN.LEFT)

footer_bar(slide, 2)

# ════════════════════════════════════════════════════════════
#  SLIDE 3 - PRÉSENTATION DU PROJET
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Présentation du Projet", "Biwex Store — E-commerce Flask")

cards = [
    ("🛒", "E-commerce Flask", "Site de vente high-tech\npour le marché tunisien"),
    ("📦", "38 Produits", "7 catégories de produits\ntechnologiques"),
    ("🗄️", "Stack Technique", "Flask + SQLAlchemy\nSQLite + Gunicorn"),
    ("🌐", "Accès", "http://localhost:5000\nDocker en production"),
]
for i, (icon, title, desc) in enumerate(cards):
    x = Inches(0.4) + i * Inches(3.2)
    add_rect(slide, x, Inches(1.5), Inches(3.0), Inches(2.3), WHITE,
             border_color=RED, border_pt=2)
    add_text(slide, icon, x, Inches(1.6), Inches(3.0), Inches(0.7),
             font_size=28, align=PP_ALIGN.CENTER, color=RED)
    add_text(slide, title, x, Inches(2.3), Inches(3.0), Inches(0.5),
             font_size=14, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    add_text(slide, desc, x, Inches(2.8), Inches(3.0), Inches(0.8),
             font_size=11, color=GRAY, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.4), Inches(4.0), W - Inches(0.8), Inches(2.5), WHITE,
         border_color=DARK, border_pt=1)
add_rect(slide, Inches(0.4), Inches(4.0), Inches(0.08), Inches(2.5), RED)
add_text(slide, "Contexte du Projet", Inches(0.65), Inches(4.1), Inches(12), Inches(0.4),
         font_size=14, bold=True, color=DARK, align=PP_ALIGN.LEFT)
context_items = [
    "Module : Introduction au DevOps — 3LIG, ISG Sousse 2026/2027",
    "Objectif : Mettre en œuvre un pipeline CI/CD et DevSecOps complet sur un projet réel",
    "Équipe : Famory TOURÉ (lead) & Abdoul TRAORÉ | Dépôt GitHub : github.com/Famorycollab/biwex-store",
    "Résultat : 6 versions livrées (v1.0.0 → v1.6.0) | 4 Pipelines Jenkins | 100% fonctionnel",
]
bullet_block(slide, context_items, Inches(0.65), Inches(4.55), W - Inches(1.2), Inches(1.8),
             item_color=DARK, font_size=12)

footer_bar(slide, 3)

# ════════════════════════════════════════════════════════════
#  SLIDE 4 - ARCHITECTURE GLOBALE
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Architecture Globale CI/CD & DevSecOps", "Flux complet du développement à la production sécurisée")

boxes = [
    ("👨‍💻\nDéveloppeur", RGBColor(0x2D, 0x3D, 0x55)),
    ("📁\nGitHub\nRepository", BLUE),
    ("⚙️\nJenkins\nCI/CD", RED),
    ("🐳\nDocker\nBuild", RGBColor(0x09, 0x69, 0xDA)),
    ("🧪\nTests &\nSécurité", RGBColor(0xE0, 0x7B, 0x22)),
    ("🚀\nProduction\nlocalhost:5000", GREEN),
]

box_w = Inches(1.9)
box_h = Inches(1.7)
start_x = Inches(0.3)
y = Inches(1.6)

for i, (label, color) in enumerate(boxes):
    x = start_x + i * (box_w + Inches(0.2))
    add_rect(slide, x, y, box_w, box_h, color)
    add_text(slide, label, x, y, box_w, box_h,
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(boxes) - 1:
        add_text(slide, "→", x + box_w + Inches(0.01), y + Inches(0.6), Inches(0.22), Inches(0.5),
                 font_size=18, bold=True, color=RED, align=PP_ALIGN.CENTER)

labels_sub = ["git push", "webhook trigger", "4 pipelines", "image créée", "smoke + audit AST", "déploiement"]
for i, lab in enumerate(labels_sub):
    x = start_x + i * (box_w + Inches(0.2))
    add_text(slide, lab, x, y + box_h + Inches(0.05), box_w, Inches(0.35),
             font_size=9, italic=True, color=GRAY, align=PP_ALIGN.CENTER)

# 4 Pipelines Jenkins
add_rect(slide, Inches(0.3), Inches(3.9), W - Inches(0.6), Inches(2.7), WHITE,
         border_color=RED, border_pt=2)
add_text(slide, "Les 4 Pipelines Jenkins de l'Architecture :", Inches(0.5), Inches(4.0), Inches(7), Inches(0.35),
         font_size=13, bold=True, color=DARK, align=PP_ALIGN.LEFT)

pipe_boxes = [
    ("📋 Jenkinsfile\nPush dev (Build Parallèle)", DARK),
    ("🔍 Jenkinsfile-PR\nValidation Pull Request", BLUE),
    ("🏷️ Jenkinsfile-Tag\nRelease officielle SemVer", GREEN),
    ("🛡️ Jenkinsfile-Nightly\nDevSecOps & Audit Sécurité", PURPLE),
]
for i, (txt, col) in enumerate(pipe_boxes):
    x = Inches(0.5) + i * Inches(3.1)
    add_rect(slide, x, Inches(4.45), Inches(2.9), Inches(1.8), col)
    add_text(slide, txt, x, Inches(4.45), Inches(2.9), Inches(1.8),
             font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

footer_bar(slide, 4)

# ════════════════════════════════════════════════════════════
#  SLIDE 5 - STRATÉGIE DE BRANCHES GIT
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Stratégie de Branches Git", "GitFlow adapté — Workflow collaboratif structuré")

branches = [
    ("main", "🏭 Production stable", RGBColor(0x22, 0xC5, 0x5E)),
    ("dev", "🔧 Intégration continue", BLUE),
    ("feature/famory-toure", "👨‍💻 Famory — Lead Developer", RED),
    ("feature/abdoul-traore", "👤 Abdoul — Contributeur", RGBColor(0xE0, 0x7B, 0x22)),
    ("feature/health-endpoint", "❤️ Endpoint de santé /health", RGBColor(0x9B, 0x59, 0xB6)),
]

for i, (name, desc, color) in enumerate(branches):
    y_b = Inches(1.55) + i * Inches(0.95)
    add_rect(slide, Inches(0.4), y_b, Inches(2.8), Inches(0.7), color)
    add_text(slide, name, Inches(0.4), y_b, Inches(2.8), Inches(0.7),
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, Inches(3.3), y_b + Inches(0.3), Inches(0.4), Inches(0.05), color)
    add_rect(slide, Inches(3.9), y_b, Inches(5.5), Inches(0.7), WHITE,
             border_color=color, border_pt=1)
    add_text(slide, desc, Inches(3.9), y_b, Inches(5.5), Inches(0.7),
             font_size=12, color=DARK, align=PP_ALIGN.LEFT)

add_rect(slide, Inches(0.4), Inches(6.3), W - Inches(0.8), Inches(0.75), DARK)
flow_text = "Flux : feature → Pull Request → dev (Pipeline-PR) → main (merge) → Tag vX.Y.Z (Release) + Audit DevSecOps"
add_text(slide, flow_text, Inches(0.6), Inches(6.3), W - Inches(1.2), Inches(0.75),
         font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

footer_bar(slide, 5)

# ════════════════════════════════════════════════════════════
#  SLIDE 6 - LES 4 PIPELINES JENKINS
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Les 4 Pipelines Jenkins", "Couverture complète du cycle de vie DevOps & DevSecOps")

pipelines = [
    {
        "file": "Jenkinsfile",
        "titre": "Pipeline Principal",
        "trigger": "Push sur dev",
        "color": DARK,
        "points": [
            "6 étapes automatiques",
            "Build parallèle Py 3.11 & 3.12",
            "Smoke test HTTP live",
            "Archivage rapports Jenkins",
        ],
    },
    {
        "file": "Jenkinsfile-PR",
        "titre": "Pipeline Pull Request",
        "trigger": "Création d'une PR",
        "color": BLUE,
        "points": [
            "Bloque les PR directes sur main",
            "Vérifie la cible 'dev'",
            "Build + smoke test PR",
            "Décision fusion automatique",
        ],
    },
    {
        "file": "Jenkinsfile-Tag",
        "titre": "Pipeline Release",
        "trigger": "Tag vX.Y.Z",
        "color": GREEN,
        "points": [
            "Validation SemVer obligatoire",
            "Images taguées + :latest",
            "20 tentatives smoke test",
            "Manifeste de release scellé",
        ],
    },
    {
        "file": "Jenkinsfile-Nightly",
        "titre": "Pipeline DevSecOps",
        "trigger": "Cron nocturne (2h00)",
        "color": PURPLE,
        "points": [
            "Audit statique AST Python",
            "Audit dépendances & Docker",
            "Contrôle intégrité SQLite",
            "Benchmark latence HTTP",
        ],
    },
]

for i, p in enumerate(pipelines):
    x = Inches(0.3) + i * Inches(3.2)
    add_rect(slide, x, Inches(1.4), Inches(3.05), Inches(0.55), p["color"])
    add_text(slide, p["file"], x, Inches(1.4), Inches(3.05), Inches(0.55),
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, x, Inches(1.95), Inches(3.05), Inches(4.7), WHITE,
             border_color=p["color"], border_pt=2)
    add_text(slide, p["titre"], x + Inches(0.1), Inches(2.05), Inches(2.85), Inches(0.35),
             font_size=12, bold=True, color=DARK, align=PP_ALIGN.LEFT)
    add_rect(slide, x + Inches(0.1), Inches(2.45), Inches(2.85), Inches(0.3), RGBColor(0xF0, 0xF4, 0xF8))
    add_text(slide, f"⚡ {p['trigger']}", x + Inches(0.15), Inches(2.47), Inches(2.75), Inches(0.26),
             font_size=9, italic=True, color=GRAY, align=PP_ALIGN.LEFT)
    for j, pt in enumerate(p["points"]):
        py = Inches(2.85) + j * Inches(0.5)
        add_rect(slide, x + Inches(0.12), py + Inches(0.08), Inches(0.06), Inches(0.28), p["color"])
        add_text(slide, pt, x + Inches(0.28), py, Inches(2.65), Inches(0.48),
                 font_size=10, color=DARK, align=PP_ALIGN.LEFT)

footer_bar(slide, 6)

# ════════════════════════════════════════════════════════════
#  SLIDE 7 - PIPELINE PRINCIPAL DÉTAIL
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Pipeline Principal — Jenkinsfile", "6 étapes automatiques déclenchées sur push → dev")

steps_data = [
    ("1\nCheckout", "Télécharge le code\nsource GitHub", DARK),
    ("2\nSetup", "Vérifie les fichiers\net Docker", BLUE),
    ("3\nBuild\nParallèle", "2 images Docker\nPy3.11 + Py3.12", RED),
    ("4\nRun\nDocker", "Lance le conteneur\nde test", RGBColor(0xE0, 0x7B, 0x22)),
    ("5\nSmoke\nTest", "Test HTTP 200\nretry x15", RGBColor(0x9B, 0x59, 0xB6)),
    ("6\nArchive", "Rapport +\nartefacts Jenkins", GREEN),
]

box_w = Inches(1.9)
box_h = Inches(1.9)
start_x = Inches(0.3)
y = Inches(1.5)

for i, (title, desc, col) in enumerate(steps_data):
    x = start_x + i * (box_w + Inches(0.18))
    add_rect(slide, x, y, box_w, box_h, col)
    add_text(slide, title, x, y + Inches(0.1), box_w, Inches(0.9),
             font_size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, x, y + Inches(0.9), box_w, Inches(0.05), WHITE)
    add_text(slide, desc, x, y + Inches(0.98), box_w, Inches(0.9),
             font_size=10, color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(steps_data) - 1:
        add_text(slide, "→", x + box_w + Inches(0.0), y + Inches(0.65), Inches(0.2), Inches(0.6),
                 font_size=18, bold=True, color=RED, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.3), Inches(3.6), W - Inches(0.6), Inches(2.9), WHITE,
         border_color=RED, border_pt=2)
add_rect(slide, Inches(0.3), Inches(3.6), Inches(0.1), Inches(2.9), RED)
add_text(slide, "🔀 Build Parallèle — Point fort du pipeline", Inches(0.6), Inches(3.65),
         Inches(12), Inches(0.45), font_size=14, bold=True, color=DARK, align=PP_ALIGN.LEFT)

par_items = [
    "Stage 3A (Python 3.11 LTS) et Stage 3B (Python 3.12) s'exécutent SIMULTANÉMENT",
    "Avantage : Le temps de build est divisé par 2 — Réduction de 50% du temps d'attente",
    "Python 3.11 : image de production principale — Python 3.12 : validation de compatibilité future",
    "Paramètre Docker : --build-arg PYTHON_VERSION permet de choisir la version dynamiquement",
]
bullet_block(slide, par_items, Inches(0.6), Inches(4.15), W - Inches(1.0), Inches(2.2),
             item_color=DARK, marker_color=RED, font_size=12)

footer_bar(slide, 7)

# ════════════════════════════════════════════════════════════
#  SLIDE 8 - PIPELINE PR
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Pipeline Pull Request — Jenkinsfile-PR", "Contrôle qualité automatique avant fusion")

add_rect(slide, Inches(0.4), Inches(1.4), Inches(5.8), Inches(5.1), WHITE,
         border_color=BLUE, border_pt=2)
add_text(slide, "Flux de validation PR", Inches(0.5), Inches(1.5), Inches(5.6), Inches(0.4),
         font_size=13, bold=True, color=DARK, align=PP_ALIGN.CENTER)

flow_items = [
    ("→", "Développeur crée une PR vers 'dev'", BLUE),
    ("→", "Jenkins détecte via webhook GitHub", DARK),
    ("→", "Vérifie : cible = 'dev' ? (sinon BLOQUÉ)", RED),
    ("→", "Build Docker de la branche PR", DARK),
    ("→", "Smoke test HTTP 200 (15 tentatives)", RGBColor(0xE0, 0x7B, 0x22)),
    ("✅", "PASSED → Fusion autorisée dans dev", GREEN),
    ("❌", "FAILED → Fusion interdite, PR rejetée", RED),
]

for i, (ico, txt, col) in enumerate(flow_items):
    y_i = Inches(2.0) + i * Inches(0.6)
    add_rect(slide, Inches(0.6), y_i, Inches(0.5), Inches(0.45), col)
    add_text(slide, ico, Inches(0.6), y_i, Inches(0.5), Inches(0.45),
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, txt, Inches(1.25), y_i, Inches(4.8), Inches(0.45),
             font_size=12, color=DARK, align=PP_ALIGN.LEFT)

add_rect(slide, Inches(6.5), Inches(1.4), Inches(6.5), Inches(5.1), WHITE,
         border_color=DARK, border_pt=1)
add_rect(slide, Inches(6.5), Inches(1.4), Inches(6.5), Inches(0.5), DARK)
add_text(slide, "🔒 Règles de Sécurité Git", Inches(6.5), Inches(1.4), Inches(6.5), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

rules = [
    "Toute PR doit cibler 'dev' — jamais 'main' directement",
    "Aucun code non testé ne peut entrer dans dev",
    "Jenkins est le seul juge — décision automatique",
    "Builds concurrents désactivés (disableConcurrentBuilds)",
    "Timeout 30 min : pipeline tué si bloqué",
    "Nettoyage automatique : conteneur + image supprimés",
    "Historique : 10 derniers builds conservés dans Jenkins",
]
bullet_block(slide, rules, Inches(6.65), Inches(2.0), Inches(6.1), Inches(4.3),
             item_color=DARK, marker_color=RED, font_size=11, marker="✓")

footer_bar(slide, 8)

# ════════════════════════════════════════════════════════════
#  SLIDE 9 - PIPELINE TAG / RELEASE
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Pipeline Tag/Release — Jenkinsfile-Tag", "Certification officielle des versions de production")

releases = ["v1.0.0", "v1.1.0", "v1.2.0", "v1.3.0", "v1.4.0", "v1.5.0", "v1.6.0"]
colors_r = [RGBColor(0x2D, 0x3D, 0x55), BLUE, RED,
            RGBColor(0xE0, 0x7B, 0x22), RGBColor(0x9B, 0x59, 0xB6), GREEN,
            RGBColor(0xE0, 0x1E, 0x22)]
descriptions = [
    "Version initiale\nMVP fonctionnel",
    "Produits ajoutés\nCatégories",
    "Images produits\nUI améliorée",
    "Scroll optimisé\nPerformance",
    "Tests complets\nSécurité",
    "Build parallèle\nPy3.11+3.12",
    "Release finale\nSoutenance",
]

tag_w = Inches(1.65)
tag_h = Inches(1.0)
for i, (ver, col, desc) in enumerate(zip(releases, colors_r, descriptions)):
    x = Inches(0.3) + i * (tag_w + Inches(0.08))
    add_rect(slide, x, Inches(1.5), tag_w, tag_h, col)
    add_text(slide, ver, x, Inches(1.5), tag_w, Inches(0.45),
             font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, desc, x, Inches(1.95), tag_w, Inches(0.55),
             font_size=9, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.3), Inches(2.6), W - Inches(0.6), Inches(0.08), GRAY)
add_text(slide, "→", W - Inches(0.9), Inches(2.45), Inches(0.6), Inches(0.4),
         font_size=18, bold=True, color=RED, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.3), Inches(2.9), Inches(5.9), Inches(3.5), WHITE,
         border_color=GREEN, border_pt=2)
add_rect(slide, Inches(0.3), Inches(2.9), Inches(5.9), Inches(0.5), GREEN)
add_text(slide, "⚙️ Spécifications Techniques", Inches(0.3), Inches(2.9), Inches(5.9), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tech_items = [
    "Validation SemVer : regex ^v\\d+\\.\\d+\\.\\d+$ obligatoire",
    "Build parallèle : Python 3.11 (prod) + Python 3.12 (compat)",
    "Tags Docker : biwex-store:v1.6.0-py311 + alias :latest",
    "Labels Docker : version, build, role (traçabilité complète)",
    "Smoke test : 20 tentatives / 2 secondes (tolérance maximale)",
    "Conservation : images de release JAMAIS supprimées",
]
bullet_block(slide, tech_items, Inches(0.5), Inches(3.5), Inches(5.5), Inches(2.7),
             item_color=DARK, marker_color=GREEN, font_size=11)

add_rect(slide, Inches(6.5), Inches(2.9), Inches(6.5), Inches(3.5), WHITE,
         border_color=DARK, border_pt=1)
add_rect(slide, Inches(6.5), Inches(2.9), Inches(6.5), Inches(0.5), DARK)
add_text(slide, "📋 Manifeste Officiel de Release", Inches(6.5), Inches(2.9), Inches(6.5), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
manifest_items = [
    "Version publiée & date de release",
    "N° Build Jenkins & commit Git hash",
    "Images Docker homologuées listées",
    "Résultat du smoke test d'homologation",
    "Statut : CONFORME POUR PRODUCTION",
    "Artefacts scellés (fingerprint MD5)",
]
bullet_block(slide, manifest_items, Inches(6.65), Inches(3.5), Inches(6.1), Inches(2.7),
             item_color=DARK, marker_color=DARK, font_size=11, marker="📌")

footer_bar(slide, 9)

# ════════════════════════════════════════════════════════════
#  SLIDE 10 (NOUVEAU) - PIPELINE NIGHTLY DEVSECOPS
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Pipeline Nightly DevSecOps — Jenkinsfile-Nightly-Security", "Audit automatique de sécurité, qualité et santé (Planification Cron)")

# Colonne gauche : Étapes d'audit
add_rect(slide, Inches(0.3), Inches(1.4), Inches(6.2), Inches(5.5), WHITE,
         border_color=PURPLE, border_pt=2)
add_rect(slide, Inches(0.3), Inches(1.4), Inches(6.2), Inches(0.5), PURPLE)
add_text(slide, "🛡️ Les 4 Piliers de l'Audit DevSecOps", Inches(0.3), Inches(1.4), Inches(6.2), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

audit_pillars = [
    ("1. Analyse Statique AST", "Contrôle de la syntaxe et des structures Python sur 9 fichiers sans dépendre de l'environnement hôte.", BLUE),
    ("2. Scan requirements.txt", "Vérifie l'épinglage des dépendances pour garantir des builds strictement reproductibles.", GREEN),
    ("3. Conformité Dockerfile", "Valide le Multi-Stage build, l'utilisateur non-root appuser et l'absence de cache résiduel.", RED),
    ("4. Intégrité Base SQLite", "Mesure le temps d'accès direct et certifie le catalogue de 38 produits et 7 catégories.", PURPLE),
]

for i, (title, desc, col) in enumerate(audit_pillars):
    y_p = Inches(2.05) + i * Inches(1.15)
    add_rect(slide, Inches(0.5), y_p, Inches(5.8), Inches(1.05), RGBColor(0xF8, 0xFA, 0xFC),
             border_color=col, border_pt=1)
    add_rect(slide, Inches(0.5), y_p, Inches(0.1), Inches(1.05), col)
    add_text(slide, title, Inches(0.7), y_p + Inches(0.08), Inches(5.4), Inches(0.35),
             font_size=12, bold=True, color=DARK, align=PP_ALIGN.LEFT)
    add_text(slide, desc, Inches(0.7), y_p + Inches(0.42), Inches(5.4), Inches(0.58),
             font_size=10, color=GRAY, align=PP_ALIGN.LEFT)

# Colonne droite : Déclencheur & Rapport
add_rect(slide, Inches(6.8), Inches(1.4), Inches(6.2), Inches(5.5), WHITE,
         border_color=DARK, border_pt=1)
add_rect(slide, Inches(6.8), Inches(1.4), Inches(6.2), Inches(0.5), DARK)
add_text(slide, "⚙️ Automatisation & Livrables Sécurité", Inches(6.8), Inches(1.4), Inches(6.2), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

sec_details = [
    "Planification Cron : H 2 * * * (Exécution nocturne quotidienne à 2h00)",
    "Non-bloquant pour les développeurs la journée",
    "Script dédié : scripts/security_audit.py (100% autonome)",
    "Benchmark de performance intégré dans le conteneur",
    "Génération du certificat : security-audit-report.txt",
    "Archivage sécurisé avec empreinte numérique MD5",
    "Valeur ajoutée : Passage du DevOps classique au DevSecOps moderne",
]
bullet_block(slide, sec_details, Inches(7.0), Inches(2.1), Inches(5.8), Inches(4.5),
             item_color=DARK, marker_color=PURPLE, font_size=11, marker="🔒")

footer_bar(slide, 10)

# ════════════════════════════════════════════════════════════
#  SLIDE 11 - TESTS AUTOMATISÉS
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Tests Automatisés", "Stratégie de qualité à 4 niveaux")

test_suites = [
    {
        "name": "test_structure.py",
        "type": "Tests Structurels",
        "nb": "3 tests",
        "color": BLUE,
        "tests": [
            "test_app_importable — Flask s'importe sans erreur",
            "test_database_tables — Tables products, users OK",
            "test_routes_exist — Routes /, /products, /login OK",
        ],
    },
    {
        "name": "test_business_logic.py",
        "type": "Tests Métier",
        "nb": "7 tests",
        "color": RED,
        "tests": [
            "test_product_has_name — Produit avec nom",
            "test_product_has_price — Produit avec prix > 0",
            "test_product_has_category — Catégorie assignée",
            "test_cart_add_item — Ajout panier fonctionnel",
            "test_user_registration — Inscription utilisateur",
            "test_user_login — Authentification OK",
            "test_order_total — Calcul total commande",
        ],
    },
    {
        "name": "smoke_test.py",
        "type": "Smoke Test HTTP",
        "nb": "Test live",
        "color": RGBColor(0xE0, 0x7B, 0x22),
        "tests": [
            "Envoie une requête HTTP GET / dans le conteneur",
            "Vérifie la réponse HTTP 200 OK",
            "Exécuté après chaque build Docker",
            "15 à 20 tentatives avec 2s de délai",
        ],
    },
    {
        "name": "benchmark.py",
        "type": "Tests Performance",
        "nb": "Benchmark",
        "color": GREEN,
        "tests": [
            "Mesure le temps de réponse moyen",
            "Teste la charge sur /products et /",
            "Génère un rapport de performance",
            "Détecte les régressions de vitesse",
        ],
    },
]

for i, suite in enumerate(test_suites):
    x = Inches(0.3) + i * Inches(3.25)
    add_rect(slide, x, Inches(1.4), Inches(3.1), Inches(0.55), suite["color"])
    add_text(slide, suite["name"], x, Inches(1.4), Inches(3.1), Inches(0.3),
             font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, f"{suite['type']} | {suite['nb']}", x, Inches(1.7), Inches(3.1), Inches(0.25),
             font_size=9, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, x, Inches(1.95), Inches(3.1), Inches(4.55), WHITE,
             border_color=suite["color"], border_pt=1)
    for j, test in enumerate(suite["tests"]):
        ty = Inches(2.05) + j * Inches(0.58)
        add_rect(slide, x + Inches(0.1), ty + Inches(0.15), Inches(0.08), Inches(0.3), suite["color"])
        add_text(slide, test, x + Inches(0.28), ty, Inches(2.75), Inches(0.58),
                 font_size=10, color=DARK, align=PP_ALIGN.LEFT)

add_rect(slide, Inches(3.5), Inches(6.6), Inches(6.3), Inches(0.6), GREEN)
add_text(slide, "✅  RÉSULTAT GLOBAL : 10 tests — 100% PASSÉS — Zéro régression détectée",
         Inches(3.5), Inches(6.6), Inches(6.3), Inches(0.6),
         font_size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

footer_bar(slide, 11)

# ════════════════════════════════════════════════════════════
#  SLIDE 12 - DOCKER & CONTENEURISATION
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Docker & Conteneurisation", "Multi-stage build — Image légère et sécurisée")

add_rect(slide, Inches(0.3), Inches(1.4), Inches(5.9), Inches(5.5), WHITE,
         border_color=RGBColor(0x09, 0x69, 0xDA), border_pt=2)
add_rect(slide, Inches(0.3), Inches(1.4), Inches(5.9), Inches(0.5),
         RGBColor(0x09, 0x69, 0xDA))
add_text(slide, "🐳 Multi-Stage Dockerfile", Inches(0.3), Inches(1.4), Inches(5.9), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.5), Inches(2.0), Inches(5.5), Inches(1.4), RGBColor(0xEB, 0xF5, 0xFF))
add_rect(slide, Inches(0.5), Inches(2.0), Inches(0.08), Inches(1.4), BLUE)
add_text(slide, "ÉTAPE 1 — BUILDER (Cuisine temporaire)",
         Inches(0.65), Inches(2.0), Inches(5.2), Inches(0.35),
         font_size=11, bold=True, color=DARK, align=PP_ALIGN.LEFT)
stage1_items = [
    "FROM python:3.11-slim AS builder",
    "python -m venv /opt/venv",
    "pip install -r requirements.txt (dans le venv)",
]
bullet_block(slide, stage1_items, Inches(0.65), Inches(2.35), Inches(5.1), Inches(1.0),
             item_color=DARK, marker_color=BLUE, font_size=10, marker="$")

add_text(slide, "↓  COPY --from=builder /opt/venv  ↓", Inches(0.3), Inches(3.42),
         Inches(5.9), Inches(0.3), font_size=10, italic=True, bold=True,
         color=RGBColor(0x09, 0x69, 0xDA), align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.5), Inches(3.75), Inches(5.5), Inches(1.5), RGBColor(0xE8, 0xF8, 0xEE))
add_rect(slide, Inches(0.5), Inches(3.75), Inches(0.08), Inches(1.5), GREEN)
add_text(slide, "ÉTAPE 2 — IMAGE FINALE (Propre et légère)",
         Inches(0.65), Inches(3.75), Inches(5.2), Inches(0.35),
         font_size=11, bold=True, color=DARK, align=PP_ALIGN.LEFT)
stage2_items = [
    "FROM python:3.11-slim (image finale propre)",
    "USER appuser (sécurité : non-root)",
    "gunicorn --bind 0.0.0.0:5000 app:app",
]
bullet_block(slide, stage2_items, Inches(0.65), Inches(4.1), Inches(5.1), Inches(1.0),
             item_color=DARK, marker_color=GREEN, font_size=10, marker="$")

add_rect(slide, Inches(0.5), Inches(5.35), Inches(5.5), Inches(0.9), DARK)
add_text(slide, "📦 Image finale : ~180 Mo  vs  800 Mo sans multi-stage\n= 78% plus légère !",
         Inches(0.5), Inches(5.35), Inches(5.5), Inches(0.9),
         font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(6.5), Inches(1.4), Inches(6.5), Inches(5.5), WHITE,
         border_color=DARK, border_pt=1)
add_rect(slide, Inches(6.5), Inches(1.4), Inches(6.5), Inches(0.5), DARK)
add_text(slide, "🔒 Bonnes Pratiques de Sécurité", Inches(6.5), Inches(1.4), Inches(6.5), Inches(0.5),
         font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

security_items = [
    "USER appuser — jamais root en production",
    "PYTHONDONTWRITEBYTECODE=1 — pas de .pyc",
    "PYTHONUNBUFFERED=1 — logs en temps réel",
    "EXPOSE 5000 — port déclaré explicitement",
    "--no-cache-dir — pas de cache pip inutile",
    "ARG PYTHON_VERSION — build paramétrable",
    "Labels Docker : version + build + role",
    "Conteneur isolé avec venv propre",
]
bullet_block(slide, security_items, Inches(6.65), Inches(2.0), Inches(6.1), Inches(4.7),
             item_color=DARK, marker_color=RED, font_size=11, marker="✓")

footer_bar(slide, 12)

# ════════════════════════════════════════════════════════════
#  SLIDE 13 - CONTRIBUTIONS
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Répartition des Contributions", "Travail collaboratif — Rôles et responsabilités")

add_rect(slide, Inches(0.4), Inches(1.4), Inches(5.9), Inches(5.5), WHITE,
         border_color=RED, border_pt=3)
add_rect(slide, Inches(0.4), Inches(1.4), Inches(5.9), Inches(0.65), RED)
add_text(slide, "👨‍💻 Famory TOURÉ — Lead Developer",
         Inches(0.4), Inches(1.4), Inches(5.9), Inches(0.65),
         font_size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(0.6), Inches(2.15), Inches(5.5), Inches(0.4), RGBColor(0xF0, 0xF4, 0xF8))
add_rect(slide, Inches(0.6), Inches(2.15), Inches(5.0), Inches(0.4), RED)
add_text(slide, "91% des commits — 70+ contributions",
         Inches(0.6), Inches(2.15), Inches(5.5), Inches(0.4),
         font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

famory_items = [
    "Architecture complète Flask + SQLAlchemy",
    "4 Jenkinsfiles complets (CI/CD + DevSecOps)",
    "Dockerfile multi-stage sécurisé",
    "Suite de tests & audits DevSecOps",
    "Scripts smoke_test.py, security_audit.py",
    "38 produits avec données complètes",
    "GitFlow et branching strategy",
    "Tags v1.0.0 → v1.6.0 (6 releases)",
    "Documentation technique & soutenance",
]
bullet_block(slide, famory_items, Inches(0.6), Inches(2.65), Inches(5.5), Inches(3.9),
             item_color=DARK, marker_color=RED, font_size=11)

add_rect(slide, Inches(6.7), Inches(1.4), Inches(6.3), Inches(5.5), WHITE,
         border_color=GRAY, border_pt=2)
add_rect(slide, Inches(6.7), Inches(1.4), Inches(6.3), Inches(0.65), GRAY)
add_text(slide, "👤 Abdoul TRAORÉ — Contributeur",
         Inches(6.7), Inches(1.4), Inches(6.3), Inches(0.65),
         font_size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(slide, Inches(6.9), Inches(2.15), Inches(5.9), Inches(0.4), RGBColor(0xF0, 0xF4, 0xF8))
add_rect(slide, Inches(6.9), Inches(2.15), Inches(0.59), Inches(0.4), GRAY)
add_text(slide, "9% des commits — 6 contributions",
         Inches(6.9), Inches(2.15), Inches(5.9), Inches(0.4),
         font_size=11, bold=True, color=DARK, align=PP_ALIGN.CENTER)

abdoul_items = [
    "Branche feature/abdoul-traore",
    "Ajout de produits au catalogue",
    "Tests de l'interface utilisateur",
    "Revue et validation de code (PR)",
    "Support lors des démos",
    "Participation aux réunions de projet",
]
bullet_block(slide, abdoul_items, Inches(6.9), Inches(2.65), Inches(5.9), Inches(3.9),
             item_color=DARK, marker_color=GRAY, font_size=11)

footer_bar(slide, 13)

# ════════════════════════════════════════════════════════════
#  SLIDE 14 - MÉTRIQUES & RÉSULTATS
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Métriques & Résultats", "Chiffres clés du projet DevOps & DevSecOps")

kpis = [
    ("6", "Versions\nlivrées", RED, "v1.0.0 → v1.6.0"),
    ("4", "Pipelines\nJenkins", DARK, "Dev + PR + Tag + Nightly"),
    ("10", "Tests\nautomatisés", GREEN, "100% passés ✅"),
    ("70+", "Commits\nGit", BLUE, "Famory TOURÉ lead"),
    ("38", "Produits\ncatalogués", RGBColor(0xE0, 0x7B, 0x22), "7 catégories high-tech"),
    ("100%", "Pipelines\nfonctionnels", PURPLE, "DevSecOps conforme"),
]

for i, (val, label, col, sub) in enumerate(kpis):
    row = i // 3
    col_i = i % 3
    x = Inches(0.4) + col_i * Inches(4.3)
    y = Inches(1.5) + row * Inches(2.3)
    add_rect(slide, x, y, Inches(4.0), Inches(2.0), WHITE,
             border_color=col, border_pt=3)
    add_rect(slide, x, y, Inches(0.12), Inches(2.0), col)
    add_text(slide, val, x + Inches(0.2), y + Inches(0.1), Inches(3.7), Inches(0.9),
             font_size=42, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_text(slide, label, x + Inches(0.2), y + Inches(1.0), Inches(3.7), Inches(0.5),
             font_size=13, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    add_text(slide, sub, x + Inches(0.2), y + Inches(1.5), Inches(3.7), Inches(0.4),
             font_size=10, italic=True, color=GRAY, align=PP_ALIGN.CENTER)

footer_bar(slide, 14)

# ════════════════════════════════════════════════════════════
#  SLIDE 15 - DÉMONSTRATION LIVE
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, LIGHT)
header_bar(slide, "Démonstration Live", "Pipeline CI/CD en action — http://localhost:5000")

add_rect(slide, Inches(0.4), Inches(1.4), W - Inches(0.8), Inches(5.5), WHITE,
         border_color=RED, border_pt=2)

add_text(slide, "🎯 Scénario de démonstration", Inches(0.6), Inches(1.5), Inches(12), Inches(0.5),
         font_size=16, bold=True, color=DARK, align=PP_ALIGN.LEFT)

demo_steps = [
    ("Étape 1", "Accéder au site Biwex Store sur http://localhost:5000", GREEN),
    ("Étape 2", "Montrer Jenkins UI : 4 pipelines configurés (Dev, PR, Tag, Nightly)", BLUE),
    ("Étape 3", "Montrer l'historique des builds et tags : v1.0.0 → v1.6.0", RGBColor(0xE0, 0x7B, 0x22)),
    ("Étape 4", "Montrer le build parallèle (Python 3.11 et Python 3.12)", RED),
    ("Étape 5", "Montrer les artefacts de release et d'audit : security-audit-report.txt", PURPLE),
    ("Étape 6", "Montrer GitHub : branches protégées, commits, tags, PRs", DARK),
    ("Étape 7", "Montrer Docker : multi-stage build et utilisateur appuser non-root", RGBColor(0x09, 0x69, 0xDA)),
]

for i, (step, desc, col) in enumerate(demo_steps):
    y_i = Inches(2.1) + i * Inches(0.6)
    add_rect(slide, Inches(0.6), y_i, Inches(1.2), Inches(0.45), col)
    add_text(slide, step, Inches(0.6), y_i, Inches(1.2), Inches(0.45),
             font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, desc, Inches(2.0), y_i, Inches(10.8), Inches(0.45),
             font_size=12, color=DARK, align=PP_ALIGN.LEFT)

footer_bar(slide, 15)

# ════════════════════════════════════════════════════════════
#  SLIDE 16 - CONCLUSION
# ════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, W, H, DARK)

add_rect(slide, 0, Inches(1.8), W, Inches(3.4), RED)
add_rect(slide, 0, Inches(1.8), W, Inches(0.06), WHITE)
add_rect(slide, 0, Inches(5.14), W, Inches(0.06), WHITE)

add_text(slide, "Conclusion", Inches(0.5), Inches(1.95), W - Inches(1), Inches(0.9),
         font_size=42, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

compétences = [
    "CI/CD & DevSecOps avec Jenkins — 4 pipelines automatisés",
    "Containerisation Docker — Multi-stage, non-root (appuser), Gunicorn",
    "GitFlow — Branches, Pull Requests contrôlées, Tags SemVer",
    "Tests & Qualité Continue — Structure, Métier, Smoke, Benchmark, Audit AST",
]
for i, skill in enumerate(compétences):
    add_text(slide, f"✅  {skill}", Inches(1.0), Inches(2.95) + i * Inches(0.52),
             W - Inches(2), Inches(0.5),
             font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_text(slide, "Merci pour votre attention !",
         Inches(0.5), Inches(5.4), W - Inches(1), Inches(0.6),
         font_size=22, bold=True, color=RGBColor(0xFF, 0xE0, 0xE0), align=PP_ALIGN.CENTER)

add_text(slide, "Famory TOURÉ & Abdoul TRAORÉ — 3LIG DevOps — ISG Sousse 2026/2027",
         Inches(0.5), Inches(6.0), W - Inches(1), Inches(0.4),
         font_size=12, color=GRAY, align=PP_ALIGN.CENTER)

add_text(slide, "Questions ?",
         Inches(0.5), Inches(6.5), W - Inches(1), Inches(0.6),
         font_size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

footer_bar(slide, 16)

# ── Sauvegarde ─────────────────────────────────────────────
out_dir = r"c:\Users\Famory Toure\biwex-store\docs"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "Presentation_Pipeline_CICD_Biwex.pptx")
prs.save(out_path)
print(f"[OK] Présentation mise à jour : {out_path}")
print(f"[INFO] Taille : {os.path.getsize(out_path) / 1024:.1f} Ko — {len(prs.slides)} diapositives")
