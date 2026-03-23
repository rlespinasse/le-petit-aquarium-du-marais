# Comment ajouter un poisson

## Étape 1 : Préparer le dessin

1. L'enfant dessine un poisson sur une feuille de papier (crayons, feutres, peinture — tout est permis).
2. Un adulte prend le dessin en photo ou le scanne.

## Étape 2 : Nommer le fichier

Placer le fichier image dans le dossier `dessins/` en respectant la convention de nommage :

| Format du nom | Exemple | Résultat |
|---------------|---------|----------|
| `prenom.ext` | `emma.jpg` | « Poisson de Emma » |
| `prenom--nom-du-poisson.ext` | `abel--paillette.jpg` | « Paillette, poisson de Abel » |

Règles :
- Le prénom et le nom du poisson sont séparés par `--` (double tiret).
- Pour les prénoms composés, utiliser un simple `-` : `jean-luc.jpg` donnera « Jean-Luc ».
- Les formats acceptés sont : jpg, jpeg, png, svg, webp, bmp, tiff, heic.
- Le nom du fichier doit être en minuscules.

## Étape 3 : Générer et vérifier

```bash
# Convertir et synchroniser
just sync

# Vérifier le résultat en local
just serve
```

La commande `just sync` effectue trois actions :
1. Convertit l'image en `site/images/fish-{nom}.png` et `.webp` (redimensionnée à 800×800 max).
2. Met à jour les blocs `FISH:START` / `FISH:END` dans `site/index.html`.
3. Met à jour le cache du service worker dans `site/sw.js`.

## Étape 4 : Créer un commit et une pull request

```bash
git add dessins/ site/
git commit -m "feat: ajouter le poisson de Emma"
```

Pousser la branche et ouvrir une pull request. La CI vérifie automatiquement que le fichier `index.html` est synchronisé avec les images.

## Consentement

En soumettant un dessin, le responsable légal de l'enfant autorise sa publication sur le site. Un retrait peut être demandé à tout moment en contactant l'éditeur du site.
