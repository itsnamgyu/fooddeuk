from abc import abstractmethod

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.decorators import classproperty
from django.utils.text import camel_case_to_spaces
from model_utils.managers import InheritanceManager
from versatileimagefield.fields import PPOIField, VersatileImageField
from django.contrib.staticfiles.templatetags.staticfiles import static

from .fields import SummernoteField


class Menu(models.Model):
    title = models.CharField(max_length=256, db_index=True)
    url_slug = models.SlugField(max_length=32, db_index=True)
    disabled = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self", related_name="children", on_delete=models.CASCADE, null=True, blank=True
    )
    # User will be redirected if redirect link is set
    redirect_to = models.URLField(null=True, blank=True)

    class Meta:
        order_with_respect_to = "parent"
        indexes = [models.Index(fields=["parent", "url_slug"])]
        constraints = [
            models.UniqueConstraint(
                fields=["url_slug"],
                condition=Q(parent__isnull=True),
                name="unique_parent_url_slug",
            ),
            models.UniqueConstraint(
                fields=["parent", "url_slug"], name="unique_child_url_slug"
            ),
        ]

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        # Validate the partial UniqueConstrain (unique_parent_url_slug)
        # manually
        if self.parent is None and self.url_slug is not None:
            if (
                Menu.objects.filter(parent=None, url_slug=self.url_slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError("A menu with the same url already exists")

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ("parent", "url_slug"):
            return "A submenu with the same url already exists"
        else:
            return super().unique_error_message(model_class, unique_check)

    def get_content_section(self):
        ContentSection = apps.get_model("dt_content", "ContentSection")
        content_section, created = ContentSection.objects.get_or_create(menu=self)
        return content_section

    def save(self, *args, **kwargs):
        if self.parent and self.children.exists():
            raise RuntimeError(
                "Multi-level submenus are not supported (only menu and sub-menu)"
            )
        super().save(*args, **kwargs)

    @property
    def update_url(self):
        if self.parent:
            return reverse("dt-content:submenu-update", args=[self.id])
        else:
            return reverse("dt-content:menu-update", args=[self.id])

    @property
    def console_list_url(self):
        if self.parent:
            return reverse("dt-content:menu-update", args=[self.parent.id])
        else:
            return reverse("dt-content:menu-list")

    @property
    def url_path(self):
        if self.parent:  # is child
            return "{}/{}".format(self.parent.url_slug, self.url_slug)
        else:  # is parent
            return "{}".format(self.url_slug)

    def __str__(self):
        if self.parent:
            return "{} > {}".format(self.parent.title, self.title)
        else:
            return self.title


class StaticContentSectionManager(InheritanceManager):
    def get_queryset(self):
        return self._queryset_class(self.model).filter(menu=None)


class ContentSection(models.Model):
    # Key for static content sections (standlone content sections used in custom HTML)
    key = models.CharField(max_length=256, db_index=True)
    # Location of static ContentSection (if it is static)
    # Saves the url where the ContentSection was first initiated
    static_location = models.URLField(null=True)

    menu = models.OneToOneField(
        Menu,
        related_name="content_section",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    objects = models.Manager()
    static_objects = StaticContentSectionManager()

    def __str__(self):
        if self.menu:
            if self.menu.parent:
                return "{} > {}".format(self.menu.parent.title, self.menu.title)
            else:
                return "{}".format(self.menu.title)
        else:
            return "{}".format(self.key)

    @property
    def blocks(self):
        ContentBlock = apps.get_model("dt_content", "ContentBlock")
        return ContentBlock.objects.select_subclasses().filter(section=self)

    @property
    def empty(self):
        return not self.blocks.exists()

    @property
    def template_name(self):
        return "dt_content/content/content_section.html"


class StaticContentBlockManager(InheritanceManager):
    def get_queryset(self):
        return self._queryset_class(self.model).filter(section=None)


class ContentBlock(models.Model):
    section = models.ForeignKey(
        ContentSection,
        related_name="_blocks",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Whether this block is disabled within a ContentSection
    disabled = models.BooleanField(default=False)

    # Key for static content blocks (standlone content blocks used in custom HTML)
    key = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    # Location of static ContentSection (if it is static)
    # Saves the url where the ContentSection was first initiated
    static_location = models.URLField(null=True)

    objects = InheritanceManager()
    static_objects = StaticContentBlockManager()

    class Meta:
        order_with_respect_to = "section"

    @classproperty
    def block_type(cls):
        return camel_case_to_spaces(cls.__name__).title()

    def get_block_type(self):
        return self.__class__.block_type

    @classproperty
    def block_type_key(cls):
        return camel_case_to_spaces(cls.__name__).replace(" ", "_")

    @property
    def console_list_url(self):
        if self.section:
            menu = self.section.menu
            if menu:
                # menu-bound section
                menu.update_url
            else:
                # static section
                return reverse(
                    "dt-content:content-section-update", args=[self.section.id]
                )
        else:
            # static block
            return reverse("dt-content:content-block-list")

    @property
    def template_name(self):
        return "dt_content/content/content_block.html"

    @property
    @abstractmethod
    def child_template_name(self):
        if type(self) is ContentBlock:
            raise RuntimeError(
                "The child_template_name property can only be retrieved from a subclass of ContentBlock. Consider looking into multi-table inheritance for Django models."
            )
        else:
            raise NotImplementedError(
                "The child_template_name property has not been set for {}".format(
                    type(self).__name__
                )
            )

    @classproperty
    @abstractmethod
    def create_url(cls):
        if cls is ContentBlock:
            raise RuntimeError(
                "The create_url property can only be retrieved from a subclass of ContentBlock. Consider looking into multi-table inheritance for Django models."
            )
        else:
            raise NotImplementedError(
                "The create_url property has not been set for {}".format(cls.__name__)
            )

    @property
    @abstractmethod
    def update_url(self):
        if type(self) is ContentBlock:
            raise RuntimeError(
                "The update_url property can only be retrieved from a child model of ContentBlock. Consider looking into multi-table inheritance for Django models."
            )
        else:
            raise NotImplementedError(
                "The update_url property has not been set for {}".format(
                    type(self).__name__
                )
            )

    def __str__(self):
        if self.section:
            return "{} in {}".format(self.block_type, str(self.section))
        else:
            # static block
            return "Static {} ({})".format(self.block_type, self.key)


class RichTextBlock(ContentBlock):
    base = models.OneToOneField(
        ContentBlock, on_delete=models.CASCADE, parent_link=True
    )
    content = SummernoteField(default="", blank=True)

    @property
    def child_template_name(self):
        return "dt_content/content/rich_text_block.html"

    @classproperty
    def create_url(cls):
        return reverse("dt-content:rich-text-block-create")

    @property
    def update_url(self):
        return reverse("dt-content:rich-text-block-update", args=[self.id])


class CarouselBlock(ContentBlock):
    base = models.OneToOneField(
        ContentBlock, on_delete=models.CASCADE, parent_link=True
    )

    # NOT IMPLEMENTED

    @property
    def child_template_name(self):
        raise NotImplementedError()

    @classproperty
    def create_url(cls):
        return ""

    @property
    def update_url(self):
        raise NotImplementedError()


class Blurb(models.Model):
    # Identifiers are primarily for the template-embedded blurb use case,
    # using the `blurb` template tag.
    identifier = models.CharField(max_length=256, unique=True, null=True, blank=True)
    label = models.TextField(null=True, blank=True)
    # A null value indicates that the content has not been set.
    # An empty value would indicate that the blurb is intentionally empty.
    content = SummernoteField(null=True, blank=True)
    plain_text = models.BooleanField(null=False, default=False, editable=False)
    last_known_location = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["identifier"]),
            models.Index(fields=["last_known_location", "identifier"]),
        ]

    def empty(self):
        return self.content == ""

    @property
    def display_name(self):
        if self.label:
            return self.label
        if self.identifier:
            return self.identifier
        return "Unnamed Blurb ({})".format(self.id)

    @property
    def html_id(self):
        return "dt-content-blurb-{}".format(self.id)

    @property
    def href(self):
        if self.last_known_location:
            return "{}#{}".format(self.last_known_location, self.html_id)
        else:
            return ""

    @property
    def template_name(self):
        return "dt_content/content/blurb.html"

    def __str__(self):
        if self.last_known_location:
            return "{} ({})".format(self.display_name, self.last_known_location)
        return self.display_name


class ImageBlurb(models.Model):
    # Identifiers are primarily for the template-embedded use case,
    # using the `image_blurb` template tag.
    identifier = models.CharField(max_length=256, unique=True, null=True, blank=True)
    label = models.TextField(null=True, blank=True)
    # A null value indicates that the content has not been set.
    # An empty value would indicate that the blurb is intentionally empty.
    image = VersatileImageField(
        upload_to="image_blurbs", null=True, blank=True, default=None
    )
    placeholder = models.TextField(
        help_text="Path to static placeholder image file",
        null=True,
        blank=True,
        default=None,
    )
    last_known_location = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["identifier"]),
            models.Index(fields=["last_known_location", "identifier"]),
        ]

    @property
    def display_name(self):
        if self.label:
            return self.label
        if self.identifier:
            return self.identifier
        return "Unnamed Blurb ({})".format(self.id)

    @property
    def src(self):
        if self.image:
            return self.image.url
        if self.placeholder:
            return static(self.placeholder)
        return None

    @property
    def html_id(self):
        return "dt-content-image-blurb-{}".format(self.id)

    @property
    def update_url(self):
        return reverse("dt-content:image-blurb-update", args=(self.id,))

    @property
    def update_link_template_name(self):
        return "dt_content/content/image_blurb_update_link.html"

    @property
    def href(self):
        if self.last_known_location:
            return "{}#{}".format(self.last_known_location, self.html_id)
        else:
            return ""

    def __str__(self):
        if self.last_known_location:
            return "{} ({})".format(self.display_name, self.last_known_location)
        return self.display_name


def update_content_block_subclasses():
    """
    Call this after you have defined additional ContentBlock subclasses
    to include them in `content_block_subclasses`
    """
    global content_block_classes
    content_block_classes = dict()
    for klass in ContentBlock.__subclasses__():
        content_block_classes[klass.block_type_key] = klass


content_block_classes = None
update_content_block_subclasses()
