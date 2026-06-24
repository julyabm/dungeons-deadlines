from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_upgrade_schema'),
    ]

    operations = [
        migrations.AddField(
            model_name='avatar',
            name='hair_color',
            field=models.CharField(
                choices=[('black', 'Preto'), ('brown', 'Castanho'), ('blonde', 'Loiro'), ('red', 'Ruivo')],
                default='brown',
                max_length=10,
                verbose_name='Cor do cabelo',
            ),
        ),
        migrations.AddField(
            model_name='avatar',
            name='hair_style',
            field=models.CharField(
                choices=[('short', 'Curto'), ('long', 'Longo'), ('spiky', 'Espetado')],
                default='short',
                max_length=10,
                verbose_name='Estilo de cabelo',
            ),
        ),
        migrations.AddField(
            model_name='avatar',
            name='skin_tone',
            field=models.CharField(
                choices=[('light', 'Claro'), ('medium', 'Médio'), ('dark', 'Escuro')],
                default='medium',
                max_length=10,
                verbose_name='Tom de pele',
            ),
        ),
        migrations.AddField(
            model_name='item',
            name='cosmetic_slot',
            field=models.CharField(
                blank=True,
                choices=[('head', 'Cabeça'), ('body', 'Corpo')],
                max_length=10,
                null=True,
                verbose_name='Slot cosmético',
            ),
        ),
        migrations.AddField(
            model_name='item',
            name='layer_file',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Arquivo de camada'),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_type',
            field=models.CharField(
                choices=[
                    ('Consumível', 'Consumível'),
                    ('Equipamento', 'Equipamento'),
                    ('Cosmético', 'Cosmético'),
                ],
                max_length=50,
                verbose_name='Tipo',
            ),
        ),
    ]
