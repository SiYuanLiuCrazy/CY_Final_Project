from django.shortcuts import render

# Create your views here.
import os
from django.http import HttpResponse
from .models import TyPptCatalog
from .forms import CatalogForm
from django.shortcuts import render, redirect, get_object_or_404
import uuid
import shutil

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
    catalogs = TyPptCatalog.objects.all().order_by('label')
    catalog_tree = get_catalog_tree(catalogs)
    return render(request, 'catalog_list.html', {'catalog_tree': catalog_tree})

def delete_catalog_view(request, catalog_id):
    catalog = get_object_or_404(TyPptCatalog, id=catalog_id)

    # 递归删除目录及其所有子目录
    def delete_directory(catalog):
        folder_path = catalog.path
        children = catalog.children.all()
        for child in children:
            delete_directory(child)  # 递归调用删除子目录
        
        catalog.delete()  # 删除数据库记录

        # 删除文件系统中的文件夹
        if os.path.exists(folder_path):
            try:
                os.rmdir(folder_path)  # os.rmdir 仅在文件夹为空时删除
            except OSError:
                # 如果文件夹不为空，使用 shutil.rmtree 递归删除
                shutil.rmtree(folder_path)
    
    try:
        delete_directory(catalog)
    except Exception as e:
        return HttpResponse(f'删除失败: {e}', status=500)

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

            # 尝试更改父文件夹的名称
            try:
                os.rename(old_path, new_path)
            except OSError as e:
                return HttpResponse(f'Error renaming folder: {e}', status=500)

            # 更新父文件夹信息并保存到数据库
            catalog.label = new_label
            catalog.path = new_path
            catalog.save()

            # 定义更新子文件夹路径的递归函数
            errors = []
            def update_children_paths(parent_catalog):
                children = parent_catalog.children.all()
                for child in children:
                    old_child_path = child.path
                    new_child_path = os.path.join(parent_catalog.path, child.label)
                    try:
                        if os.path.exists(old_child_path):
                            os.rename(old_child_path, new_child_path)  # 更改文件系统中的路径
                        child.path = new_child_path  # 更新子目录的数据库记录
                        child.save()
                        update_children_paths(child)  # 递归更新更深层次的子文件夹
                    except OSError as e:
                        errors.append(f'Error renaming child folder {child.label}: {e}')

            # 更新所有子文件夹的路径
            update_children_paths(catalog)

            if errors:
                return HttpResponse("<br>".join(errors), status=500)

            return redirect('catalog_list')
    else:
        form = CatalogForm(initial={'catalog': catalog.label}, catalog_id=catalog_id, parent_id=catalog.parent_id)

    return render(request, 'edit_catalog.html', {'form': form, 'catalog': catalog})

def move_catalog_view(request):
    if request.method == 'POST':
        catalog_id = request.POST.get('catalog_id')
        target_folder_id = request.POST.get('target_folder')

        catalog = get_object_or_404(TyPptCatalog, id=catalog_id)
        target_folder = get_object_or_404(TyPptCatalog, id=target_folder_id)

        old_path = catalog.path
        new_path = os.path.join(target_folder.path, catalog.label)

        if os.path.exists(new_path):
            return HttpResponse('移动失败，目标文件夹中已存在同名文件夹')

        # 移动文件夹
        try:
            shutil.move(old_path, new_path)  # 使用shutil.move而不是os.rename来处理跨分区移动
        except OSError as e:
            return HttpResponse(f'Error moving folder: {e}', status=500)

        # 更新数据库中的路径信息
        catalog.parent_id = target_folder.id
        catalog.path = new_path
        catalog.save()

        # 更新子文件夹的路径信息
        def update_children_paths(parent_catalog, new_parent_path):
            children = parent_catalog.children.all()
            for child in children:
                old_child_path = child.path
                new_child_path = os.path.join(new_parent_path, child.label)
                try:
                    if os.path.exists(old_child_path):
                        shutil.move(old_child_path, new_child_path)  # 使用shutil.move而不是os.rename
                    child.path = new_child_path
                    child.save()
                    update_children_paths(child, new_child_path)
                except OSError as e:
                    return HttpResponse(f'Error renaming child folder {child.label}: {e}', status=500)

        update_children_paths(catalog, new_path)

        return redirect('catalog_list')
    else:
        return redirect('catalog_list')
    
def get_catalog_tree(catalogs, parent=None, level=0):
    tree = []
    for catalog in catalogs:
        if catalog.parent_id == parent:
            indent = '&nbsp;' * level * 4  # 生成缩进字符串
            tree.append((catalog, indent))
            tree.extend(get_catalog_tree(catalogs, catalog.id, level + 1))
    return tree