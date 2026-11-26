from django.db import migrations, models
from django.db.models import F


def preserve_history(apps, schema_editor):
    history = apps.get_model('store', 'FinishedProductCostHistory')
    history.objects.using(schema_editor.connection.alias).update(
        reference_cost=F('bead_cost') + F('accessory_cost') + F('labor_cost') + F('elastic_cost'),
    )


class Migration(migrations.Migration):
    dependencies = [('store', '0018_alter_finishedproductaccessory_accessory_and_more')]
    operations = [
        migrations.AddField('finishedproduct', 'cost_mode', models.CharField(max_length=10, choices=[('auto', '按组成核算'), ('manual', '独立定价')], default='auto', verbose_name='成本模式')),
        migrations.AddField('finishedproduct', 'manual_cost', models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='独立整件成本')),
        migrations.AddField('finishedproductcosthistory', 'cost_mode', models.CharField(max_length=10, default='auto', verbose_name='当时成本模式')),
        migrations.AddField('finishedproductcosthistory', 'reference_cost', models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='参考测算成本')),
        migrations.AddField('finishedproductcosthistory', 'change_type', models.CharField(max_length=20, default='legacy', verbose_name='变更类型')),
        migrations.RunPython(preserve_history, migrations.RunPython.noop),
    ]
