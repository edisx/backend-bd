from django.db import models


#TODO: remove this later
# simple note model name and text
class Note (models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.name
