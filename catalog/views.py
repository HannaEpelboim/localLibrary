from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    #desafio 
    num_genres = Genre.objects.count()
    num_books_with_The = Book.objects.filter(title__icontains='The').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_The': num_books_with_The,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

class AuthorDetailView(generic.DetailView):
    model = Author

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



###desafio
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

class LoanedBook(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """Generic class-based view listing books on loan."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    
    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage

class AuthorUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage

class AuthorDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    
    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage


from catalog.models import Book

class BookCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    fields = '__all__'

    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage


class BookUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book

    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage


class BookDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')

    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()
        #return True

    def handle_no_permission(self):
        return redirect('index')  # Redirect unauthorized users to the homepage
