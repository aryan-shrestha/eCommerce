# Generated by Django 4.2.2 on 2023-07-07 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='user_profile/user.png', upload_to='user_profile/'),
        ),
    ]
