from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.conf import  settings


# signup: allauth.account.forms.SignupForm
# signup: allauth.socialaccount.forms.SignupForm
# add_email: allauth.account.forms.AddEmailForm
# change_password: allauth.account.forms.ChangePasswordForm
# reset_password: allauth.account.forms.ResetPasswordForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


@login_required
def my(request):
    from batch.models import Batch
    query_results = Batch.objects.filter(User_ID=request.user)
    template = loader.get_template('my.html')
    context = {
        'query_results': query_results,
    }
    return HttpResponse(template.render(context, request))


# no login
def public(request):
    from batch.models import Batch

    public_batches = Batch.objects.filter(Project_IsPublic=True)

    template = loader.get_template('public.html')

    context = {
        'public_batches': public_batches,
    }

    return HttpResponse(template.render(context, request))


@login_required
def send(request):
    from django.http import HttpResponseRedirect
    from .forms import SendForm
    from .helpers import handle_uploaded_file

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = SendForm(request.POST, request.FILES)

        if form.is_valid():
            batch = form.save(commit=False)
            batch.User_ID = request.user
            batch.save()

            # analyse
            uploaded = batch.Project_FileSourcePathName.path
            (analyse_result, file_csv) = handle_uploaded_file(uploaded, batch)

            if analyse_result:
                batch.Project_FileSourcePathName = file_csv
                batch.save()

            return HttpResponseRedirect('/view/' + str(batch.Batch_Id))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SendForm()

    return render(request, 'send.html', {'form': form})


@login_required
def view(request, batch_id=None):
    from .models import Batch
    from .helpers import get_csv_lines
    from django.conf import settings
    import os
    import json

    FIRST_LINES = 5
    LAST_LINES = 5

    batch = Batch.objects.get(Batch_Id=batch_id)

    #
    if os.path.isfile(batch.Project_FileSourcePathName.path):
        file_name = batch.Project_FileSourcePathName.path
        (csv_title, csv_first, csv_last) = get_csv_lines(file_name, 1 + FIRST_LINES, LAST_LINES)
        csv_last.reverse()
    else:
        (csv_title, csv_first, csv_last) = ([], [], [])

    #
    if batch.AnalysisSource_ColumnsNameInput:
        analyser_cols_input = json.loads(batch.AnalysisSource_ColumnsNameInput)
    else:
        analyser_cols_input = []

    #
    if batch.AnalysisSource_ColumnsNameOutput:
        analyser_cols_output = json.loads(batch.AnalysisSource_ColumnsNameOutput)
    else:
        analyser_cols_output = []

    #
    if batch.AnalysisSource_ColumnType:
        analyser_cols_type_in = []
        types = json.loads(batch.AnalysisSource_ColumnType)
        for cname in analyser_cols_input:
            tp = types[cname]
            analyser_cols_type_in.append( tp )
    else:
        analyser_cols_type_in = []

    #
    if batch.AnalysisSource_ColumnType:
        analyser_cols_type_out = []
        types = json.loads(batch.AnalysisSource_ColumnType)
        for cname in analyser_cols_output:
            tp = types[cname]
            analyser_cols_type_out.append( tp )
    else:
        analyser_cols_type_out = []

    #
    analyser_first_5 = []
    for row in csv_first:
        newrow = []
        for title in analyser_cols_input:
            i = csv_title.index(title)
            newrow.append(row[i])
        for title in analyser_cols_output:
            i = csv_title.index(title)
            newrow.append(row[i])
        analyser_first_5.append(newrow)

    #
    analyser_last_5 = []
    for row in csv_last:
        newrow = []
        for title in analyser_cols_input:
            i = csv_title.index(title)
            newrow.append(row[i])
        for title in analyser_cols_output:
            i = csv_title.index(title)
            newrow.append(row[i])
        analyser_last_5.append(newrow)

    template = loader.get_template('view.html')

    context = {
        'batch': batch,
        'csv_title': csv_title,
        'csv_first': csv_first,
        'csv_last' : csv_last,
        'analyser_errors'       : batch.AnalysisSource_Errors,
        'analyser_warnings'     : batch.AnalysisSource_Warnings,
        'analyser_cols_input'   : analyser_cols_input,
        'analyser_cols_output'  : analyser_cols_output,
        'analyser_cols_type_in' : analyser_cols_type_in,
        'analyser_cols_type_out': analyser_cols_type_out,
        'analyser_first_5'      : analyser_first_5,
        'analyser_last_5'       : analyser_last_5,
    }
    return HttpResponse(template.render(context, request))
