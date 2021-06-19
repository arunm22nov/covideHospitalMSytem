from django.shortcuts import render
from .Utils import setBedavailabilty
from .models import BedTypes
from django.db.models import Sum
from django.db.models.functions import Cast
from django.http import JsonResponse
from .models import BedSystemForm, BedTypes, BedSystem
from django.db.models import Q
from django.core import serializers
from collections import OrderedDict

# Create your views here.


def home(request):
    assign_form = None
    patient_name = None
    bedList = None
    bed_status = None
    bed_checkout = None
    
    if request.method == 'POST':
        print(request.POST)
        if  request.POST.get('form_type') == 'bed_assign':
            assign_form = BedSystemForm(request.POST)
            
            if assign_form.is_valid():
            
                assign_form.save(commit=False)
                bed_type = request.POST['type']
                bed_type_q = BedTypes.objects.get(pk=eval(bed_type))
                
                BedSystem.objects.create(bed_no=request.POST['bed_no'], bed_type=bed_type_q, free_or_occupy=True, patient_name=request.POST['patient_name'], patient_mobile=request.POST['patient_mobile'], checkout=False) 
        else:
            assign_form = BedSystemForm()   
        if request.POST.get('form_type') == 'bed_details': 
            param = request.POST.get('selectDetailsType')
            if param == '1':
                bedList = BedSystem.objects.all()
            elif param == '2':
                bedList = BedSystem.objects.filter(bed_type=1)
            elif param == '3':
                bedList = BedSystem.objects.filter(bed_type=2)
            elif param == '4':
                bedList = BedSystem.objects.filter(bed_type=3)
            if bedList:
                bedList = list(bedList)
                print(bedList)
           
        elif request.POST.get('form_type') == 'bedNo':
            bedNo = request.POST.get('bed_no')
            bed_status = BedSystem.objects.filter(bed_no=eval(bedNo)).values('bed_no', 'patient_name', 'patient_mobile', 'bed_type__bed_name')
            
        elif request.POST.get('form_type') == 'bedCheckout' and request.POST.get('isConfirm') == '1':
            bedNo = request.POST.get('bed_no')
            
            bed_checkout = BedSystem.objects.filter(bed_no=eval(bedNo)).update(checkout=True)   
            
    else:
        
        assign_form = BedSystemForm()
   
    if bedList is None:
        bedList = BedSystem.objects.all()
        bedList = list(bedList)
    bedTypeQ = BedTypes.objects.all().values()
    general_bed_range = dict()
    semi_bed_range = dict()
    private_bed_range = dict()
    count_n = None
    Occupy_genralBed = 0
    Occupy_semiPrivateBed = 0
    Occupy_privateBed = 0
    general_index = 0
    semi_private_index = 0
    private_index = 0
    
    if bedTypeQ.count() > 0:
       
        print(bedTypeQ)
       
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
    
    return render(request, 'home.html', {'assign_form': assign_form, "no_of_bed":count_n, 'general':general_bed_range,
                                       'semi_private':semi_bed_range, 'private': private_bed_range, 'patient_name':patient_name,
                                       'bed_details':bedList, 'bed_status':bed_status, 'bed_checkout':bed_checkout
                                       , 'total_genralBed':general_index, 'Occupy_genralBed':Occupy_genralBed
                                       , 'free_genralBed':(general_index - Occupy_genralBed),
                                       'total_semiPrivateBed':semi_private_index, 'total_privateBed':private_index,
                                       'Occupy_semiPrivateBed':Occupy_semiPrivateBed,
                                       'Occupy_privateBed':Occupy_privateBed,
                                       'free_semiPrivateBed':(semi_private_index - Occupy_semiPrivateBed),
                                       'free_privateBed':(private_index - Occupy_privateBed)
                                       })


def setBedCount(request):
    
    if request.is_ajax():
        param = request.GET.get('param', None)
        setBedavailabilty(int(param))
        return JsonResponse({'result': 'OK'})
    
    
def getAllPatientList(request):
    value = None
    if request.is_ajax():
        param = request.GET.get('param', None)
        if param == 'All':
            value = BedSystem.objects.all().values()
        elif param == 'By General Bed':
            value = BedSystem.objects.filter(bed_type=1).values()
            
        elif param == 'By Semi Private':
            value = BedSystem.objects.filter(bed_type=2).values()
        elif param == 'By Private':
            value = patient_name = BedSystem.objects.filter(bed_type=3).values()
        
    # s=serializers.seialize('json', value)
    data = None
    if value:
        
        data = {'response': list(value)}
    else:
        data = {'response':""}
    return JsonResponse(data, safe=False)


def getBedStatus(request):
    value = None
    if request.is_ajax():
        param = request.GET.get('param', None)     
        value = BedSystem.objects.filter(bed_no=param).values('bed_no','bed_type__bed_name','free_or_occupy','patient_name','patient_mobile','checkout')
        print(value)
    data = None
    if value:
        
        data = {'response': list(value)}
    else:
        data = {'response':""}
    return JsonResponse(data, safe=False)

