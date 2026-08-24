from django.conf import settings


class StorageConfig:

    @staticmethod
    def bucket():
        return settings.MOVIETIME_STORAGE_BUCKET

    @staticmethod
    def cdn_domain():
        return settings.MOVIETIME_CDN_DOMAIN

    @staticmethod
    def signed_url_expiration():
        return settings.MOVIETIME_SIGNED_URL_EXPIRATION