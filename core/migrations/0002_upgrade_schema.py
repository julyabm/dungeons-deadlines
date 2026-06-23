# Generated manually to upgrade legacy schema to AbstractUser + game fields

import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def copy_admin_to_staff(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT id, username, is_admin FROM usuarios')
        for user_id, username, is_admin in cursor.fetchall():
            cursor.execute(
                '''
                UPDATE usuarios
                SET email = %s, is_staff = %s, is_superuser = %s
                WHERE id = %s
                ''',
                [f'{username}@local.dev', bool(is_admin), bool(is_admin), user_id],
            )


def populate_item_slugs(apps, schema_editor):
    Item = apps.get_model('core', 'Item')
    for item in Item.objects.all():
        item.slug = f'item-{item.pk}'
        item.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='email',
            field=models.EmailField(default='legacy@local.dev', max_length=254, verbose_name='E-mail'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usuario',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='staff status'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='is_superuser',
            field=models.BooleanField(default=False, verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.RunPython(copy_admin_to_staff, migrations.RunPython.noop),
        migrations.RunSQL(
            sql='ALTER TABLE usuarios DROP COLUMN IF EXISTS is_admin;',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='usuario',
            name='username',
            field=models.CharField(
                error_messages={'unique': 'A user with that username already exists.'},
                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                max_length=150,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name='username',
            ),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='avatar',
            name='max_hp',
            field=models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(1)], verbose_name='HP Máximo'),
        ),
        migrations.AddField(
            model_name='avatar',
            name='total_xp',
            field=models.IntegerField(default=0, verbose_name='XP Total'),
        ),
        migrations.AddField(
            model_name='task',
            name='overdue_processed',
            field=models.BooleanField(default=False, verbose_name='Atraso Processado'),
        ),
        migrations.AddField(
            model_name='task',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Concluída em'),
        ),
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(max_length=50, null=True, verbose_name='Identificador'),
        ),
        migrations.AddField(
            model_name='item',
            name='icon',
            field=models.CharField(default='📦', max_length=10, verbose_name='Ícone'),
        ),
        migrations.RunPython(populate_item_slugs, migrations.RunPython.noop),
        migrations.RunSQL(
            sql='''
                DROP INDEX IF EXISTS core_item_slug_07f502d0_like;
                DROP INDEX IF EXISTS core_item_slug_07f502d0;
                CREATE UNIQUE INDEX IF NOT EXISTS core_item_slug_uniq ON core_item (slug);
                ALTER TABLE core_item ALTER COLUMN slug SET NOT NULL;
            ''',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='item',
                    name='slug',
                    field=models.SlugField(max_length=50, unique=True, verbose_name='Identificador'),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ActiveEffect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=50, verbose_name='Tipo')),
                ('expires_at', models.DateTimeField(verbose_name='Expira em')),
                ('avatar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='active_effects', to='core.avatar')),
            ],
            options={
                'unique_together': {('avatar', 'kind')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='inventory',
            unique_together={('avatar', 'item')},
        ),
    ]
