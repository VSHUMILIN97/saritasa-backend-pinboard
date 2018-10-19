from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from taggit.managers import TaggableManager

from apps.users.models import AppUser


class Advertisement(models.Model):
    """Custom model for advertisements

    Attributes:
        user (AppUser): a user to which an ad belongs
        title (str): a title of an ad
        description (str): description for an ad
        photo (image): 1 photo for an ad
        address (str): address where to meet
        created_date (datetime): when an ad was added
        modified_date (datetime): the last time an ad was modified
        price (money): how much an ad's product costs
        tags(TaggableManager): M2M with Tag model from taggit lib

    Methods:
        get_absolute_url: The method that returns
        a unique link to an every advert instance

    """

    user = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('User')
    )
    title = models.CharField(
        max_length=100,
        verbose_name=_('Title')
    )
    description = models.TextField(
        max_length=3000,
        verbose_name=_('Description')
    )
    address = models.CharField(
        max_length=100,
        null=True,
        verbose_name=_('Address')
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Date of creation')
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Date of modification')
    )
    price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name=_('Price'),
        validators=[
            MinMoneyValidator(0)
        ]
    )
    favourite = models.ManyToManyField(AppUser, related_name='user_favourites')

    published = models.BooleanField(
        default=True,
        verbose_name=_('Published')
    )
    tags = TaggableManager(blank=True)

    def __str__(self):
        return f'{self.title} ({self.user})'

    def get_absolute_url(self):
        return reverse('info', args=[self.id])

    class Meta:
        verbose_name = _('Ad')
        verbose_name_plural = _('Ads')


class Image(models.Model):
    """Model for advert images"""

    advertisement = models.ForeignKey(
        Advertisement,
        related_name=_('images'),
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='backend/assets/image_ad',
        verbose_name=_('Photo')
    )


class Comments(models.Model):
    """Custom model for comments

    Attributes:
        advertisement (Advertisement): ads to which a comment belongs
        Related to the Advertisement model
        user (AppUser): a comment's author
        Related to the AppUser model
        created_date (datetime): when comment is added
        text (str): a comment's text

    """

    # Reaction on deleting Advertisement object is obviously
    # deleting the whole chain
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        verbose_name=_('Advertisement')
    )

    # Cannot be deleted via deleting User object
    user = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Date of creation')
    )
    text = models.TextField(
        max_length=300,
        verbose_name=_('Text')
    )

    def __str__(self):
        return f'{self.advertisement} ({self.created_date})'

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')


class Complaints(models.Model):
    """Custom model for complaints

    Attributes:
        advertisement (Advertisement): ads to which a complaint belongs.
        Related to the Advertisement model
        user (AppUser): a complaint's author
        Related to the AppUser model
        text (str): a complaint's text
        created_date (datetime): when complaint is added
        confirmed (bool): a flag that shows whether a complaint was confirmed
        by admins or not

    """

    # Reaction on deleting Advertisement object is obviously
    # deleting the whole chain
    user = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )

    # Cannot be deleted via deleting User object
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        verbose_name=_('Advertisement')
    )

    text = models.TextField(
        max_length=300,
        verbose_name=_('Text')
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Date of creation')
    )

    applier = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Applier')

    )

    confirmed = models.BooleanField(
        verbose_name=_('Is confirmed'),
        blank=True,
        null=True,
    )
    # TODO: there must be a field where user who confirm a complaint is stored

    def __str__(self):
        return f'{self.advertisement} ({self.created_date})'

    class Meta:
        verbose_name = _('Complaint')
        verbose_name_plural = _('Complaints')
