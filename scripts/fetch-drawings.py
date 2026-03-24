#!/usr/bin/env python3
"""Télécharge les dessins approuvés depuis un stockage externe vers dessins/.

Deux backends supportés, configurés via la variable d'environnement DRAWING_STORAGE :

  DRAWING_STORAGE=nextcloud  (défaut)
    Télécharge depuis un dossier Nextcloud via WebDAV.
    Variables requises :
      NEXTCLOUD_URL       — URL WebDAV du dossier (ex: https://nuage.apps.education.fr/remote.php/dav/files/user/aquarium/approuves)
      NEXTCLOUD_USER      — identifiant Nextcloud
      NEXTCLOUD_PASSWORD  — mot de passe ou mot de passe d'application

  DRAWING_STORAGE=r2
    Télécharge depuis un bucket Cloudflare R2 (compatible S3).
    Variables requises :
      R2_ENDPOINT_URL     — URL du endpoint S3 (ex: https://<account_id>.r2.cloudflarestorage.com)
      R2_ACCESS_KEY_ID    — clé d'accès
      R2_SECRET_ACCESS_KEY — clé secrète
      R2_BUCKET           — nom du bucket
      R2_PREFIX            — préfixe des objets (défaut: approuves/)
"""

import os
import pathlib
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
DST_DIR = ROOT / "dessins"

EXTENSIONS = {".jpg", ".jpeg", ".png", ".svg", ".webp", ".bmp", ".tiff", ".tif", ".heic"}


# ---------------------------------------------------------------------------
# Backend : Nextcloud (WebDAV)
# ---------------------------------------------------------------------------

def fetch_nextcloud():
    """Télécharge les fichiers images depuis un dossier Nextcloud via WebDAV."""
    base_url = os.environ.get("NEXTCLOUD_URL", "").rstrip("/")
    user = os.environ.get("NEXTCLOUD_USER", "")
    password = os.environ.get("NEXTCLOUD_PASSWORD", "")

    if not all([base_url, user, password]):
        print("ERROR: NEXTCLOUD_URL, NEXTCLOUD_USER et NEXTCLOUD_PASSWORD sont requis.", file=sys.stderr)
        sys.exit(1)

    # Configurer l'authentification HTTP Basic
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, base_url, user, password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(auth_handler)

    # Lister le contenu du dossier via PROPFIND
    propfind_body = b'<?xml version="1.0" encoding="UTF-8"?><d:propfind xmlns:d="DAV:"><d:prop><d:displayname/><d:getcontenttype/></d:prop></d:propfind>'
    req = urllib.request.Request(base_url + "/", method="PROPFIND", data=propfind_body)
    req.add_header("Depth", "1")
    req.add_header("Content-Type", "application/xml")

    try:
        resp = opener.open(req)
    except urllib.error.HTTPError as e:
        print(f"ERROR: Impossible de lister le dossier Nextcloud: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Parser la réponse XML pour extraire les noms de fichiers
    xml_data = resp.read()
    root = ET.fromstring(xml_data)
    ns = {"d": "DAV:"}

    files = []
    for response in root.findall("d:response", ns):
        href = response.find("d:href", ns)
        if href is None:
            continue
        path = urllib.parse.unquote(href.text)
        filename = path.rstrip("/").split("/")[-1]
        suffix = pathlib.Path(filename).suffix.lower()
        if suffix in EXTENSIONS:
            files.append(filename)

    if not files:
        print("Aucun dessin trouvé dans le dossier Nextcloud.")
        return 0

    # Télécharger chaque fichier
    downloaded = 0
    for filename in files:
        dst = DST_DIR / filename
        if dst.exists():
            print(f"  skip {filename} (déjà présent)")
            continue

        file_url = base_url + "/" + urllib.parse.quote(filename)
        try:
            resp = opener.open(file_url)
            dst.write_bytes(resp.read())
            print(f"  download {filename}")
            downloaded += 1
        except urllib.error.HTTPError as e:
            print(f"  ERROR: {filename}: {e.code} {e.reason}", file=sys.stderr)

    return downloaded


# ---------------------------------------------------------------------------
# Backend : Cloudflare R2 (S3-compatible)
# ---------------------------------------------------------------------------

def fetch_r2():
    """Télécharge les fichiers images depuis un bucket Cloudflare R2 via l'API S3."""
    try:
        import boto3
    except ImportError:
        print("ERROR: boto3 est requis pour le backend R2.", file=sys.stderr)
        print("       Installer avec : pip install boto3", file=sys.stderr)
        sys.exit(1)

    endpoint_url = os.environ.get("R2_ENDPOINT_URL", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    bucket = os.environ.get("R2_BUCKET", "")
    prefix = os.environ.get("R2_PREFIX", "approuves/")

    if not all([endpoint_url, access_key, secret_key, bucket]):
        print("ERROR: R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY et R2_BUCKET sont requis.", file=sys.stderr)
        sys.exit(1)

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    # Lister les objets dans le préfixe
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    except Exception as e:
        print(f"ERROR: Impossible de lister le bucket R2: {e}", file=sys.stderr)
        sys.exit(1)

    contents = response.get("Contents", [])
    files = []
    for obj in contents:
        key = obj["Key"]
        filename = key.removeprefix(prefix)
        if not filename:
            continue
        suffix = pathlib.Path(filename).suffix.lower()
        if suffix in EXTENSIONS:
            files.append((key, filename))

    if not files:
        print("Aucun dessin trouvé dans le bucket R2.")
        return 0

    # Télécharger chaque fichier
    downloaded = 0
    for key, filename in files:
        dst = DST_DIR / filename
        if dst.exists():
            print(f"  skip {filename} (déjà présent)")
            continue

        try:
            s3.download_file(bucket, key, str(dst))
            print(f"  download {filename}")
            downloaded += 1
        except Exception as e:
            print(f"  ERROR: {filename}: {e}", file=sys.stderr)

    return downloaded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

BACKENDS = {
    "nextcloud": fetch_nextcloud,
    "r2": fetch_r2,
}


def main():
    backend_name = os.environ.get("DRAWING_STORAGE", "nextcloud").lower()

    if backend_name not in BACKENDS:
        print(f"ERROR: Backend inconnu '{backend_name}'. Valeurs possibles : {', '.join(BACKENDS)}", file=sys.stderr)
        sys.exit(1)

    print(f"Backend de stockage : {backend_name}")

    DST_DIR.mkdir(exist_ok=True)

    fetch = BACKENDS[backend_name]
    downloaded = fetch()

    # Lister les fichiers présents
    existing = sorted(
        f for f in DST_DIR.iterdir()
        if f.suffix.lower() in EXTENSIONS and not f.name.startswith(".")
    )

    print(f"\nDone — {downloaded} téléchargé(s), {len(existing)} dessin(s) au total dans dessins/.")


if __name__ == "__main__":
    main()
