from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader


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

@login_required
def public(request):
    return render(request, 'public.html')


def handle_uploaded_file(f):
    local_file = '/tmp/name.txt'
    with open(local_file, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        return local_file


@login_required
def send(request):
    from django.http import HttpResponseRedirect
    from batch.forms import SendForm

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = SendForm(request.POST, request.FILES)

        if form.is_valid():
            batch = form.save(commit=False)
            batch.User_ID = request.user;
            batch.save()
            return HttpResponseRedirect('/my')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SendForm()

    return render(request, 'send.html', {'form': form})

@login_required
def view(request):
    return render(request, 'view.html')


