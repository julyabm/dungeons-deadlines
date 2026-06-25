# Generated manually for avatar cosmetics

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_task_options_alter_usuario_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='skin_tone',
            field=models.CharField(
                choices=[
                    ('light',  'Tom de pele 1'),
                    ('medium', 'Tom de pele 2'),
                    ('dark',   'Tom de pele 3'),
                    ('pale',   'Tom de pele 4'),
                    ('tan',    'Tom de pele 5'),
                    ('olive',  'Tom de pele 6'),
                    ('deep',   'Tom de pele 7'),
                ],
                default='medium',
                max_length=10,
                verbose_name='Tom de pele',
            ),
        ),
        migrations.AlterField(
            model_name='avatar',
            name='hair_style',
            field=models.CharField(
                choices=[
                    ('short',    'Curto'),
                    ('long',     'Longo'),
                    ('spiky',    'Espetado'),
                    ('curly',    'Cacheado'),
                    ('bald',     'Careca'),
                    ('ponytail', 'Rabo de Cavalo'),
                    ('mohawk',   'Moicano'),
                ],
                default='short',
                max_length=10,
                verbose_name='Estilo de cabelo',
            ),
        ),
        migrations.AlterField(
            model_name='avatar',
            name='hair_color',
            field=models.CharField(
                choices=[
                    ('black',  'Preto'),
                    ('brown',  'Castanho'),
                    ('blonde', 'Loiro'),
                    ('red',    'Ruivo'),
                    ('white',  'Branco'),
                    ('gray',   'Cinza'),
                    ('blue',   'Azul'),
                    ('green',  'Verde'),
                    ('purple', 'Roxo'),
                    ('pink',   'Rosa'),
                ],
                default='brown',
                max_length=10,
                verbose_name='Cor do cabelo',
            ),
        ),
        migrations.AlterField(
            model_name='item',
            name='cosmetic_slot',
            field=models.CharField(
                blank=True,
                choices=[
                    ('head', 'Cabeça'),
                    ('body', 'Corpo'),
                    ('face', 'Rosto'),
                ],
                max_length=10,
                null=True,
                verbose_name='Slot cosmético',
            ),
        ),
    ]
