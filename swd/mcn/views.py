import json
from datetime import datetime, date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware

from swd import settings
from .models import MCNApplication, MCNApplicationPeriod
from main.models import Student, Leave, DayPass, Bonafide, Due, TeeBuy, ItemBuy, MessOptionOpen, MessOption


@login_required
def submit_mcn(request):

    # =================== LEFT PANEL ===================

    student = Student.objects.get(user=request.user)

    timediff = date.today() - timedelta(days=7)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=timediff)
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=timediff)
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=timediff)

    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0

    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount            

    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    swd_adv = float(data['swd-advance'])
    balance = swd_adv - float(total_amount)
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

    context = {
        'student': student,
        'balance': balance,
        'option': option,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
        'errors': []
    }

    # =================== SUBMISSION ===================

    currentDate = datetime.now()
    mcn_period = MCNApplicationPeriod.objects.filter(Open__lte=currentDate, Close__gte=currentDate).last()
    context['mcn_period'] = mcn_period

    already_submitted = MCNApplication.objects.filter(student=request.user.student, ApplicationPeriod=mcn_period).last()
    context['already_submitted'] = already_submitted

    if request.method == 'POST' and mcn_period and already_submitted is None:
        FathersIncome = request.POST['FathersIncome']
        FathersIncome = 0 if FathersIncome is '' else int(FathersIncome)

        MothersIncome = request.POST['MothersIncome']
        MothersIncome = 0 if MothersIncome is '' else int(MothersIncome)

        FathersIncomeDoc = request.FILES.get('FathersIncomeDoc', None)
        MothersIncomeDoc = request.FILES.get('MothersIncomeDoc', None)
        
        TehsildarCertificate = request.FILES.get('TehsildarCertificate', None)
        BankPassbook = request.FILES.get('BankPassbook', None)

        tehsil = ((TehsildarCertificate) or (BankPassbook))

        if FathersIncome == 0 and MothersIncome == 0:
            context['errors'].append("Please enter income of earning parent.")
            return render(request, "mcn_submit.html", context)
        else:
            if (FathersIncome != 0) and (not FathersIncomeDoc) and (not tehsil):
                context['errors'].append("Please upload proof of Father\'s Income.")
                return render(request, "mcn_submit.html", context)
            if (MothersIncome != 0) and (not MothersIncomeDoc) and (not tehsil):
                context['errors'].append("Please upload proof of Mother\'s Income.")
                return render(request, "mcn_submit.html", context)

        if (FathersIncomeDoc is None) and (MothersIncomeDoc is None):
            # If neither of father's or mother's income certificate is uploaded
            # check if both Tehsil Certificate and Passbook are uploaded
            if TehsildarCertificate is None or BankPassbook is None:
                doc_error_str = "Please upload both Tehsildar's Certificate and Bank Passbook" \
                                                    " or earning parent's income certificate"
                context['errors'].append(doc_error_str)
                return render(request, "mcn_submit.html", context)

        supported_exts = ['pdf', 'jpg', 'jpeg', 'png']

        for doc in [MothersIncomeDoc, FathersIncomeDoc, TehsildarCertificate, BankPassbook]:
            if doc is not None:
                ext = doc.name.split('.')[-1]
                if ext not in supported_exts:
                    msg_txt = "Invalid uploaded document type of {}".format(doc.name)
                    msg_txt += ", it should be one of "
                    msg_txt += ', '.join(supported_exts)
                    context['errors'].append(msg_txt)

        if len(context['errors']):
            return render(request, "mcn_submit.html", context)

        mcn_application = MCNApplication.objects.create(
            student=student,
            ApplicationPeriod=mcn_period,
            FathersIncome=FathersIncome,
            FathersIncomeDoc=FathersIncomeDoc,
            MothersIncome=MothersIncome,
            MothersIncomeDoc=MothersIncomeDoc,
            TehsildarCertificate=TehsildarCertificate,
            BankPassbook=BankPassbook
            )

        context['success'] = True

    return render(request, "mcn_submit.html", context)