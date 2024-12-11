# File: forms.py
# Author: James Xiao (jamxiao@bu.edu), 12/11/2024
# Description: File for defining forms used in project
from django import forms
from .models import UserProfile, Receipt
from django.core.exceptions import ValidationError

class CreateProfileForm(forms.ModelForm):
    '''A form to create a profile'''
    class Meta:
        model = UserProfile 
        fields = ['first_name', 'last_name', 'email', 'profile_image_url']
class UpdateUserProfileForm(forms.ModelForm):
    '''A form to update a profile'''
    class Meta:
        model = UserProfile
        fields = [ 'email', 'profile_image_url']


class ReceiptUploadForm(forms.ModelForm):
    '''Form for uploading receipt'''
    receipt_image = forms.ImageField()
    class Meta:
        model = Receipt
        fields = ['receipt_image']
    def clean_receipt_image(self):
        receipt_image = self.cleaned_data.get('receipt_image')
        print(receipt_image.name)
        # 1. Check if file is provided
        if not receipt_image:
            raise ValidationError("No file uploaded. Please upload a receipt image.")

        # 2. Check file size (limit to 20MB)
        max_size = 20 * 1024 * 1024  # 20MB in bytes
        if receipt_image.size > max_size:
            raise ValidationError("The file is too large. Maximum allowed size is 20MB.")

        # 3. Check file extension (allow jpg, jpeg, png, pdf)
        valid_extensions = ['jpg', 'jpeg', 'png']
        file_extension = receipt_image.name.split('.')[-1].lower()
        if file_extension not in valid_extensions:
            raise ValidationError("Invalid file type. Only JPG, JPEG, and PNG files are allowed.")

        return receipt_image