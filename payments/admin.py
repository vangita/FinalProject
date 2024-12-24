from django.contrib import admin

import payments
from payments.models import Payment

# Register your models here.

admin.site.register(Payment)