# Generated by Django 5.0.7 on 2024-07-16 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UID', models.TextField(default='0', max_length=256)),
                ('name', models.TextField(default='0', max_length=256)),
                ('user_name', models.TextField(default='0', max_length=256)),
                ('email', models.TextField(default='0', max_length=256)),
                ('password', models.TextField(default='0', max_length=256)),
                ('token', models.TextField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(default='0', on_delete=django.db.models.deletion.CASCADE, to='chat.chatroom')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.user')),
            ],
        ),
        migrations.AddField(
            model_name='chatroom',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatrooms_user1', to='chat.user'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatrooms_user2', to='chat.user'),
        ),
        migrations.AlterUniqueTogether(
            name='chatroom',
            unique_together={('user1', 'user2')},
        ),
    ]
