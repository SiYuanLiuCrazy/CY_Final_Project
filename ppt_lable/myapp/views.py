from django.shortcuts import render

# Create your views here.
import os
from django.http import HttpResponse
from .models import TyPptCatalog
from .forms import CatalogForm
from django.shortcuts import render, redirect, get_object_or_404
import uuid

def create_folder_view(request):
    if request.method == 'POST':
        form = CatalogForm(request.POST)
        if form.is_valid():
            catalog = form.cleaned_data['catalog']
            base_path = 'E:/tranyu_ppt/CY_Final_Project/ty_ppt_catalog'
            folder_path = os.path.join(base_path, catalog)

            if os.path.exists(folder_path):
                return HttpResponse('创建失败，文件夹已存在')

            os.makedirs(folder_path)
            
            TyPptCatalog.objects.create(
                label=catalog,
                path=folder_path
            )
            return redirect('catalog_list')
    else:
        form = CatalogForm()

    return render(request, 'create_folder.html', {'form': form})

def catalog_list_view(request):
    catalogs = TyPptCatalog.objects.filter(parent_id__isnull=True).order_by('label')
    return render(request, 'catalog_list.html', {'catalogs': catalogs})

def delete_catalog_view(request, catalog_id):
    catalog = get_object_or_404(TyPptCatalog, id=catalog_id)
    folder_path = catalog.path

    # 删除数据库记录
    catalog.delete()

    # 删除文件系统中的文件夹
    if os.path.exists(folder_path):
        try:
            os.rmdir(folder_path)  # os.rmdir 仅在文件夹为空时删除
        except OSError:
            # 如果文件夹不为空，可以使用 shutil.rmtree 递归删除
            import shutil
            shutil.rmtree(folder_path)

    return redirect('catalog_list')

def create_subitem_view(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        subitem_name = request.POST.get('subitem_name')
        
        parent_catalog = get_object_or_404(TyPptCatalog, id=parent_id)
        subitem_path = os.path.join(parent_catalog.path, subitem_name)
        
        if os.path.exists(subitem_path):
            return HttpResponse('创建失败，子项文件夹已存在')

        os.makedirs(subitem_path)
        
        TyPptCatalog.objects.create(
            label=subitem_name,
            path=subitem_path,
            parent_id=parent_catalog.id
        )
        return redirect('catalog_list')
    return redirect('catalog_list')

def edit_catalog_view(request, catalog_id):
    catalog = get_object_or_404(TyPptCatalog, id=catalog_id)
    if request.method == 'POST':
        form = CatalogForm(request.POST, catalog_id=catalog_id, parent_id=catalog.parent_id)
        if form.is_valid():
            new_label = form.cleaned_data['catalog']
            old_path = catalog.path
            new_path = os.path.join(os.path.dirname(old_path), new_label)
            catalog.label = new_label
            catalog.path = new_path
            catalog.save()

            # 如果是父文件夹，更新所有子文件夹的路径
            children = catalog.children.all()
            for child in children:
                child.path = os.path.join(new_path, child.label)
                child.save()

            return redirect('catalog_list')
    else:
        form = CatalogForm(initial={'catalog': catalog.label}, catalog_id=catalog_id, parent_id=catalog.parent_id)

    return render(request, 'edit_catalog.html', {'form': form, 'catalog': catalog})