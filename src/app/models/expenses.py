from django.db import models 

class Expenses(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    create_by = models.CharField(max_length=150, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_by = models.CharField(max_length=150, null=True, blank=True)
    update_date = models.DateTimeField(default=None, null = True , blank=True)
    price = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    destination = models.CharField(max_length=150, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Expenses'
    def __str__(self):
        return "%s" % (self.name)