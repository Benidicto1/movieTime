from django.db import models


class Genre(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.CharField(
        max_length=10,
        unique=True,
    )

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.CharField(
        max_length=3,
        unique=True,
    )

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(
        max_length=255,
    )

    bio = models.TextField(
        blank=True,
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class Movie(models.Model):

    AGE_RATING_CHOICES = [
        ("G", "G"),
        ("PG", "PG"),
        ("PG13", "PG-13"),
        ("R", "R"),
        ("NC17", "NC-17"),
    ]

    title = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
    )

    description = models.TextField()

    genres = models.ManyToManyField(
        Genre,
        related_name="movies",
        blank=True,
    )

    categories = models.ManyToManyField(
        Category,
        related_name="movies",
        blank=True,
    )

    languages = models.ManyToManyField(
        Language,
        related_name="movies",
        blank=True,
    )

    countries = models.ManyToManyField(
        Country,
        related_name="movies",
        blank=True,
    )

    release_date = models.DateField(
        null=True,
        blank=True,
    )

    runtime_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    age_rating = models.CharField(
        max_length=10,
        choices=AGE_RATING_CHOICES,
        blank=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10000.00,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["release_date"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title


class MovieCast(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="cast",
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="acting_roles",
    )

    character_name = models.CharField(
        max_length=255,
        blank=True,
    )

    billing_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["billing_order"]

    def __str__(self):
        return f"{self.person.name} - {self.movie.title}"


class MovieCrew(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="crew",
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="crew_roles",
    )

    role = models.CharField(
        max_length=100,
    )

    class Meta:
        ordering = ["role", "person__name"]

    def __str__(self):
        return f"{self.person.name} - {self.role}"


class MovieMedia(models.Model):
    movie = models.OneToOneField(
        Movie,
        on_delete=models.CASCADE,
        related_name="media",
    )

    poster = models.ImageField(
        upload_to="movies/posters/",
        blank=True,
        null=True,
    )

    backdrop = models.ImageField(
        upload_to="movies/backdrops/",
        blank=True,
        null=True,
    )

    trailer_url = models.URLField(
        blank=True,
    )

    movie_storage_key = models.CharField(
        max_length=500,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Media for {self.movie.title}"


class MovieVideo(models.Model):

    STATUS_CHOICES = [
        ("UPLOADING", "Uploading"),
        ("PROCESSING", "Processing"),
        ("READY", "Ready"),
        ("FAILED", "Failed"),
    ]

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="videos",
    )

    resolution = models.CharField(
        max_length=20,
    )

    storage_key = models.CharField(
        max_length=500,
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    file_format = models.CharField(
        max_length=20,
        default="mp4",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="UPLOADING",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.movie.title} - {self.resolution}"


class Subtitle(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="subtitles",
    )

    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="subtitles",
    )

    storage_key = models.CharField(
        max_length=500,
    )

    format = models.CharField(
        max_length=20,
        default="vtt",
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.movie.title} - {self.language.code}"