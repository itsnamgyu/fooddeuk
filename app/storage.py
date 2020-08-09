from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class LooseManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
