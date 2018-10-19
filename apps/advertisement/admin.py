from django.contrib import admin

from .models import Advertisement, Comments, Complaints, Image

# set up the header
admin.site.site_header = 'Share Pin Application'


class AdvertisementImageInline(admin.TabularInline):
    model = Image
    # initially we offer a user to upload only one photo
    extra = 1
    # the maximum amount of photos
    max_num = 5


class AdvertisementAdmin(admin.ModelAdmin):
    """ Admin model of the Advertisement model
        Helping non-programmer users interacting with app
        Declare special filters and display orders
    """

    inlines = [AdvertisementImageInline, ]

    list_display = (
        '__str__',
        'created_date'
    )
    list_filter = (
        'created_date',
    )
    search_fields = (
        'title',
        'description',
        'user__username'
    )


class ComplaintsAdmin(admin.ModelAdmin):
    """ Admin model of the Complaints model
        Helping non-programmer users interacting with app
        Declare special filters and display orders
    """
    list_display = (
        'user',
        'advertisement',
        'text',
        'confirmed'
    )
    list_filter = (
        'confirmed',
        'advertisement'
    )
    search_fields = (
        'text',
        'user__username',
        'advertisement__title'
    )

    def save_model(self, request, obj, form, change):
        """ Override save_model to check if complaint was applied
            Afterwards save applier field to the model if True
        """
        if 'confirmed' in form.changed_data:
            obj.applier = request.user.username
        super().save_model(request, obj, form, change)


class CommentsAdmin(admin.ModelAdmin):
    """ Admin model of the Comments model
        Helping non-programmer users interacting with app
        Declare special filters and display orders
    """
    list_display = (
        'user',
        'advertisement',
        'created_date'
    )
    list_filter = (
        'advertisement',
    )
    search_fields = (
        'text',
        'user__username',
        'advertisement__title'
    )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """
    Admin model for Image
    """
    pass


# register models
admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Complaints, ComplaintsAdmin)
