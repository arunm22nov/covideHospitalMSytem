from .Utils import getBedDetails, isPatientExist
from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.forms.forms import Form


# Create your models here.


class BedTypes(models.Model):
    
    bed_id = models.IntegerField(primary_key=True)
    bed_available = models.IntegerField()
    bed_name = models.CharField(max_length=20)


class BedSystem(models.Model):
    bed_no = models.PositiveIntegerField()
    bed_type = models.ForeignKey(BedTypes, on_delete=models.CASCADE, null=True)
    free_or_occupy = models.BooleanField(default=False)
    patient_name = models.CharField(max_length=20)
    patient_mobile = models.CharField(max_length=10)
    checkout = models.BooleanField(default=False)

    
class BedSystemForm(forms.ModelForm):
    b = (
        (1, "General"),
                 (2, 'Semi Private'),
                 (3, 'Private'))
    type = forms.ChoiceField(choices=b, widget=forms.Select(attrs={"class": "form-control"}))

    def clean_patient_mobile(self):
        data = self.cleaned_data["patient_mobile"]  
        if len(data) < 10:
            raise forms.ValidationError("Please enter 10 number of digit")   
        elif data.isnumeric() is False:
            raise forms.ValidationError("Please enter only digit")
        return data

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("type")
        bedNo = cleaned_data.get("bed_no")
        p_name = cleaned_data.get("patient_name")
        p_number = cleaned_data.get("patient_mobile")
        bed_details = getBedDetails(data)
        print(bed_details)
        if isPatientExist(p_name, p_number):
            print(isPatientExist(p_name, p_number))
            self.add_error('patient_mobile', 'This patient name and mobile number is already exist in Bed System')
               
        if bed_details is None or bedNo not in  bed_details.keys():
            self.add_error('bed_no', 'Bed number is not t Associated with Bed Type')
        elif bedNo in bed_details.keys() and bed_details.get(bedNo) == True:
            self.add_error('bed_no', 'This bed no is already occupy Please choose other one')
    
    class Meta:
        model = BedSystem
        fields = ('type', 'bed_no', 'patient_name', 'patient_mobile')
        widgets = {
            'bed_no': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_mobile': forms.TextInput(attrs={'class': 'form-control'})
        
        }

