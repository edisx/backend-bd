from django.contrib import admin
from .models import Note


# FIXME: move admin to some safe url later

#TODO: remove this later
admin.site.register(Note)
