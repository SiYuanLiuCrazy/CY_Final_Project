from django import forms
from .models import TyPptCatalog

class CatalogForm(forms.Form):
    catalog = forms.CharField(max_length=64, label='Catalog Name')

    def __init__(self, *args, **kwargs):
        self.catalog_id = kwargs.pop('catalog_id', None)
        self.parent_id = kwargs.pop('parent_id', None)
        super().__init__(*args, **kwargs)

    def clean_catalog(self):
        catalog_name = self.cleaned_data['catalog']
        # 检查同级目录下是否有重名
        siblings = TyPptCatalog.objects.filter(parent_id=self.parent_id).exclude(id=self.catalog_id)
        if siblings.filter(label=catalog_name).exists():
            raise forms.ValidationError('名称重复，请重新编辑')
        return catalog_name