from django.views.generic import TemplateView, ListView


class HomePageView(TemplateView):
    template_name = 'home_page.html'


class SearchResultsView(ListView):
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return query