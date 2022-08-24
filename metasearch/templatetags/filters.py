from django import template

register = template.Library()

@register.filter('link_wrapper')
def link_wrapper(link, search_engine):
    if search_engine == 'GOOGLE PATENTS':
        return f'g-https://patents.google.com/{link}'
    elif search_engine == 'LENS':
        return f'l-https://www.lens.org{link}'
    elif search_engine == 'PATENTSCOPE':
        return f'p-https://patentscope.wipo.int/search/en/{link}'
    

@register.filter()
def second_wrapper(link, query):
    if link[0] == 'g':
        query = query.replace(' ', '+')
        return link[2:] + f'?q={query}&oq={query}'
    else:
        return link[2:]

