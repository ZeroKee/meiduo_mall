from django.db import models


class Areas(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True)

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name