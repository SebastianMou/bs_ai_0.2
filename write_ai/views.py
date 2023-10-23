from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm, TaskForm, DocumentForm
from .tokens import account_activation_token
from .models import Task, Document

# Create your views here.
def home(request):
    return render(request, 'home.html')

def main(request):
    return render(request, 'main_page/main.html')

def chat(request):
    return render(request, 'main_page/chat_content.html')

def img_gen(request):
    return render(request, 'main_page/img_gen.html')

def tasks(request):
    all_tasks = Task.objects.order_by('position')
    tasks = all_tasks.filter(owner=request.user)
    task_count = tasks.count()

    status_counts = {}
    for status, _ in Task.STATUS_CHOICES:
        status_counts[status] = tasks.filter(status=status).count()

    context = {
        'tasks': tasks,
        'task_count': task_count,
        'status_counts': status_counts,
    }
    return render(request, 'main_page/tasks.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.success(request, "Invalid username or password.")

    return render(request, 'auth/user_login.html')

def login_with_email(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'auth/login_with_email.html')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('main'))

def user_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main'))
    else:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                if User.objects.filter(email=email) and User.objects.filter(username=username).exists():
                    messages.error(request, 'This email is already registered.')
                    return redirect('user_register')
                else:
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()
                    activateEmail(request, user, form.cleaned_data.get('email'))
                    return redirect('sending_activate_token')
        else:
            form = UserRegisterForm()
        context = {
            'form': form,
        }
        return render(request, 'auth/register.html', context)

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for confirming your email. You can now log in to your account.')
        return redirect('user_login')
    else:
        messages.error(request, 'The activation link is not valid!')
    
    return render(request, 'auth/login.html')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('auth/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain.split('://')[-1],  # This ensures only the domain is taken
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html"  
    if email.send():
        messages.success(request, f'Dear {user}, please go to your email {to_email} and click on the activation link you received to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, please check if you entered it correctly.')

def sending_activate_token(request):
    return render(request, 'auth/sending_activate_token.html')

@login_required
def tasks(request):
    all_tasks = Task.objects.order_by('position')
    tasks = all_tasks.filter(owner=request.user)
    task_count = tasks.count()

    status_counts = {}
    for status, _ in Task.STATUS_CHOICES:
        status_counts[status] = tasks.filter(status=status).count()

    if request.method == 'POST':
        form_task = TaskForm(request.POST)
        if form_task.is_valid():
            task = form_task.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect('tasks')
    else: 
        form_task = TaskForm(request.POST)
    context = {
        'tasks': tasks,
        'task_count': task_count,
        'status_counts': status_counts,
        'form_task': form_task,
    }
    return render(request, 'task/tasks_test.html', context)

def update_task_order(request):
    """
    Handle the request to update the order and status of tasks.

    This view expects a POST request with 'item' and 'status' data.
    'item' contains the IDs of tasks in their current order.
    'status' contains the status of each task.

    The function updates the position and status of each task in the database.
    """
    # Check if the request method is POST.
    if request.method == "POST":
        
        # Extract the list of task IDs from the POST data.
        items = request.POST.getlist('item')
        
        # Extract the list of statuses from the POST data.
        statuses = request.POST.getlist('status')
        
        # Print the received items and statuses for debugging purposes.
        print("Received items:", items)  
        print("Received statuses:", statuses) 
        
        # Loop through each task ID and status.
        for index, (item_id, status) in enumerate(zip(items, statuses)):
            
            # Fetch the task object from the database using its ID.
            task = Task.objects.get(id=item_id)
            
            # Update the task's position based on its order in the received list.
            task.position = index
            
            # Update the task's status.
            task.status = status
            
            # Save the updated task to the database.
            task.save()

    # Return a 204 No Content response to indicate successful processing.
    return HttpResponse(status=204)

def items_detail(request, pk):
    task = get_object_or_404(Task, id=pk)
    context = {
        'task': task,
    }
    return render(request, 'task/items_detail.html', context)

@login_required
def create_task(request):
    if request.method == 'POST':
        form_task = TaskForm(request.POST)
        if form_task.is_valid():
            task = form_task.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect('tasks')
    else: 
        form_task = TaskForm(request.POST)
    
    context = {
        'form_task': form_task,
    }
    return render(request, 'task/create_task.html', context)

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, id=pk, owner=request.user)  # Ensure the task belongs to the logged-in user
    if request.method == 'POST':  # Confirm the task deletion with a POST request
        task.delete()
        return redirect('tasks')  # Redirect to the tasks view after deletion
    context = {
        'task': task,
    }
    return render(request, 'task/confirm_delete.html', context)

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, id=pk, owner=request.user)  # Ensure the task belongs to the logged-in user
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')  
    else:
        form = TaskForm(instance=task) 
    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'task/edit_task.html', context)

@login_required
def ai_documents(request):
    documents = Document.objects.filter(owner=request.user)
    context = {
        'documents': documents
    }
    return render(request, 'main_page/ai_documents.html', context)

@login_required
def create_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            return redirect('ai_documents')
    else:
        form = DocumentForm()

    context = {
        'form': form
    }
    return render(request, 'ai document/create_document.html', context)

@login_required
def edit_document(request, pk):
    document = get_object_or_404(Document, id=pk, owner=request.user)
    documents_all_user = Document.objects.filter(owner=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            return redirect('ai_documents')  # Ensure 'tasks' is a valid redirect URL name
    else:
        form = DocumentForm(instance=document) 

    context = {
        'form': form,
        'document': document,
        'documents_all_user': documents_all_user,
    }
    return render(request, 'ai document/edit_document.html', context)

def view_document(request, pk):
    document_view = get_object_or_404(Document, id=pk, owner=request.user)
    context = {
        'document_view': document_view,
    }
    return render(request, 'ai document/view_document.html', context)


def public_privacy_policy(request):
    return render(request, 'legal/public_privacy_policy.html')

def public_terms_of_service(request):
    return render(request, 'legal/public_terms_of_service.html')
