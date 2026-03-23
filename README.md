# Le petit aquarium du Marais

Un aquarium collaboratif en ligne, rempli de dessins de poissons faits par des enfants.

Chaque enfant dessine et colorie un poisson sur papier. Un adulte prend le dessin en photo, et le poisson rejoint l'aquarium animé sur le site.

## Prérequis

- [Python 3](https://www.python.org/)
- [ImageMagick](https://imagemagick.org/) — conversion des images (`brew install imagemagick` sur macOS)
- [just](https://github.com/casey/just) — exécuteur de recettes (`brew install just` sur macOS)
- [Node.js](https://nodejs.org/) — pour le mode développement et la minification (via `npx`)

## Démarrage rapide

```bash
# Cloner le dépôt
git clone https://github.com/rlespinasse/le-petit-aquarium-du-marais.git
cd le-petit-aquarium-du-marais

# Synchroniser les images et lancer le site en local
just sync
just serve
```

Le site est accessible sur `http://localhost:8000`.

Pour le mode développement avec rechargement automatique :

```bash
just dev
```

## Structure du projet

```
dessins/                 # Photos originales des dessins (source)
site/                    # Site statique (HTML, CSS, JS)
  images/                # Images converties (png + webp), générées par just convert
  index.html             # Page principale, mise à jour par just sync
  aquarium.js            # Animation de l'aquarium
  style.css              # Styles
  sw.js                  # Service worker (cache hors-ligne)
dist/                    # Build de production, généré par just build
scripts/
  convert-fish.py        # Conversion des dessins en png/webp
  sync-fish.py           # Synchronisation images → index.html + sw.js
```

## Commandes disponibles

| Commande | Description |
|----------|-------------|
| `just` | Liste toutes les commandes disponibles |
| `just convert` | Convertit les images de `dessins/` en png/webp dans `site/images/` |
| `just sync` | Convertit les images, génère les favicons, et met à jour `index.html` |
| `just serve` | Lance un serveur local sur le port 8000 |
| `just dev` | Synchronise puis lance un serveur avec rechargement automatique |
| `just build` | Génère le build de production dans `dist/` |
| `just serve-prod` | Lance le build de production en local |
| `just check` | Vérifie que `index.html` est synchronisé avec `site/images/` (utilisé en CI) |
| `just favicon` | Régénère les favicons à partir de `site/favicon.svg` |
| `just list` | Liste tous les poissons de l'aquarium |

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour savoir comment ajouter un poisson.
