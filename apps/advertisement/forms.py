from django import forms

from taggit.models import Tag

from .models import Advertisement, Comments, Complaints, Image


class AdvertisementForm(forms.ModelForm):
    """The form for the Advertisement model"""

    def __init__(self, *args, **kwargs):
        """ Override __init__ so tags became not required in Form """
        super(AdvertisementForm, self).__init__(*args, **kwargs)
        self.fields['tags'].required = False

    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        queryset=Tag.objects
    )

    class Meta:
        model = Advertisement
        fields = (
            'title',
            'description',
            'address',
            'price',
            'tags'
        )


class CommentsForm(forms.ModelForm):
    """The form for the Comments model"""

    class Meta:
        model = Comments
        fields = ('text',)


class ComplaintsForm(forms.ModelForm):
    """The form for the Complaints model"""

    class Meta:
        model = Complaints
        fields = ('text',)


class ImageForm(forms.ModelForm):
    """The form for the Image model"""

    class Meta:
        model = Image
        exclude = ()


# the formset that unites adverts and images
ImageFormSet = forms.inlineformset_factory(
    Advertisement,
    Image,
    form=ImageForm,
    extra=1,
    max_num=5,
)
