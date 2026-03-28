# Comment ajouter un poisson

## Pour les parents et enseignants

1. L'enfant dessine un poisson sur une feuille de papier (crayons, feutres, peinture — tout est permis).
2. Un adulte prend le dessin en photo.
3. Soumettre la photo via le formulaire de soumission mis à disposition (lien sur le site, QR code, ou contact de l'administrateur).
4. L'administrateur valide le dessin et déclenche la mise à jour du site.

### Consentement

En soumettant un dessin, le responsable légal de l'enfant autorise sa publication sur le site. Un retrait peut être demandé à tout moment en contactant l'éditeur du site.

---

## Pour les développeurs

### Prérequis

- [Python 3](https://www.python.org/)
- [ImageMagick](https://imagemagick.org/)
- [just](https://github.com/casey/just)
- [Node.js](https://nodejs.org/) — pour le mode développement et la minification

### Stockage externe des dessins

Les dessins originaux ne sont **pas** stockés dans le dépôt Git. Ils sont hébergés sur un stockage externe et récupérés lors du build. Deux backends sont supportés :

#### Option A : Nextcloud (apps.education.fr) — recommandé pour l'Éducation nationale

Nextcloud est fourni gratuitement par l'Éducation nationale via [apps.education.fr](https://apps.education.fr) et hébergé en France par RENATER, conforme au RGPD.

Variables d'environnement requises :

```bash
export DRAWING_STORAGE=nextcloud
export NEXTCLOUD_URL="https://nuage.apps.education.fr/remote.php/dav/files/user/aquarium/approuves"
export NEXTCLOUD_USER="identifiant"
export NEXTCLOUD_PASSWORD="mot-de-passe-application"
```

**Configuration Nextcloud :**
1. Se connecter à [apps.education.fr](https://apps.education.fr) avec ses identifiants Éducation nationale.
2. Créer un dossier pour les dessins (ex: `aquarium/approuves/`).
3. Créer un mot de passe d'application dans les paramètres de sécurité Nextcloud.
4. Utiliser un formulaire Nextcloud ou recueillir les dessins par un autre moyen, puis déplacer les dessins approuvés dans le dossier `approuves/`.

#### Option B : Cloudflare R2 — alternative indépendante

Cloudflare R2 offre 10 Go de stockage gratuit, compatible S3. Adapté si le projet n'est pas directement rattaché à l'Éducation nationale.

Variables d'environnement requises :

```bash
export DRAWING_STORAGE=r2
export R2_ENDPOINT_URL="https://<account_id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="clé-accès"
export R2_SECRET_ACCESS_KEY="clé-secrète"
export R2_BUCKET="aquarium-dessins"
export R2_PREFIX="approuves/"  # optionnel, défaut: approuves/
```

**Dépendance supplémentaire** : `pip install boto3`

### Convention de nommage des fichiers

| Format du nom | Exemple | Résultat |
|---------------|---------|----------|
| `prenom.ext` | `emma.jpg` | « Poisson de Emma » |
| `prenom--nom-du-poisson.ext` | `abel--paillette.jpg` | « Paillette, poisson de Abel » |

Règles :
- Le prénom et le nom du poisson sont séparés par `--` (double tiret).
- Pour les prénoms composés, utiliser un simple `-` : `jean-luc.jpg` donnera « Jean-Luc ».
- Les formats acceptés sont : jpg, jpeg, png, svg, webp, bmp, tiff, heic.
- Le nom du fichier doit être en minuscules.

### Récupérer les dessins et construire en local

```bash
# Récupérer les dessins depuis le stockage externe
just fetch

# Convertir et synchroniser
just sync

# Vérifier le résultat en local
just serve
```

### Créer un commit et une pull request

```bash
git add site/
git commit -m "feat: ajouter le poisson de Emma"
```

Pousser la branche et ouvrir une pull request. La CI récupère les dessins depuis le stockage externe, puis vérifie que `index.html` est synchronisé.

### Déploiement

Le déploiement se fait automatiquement sur push vers `main`. Il peut aussi être déclenché manuellement depuis l'onglet **Actions** de GitHub (bouton « Run workflow ») après l'approbation de nouveaux dessins.

### Configuration GitHub

Les secrets et variables suivants doivent être configurés dans les paramètres du dépôt GitHub :

**Variable de dépôt** (Settings → Variables → Actions) :
- `DRAWING_STORAGE` : `nextcloud` ou `r2`

**Secrets de dépôt** (Settings → Secrets → Actions) :

Pour Nextcloud :
- `NEXTCLOUD_URL`
- `NEXTCLOUD_USER`
- `NEXTCLOUD_PASSWORD`

Pour Cloudflare R2 :
- `R2_ENDPOINT_URL`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET`

**Variable optionnelle** :
- `R2_PREFIX` : préfixe des objets dans le bucket (défaut : `approuves/`)
