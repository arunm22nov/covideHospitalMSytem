'''
Created on 17-Feb-2021

@author: aruns
'''

from django.db.models import Sum
from django.db.models import Q
from collections import OrderedDict

# from db.models import BedSystem,BedTypes


def setBedavailabilty(no_of_bed): 
    from .models import BedSystem, BedTypes
    BedTypes.objects.all().delete()    
    BedSystem.objects.all().delete()
    if no_of_bed >= 0 and no_of_bed < 4:

        BedTypes.objects.bulk_create([
            BedTypes(bed_id=1, bed_available=no_of_bed, bed_name='General'),
            BedTypes(bed_id=2, bed_available=0, bed_name='Semi Private'),
            BedTypes(bed_id=3, bed_available=0, bed_name='Private')
        
        ])
    else:
        no_general = (no_of_bed * 50) // 100    
        no_semi_private = (no_of_bed * 25) // 100
        no_private = (no_of_bed * 25) // 100  
        
        # no_general= no_general + (no_of_bed - (no_general+no_semi_private +no_private))
        general_bed_range = [i for i in range(0, (no_general * 2) - 1, 2)]
        semi_bed_range = [i for i in range(1, (no_semi_private * 4), 4)]
        private_bed_range = [i for i in range(3, (no_private * 4), 4)]
        updateDict = general_bed_range + semi_bed_range + private_bed_range
        bed_range = set(range(0, no_of_bed))
        differ_bed = bed_range.difference(set(updateDict))
        print(general_bed_range)
        print(semi_bed_range)
        print(private_bed_range)
        if len(differ_bed) > 0:
            for i in differ_bed:
                if i - semi_bed_range[len(semi_bed_range) - 1] == 4:
                    
                    no_semi_private = no_semi_private + 1
                elif i - private_bed_range[len(private_bed_range) - 1] == 4:
                    no_private += 1    
        no_general = no_general + (no_of_bed - (no_general + no_semi_private + no_private))
            
        BedTypes.objects.bulk_create([
                BedTypes(bed_id=1, bed_available=no_general, bed_name='General'),
                BedTypes(bed_id=2, bed_available=no_semi_private, bed_name='Semi Private'),
                BedTypes(bed_id=3, bed_available=no_private, bed_name='Private')
            
            ])
        
    
def getBedDetails(bedtype_list):
    from .models import BedSystem, BedTypes
    bedTypeQ = BedTypes.objects.all().values()
    general_bed_range = dict()
    semi_bed_range = dict()
    private_bed_range = dict()
    count_n = None
    Occupy_genralBed = 0
    Occupy_semiPrivateBed = 0
    Occupy_privateBed = 0
    if bedTypeQ.count() > 0:
        global general_index, semi_private_index, private_index
        # global 
        general_index = 0
        semi_private_index = 0
        private_index = 0
        count = bedTypeQ.aggregate(Sum('bed_available'))
        count_n = count['bed_available__sum']
        general_index = bedTypeQ[0]['bed_available']
        semi_private_index = bedTypeQ[1]['bed_available']
        private_index = bedTypeQ[2]['bed_available']  
        genral_bed = BedSystem.objects.filter(Q(bed_type=1) & Q(checkout=False)).values('bed_no')
        semi_private_bed = BedSystem.objects.filter(Q(bed_type=2) & Q(checkout=False)).values('bed_no')
        private_bed = BedSystem.objects.filter(Q(bed_type=3) & Q(checkout=False)).values('bed_no')
        genral_bed_count = [ i['bed_no'] for i in genral_bed]
        semi_private_bed_count = [ i['bed_no'] for i in semi_private_bed]
        private_bed_count = [ i['bed_no'] for i in private_bed]
        general_bed_range = OrderedDict()
        if genral_bed_count:
            Occupy_genralBed = len(genral_bed_count)
            Occupy_semiPrivateBed = len(semi_private_bed_count)
            Occupy_privateBed = len(private_bed_count)
            
        general_bed_range = {i: (True if (i in genral_bed_count) else False) for i in range(0, (general_index * 2) - 1, 2)}
        semi_bed_range = {i: (True if (i in semi_private_bed_count) else False) for i in range(1, (semi_private_index * 4), 4)}
        private_bed_range = {i: (True if (i in private_bed_count) else False) for i in range(3, (private_index * 4), 4)}
        
        if bedtype_list is None:
            return None
        
        if eval(bedtype_list) == 1:
            return general_bed_range
        elif eval(bedtype_list) == 2:
            return semi_bed_range
        elif eval(bedtype_list) == 3:
            return private_bed_range
        else:
            return None
        
        
def isPatientExist(p_name, m_number):
    from .models import BedSystem, BedTypes
    patientExist = BedSystem.objects.filter(Q(patient_name=p_name) & Q(patient_mobile=m_number) &Q(checkout=False)).exists()
    return patientExist  
