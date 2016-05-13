# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_category_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='concacts',
            new_name='contacts',
        ),
    ]
