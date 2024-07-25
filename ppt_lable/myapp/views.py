from django.shortcuts import render

# Create your views here.
import os
from django.http import HttpResponse
from .models import TyPptCatalog, TyPptMain
from .forms import CatalogForm
from django.shortcuts import render, redirect, get_object_or_404
import uuid
import shutil
from django.core.files.storage import FileSystemStorage
from spire.presentation import *
License.SetLicenseKey("3vgBAP6gsMpt19Lp5/dLFp/xNXCyz2vrwWXv6RZ9dhyEE6o0AFXtRmuqeHo1LxSwxYqobFgqbUkY/8y0oqHns0AgcGdhUi/gxW3rgxU03m9Je53kYu9SVmpp/9SEEkUhzJ08Ir3+/014o07W0UXzj63zhaQjMxz5Lmx+U08qabOyQmGmnbolIYd70slekKohJLucSw9KL/OxAzIhBdI1+IaElvL2jUsl1w0zGfyVVG56vcENaCh23rDBNUdkTHccDEOW9L3Qa1DZtUpJadmED0scQbbsDHtrJ8sR03yxa2stkpjXUYcVyE9xZphrvWHYvvxAt1UOFOpYxzSwvxS7TIFEhXQBzcHRpEidD1BnBQgIMvo9tdqQQCKCx4k6r9b0++Xs0vwJGUyJGg5a2hVtYnTcPp4ZfPZP8U1XI3sEaVr7BKy44sN4aFRUcOg8E5BVsXJdZQZnWxm0ZPFRazyGL0Ki6Vi0FchpZ1zlqjR15y8GrdZqd2Y4TqYp6gotvPdSH9uirPRDJTPvAvemo491EoPQo83odCDE2MoYu6dm2zNJWc0/ac6sPCt2WR5p9gibTkyjpzW9t+d8YVbjszXSecM+gi5WIBVg98flw/RVhsNg6kxqQ9EqyZXvYxXBCPoygWjJRlC8ETyeMkQy9Cw3t1nUCeFjrpJlWQMuavMa79tLT0anjYYbbl9k/j73i5lG4tmSpCFqgC+WGIzCHDKm5+uLU8MwAzwlFOZ11b2q/rR8Mf/eYczGtKwgvq8HBPx+QFbc3imAYQVhx1Jf2nvcMSD+2x17L+PBoRhvaTRmgcS3+iiB2FBI99OT3qbuIIGsG5X168kbFQH3spxYHUa2Yuik2izLDk+Mki1abBRAyC0cK47EDEtRSc8qp6BbHu4wd2YFYuZ7kYkVcoeB2aSzpKkzVQ3cNy5RU0ovTVxz4asAHUJ0kAzvX17MVsMjQ99rAN0q3WIJufuXAiY8UcSvInRxGIcnPiueETdldin8Cx5ww1yORCHRd41tYEHsGld2nKd2TaE5mGmHiYzFKKqnPFnR8ckY/B7VDslP5HdUkX6V7/aoyKMzh6X99J0PDU51A0dq0aWn6O7J2bBAShj+rjqPT1hljqGoQ37BDDhwD5ab/0Ps2JrrteOiCJbS/KyAFbZ9p6UF7SQZTFzLqaHqZVn0Qz1vgj7PhlSgvBPfGblX5GLUQzAvE8bhh9Xm2RUFTwbwem9rMXJT5hT59GdNXCPmHPpDnSBs0JCi4fB0LVLQgvpnUewkhVVgPA3v6YWBK3JdU3kb6no561XwJ5u0H+TEgXS3hL1qxnnDKlnMVgbf+DG4P0GU0ManBNNM6deXmUks5/DgO4xM2W5EWbCO0+qmGre+c9c+WBt8eflMI+HPjSIcdWeyUauO76+6tesHzIEwTTGYAkMB4KA581Ct5LTYuzv2SA2PS16VflU8mlcn2mya0sDBWwQWmyxct73Dn8NQk9OcZuk9hbBDGjIEl8wHZ161zxhexR4fU51/yDtaGx+E6usezdPVceX8GRNXoLPWWjyCcUeJ19Zax6eL8/nMr70vL03u3nNGeiBFOL4rg5EHSENVFARTAJU2gYZFo6WauXd9N711W2WST5JXOA==")
from spire.presentation.common import * 
from pathlib import Path
from openai import OpenAI
import tempfile
import time
from openai import RateLimitError, AuthenticationError
import json
from django.core.cache import cache
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

def get_catalog_tree(catalogs, parent=None, level=0):
    tree = []
    for catalog in catalogs:
        if catalog.parent_id == parent:
            indent = '&nbsp;' * level * 4  # 生成缩进字符串
            tree.append((catalog, indent))
            tree.extend(get_catalog_tree(catalogs, catalog.id, level + 1))
    return tree

def catalog_list_view(request):
    catalogs = TyPptCatalog.objects.all().order_by('label')
    catalog_tree = get_catalog_tree(catalogs)
    return render(request, 'catalog_list.html', {'catalog_tree': catalog_tree})

def delete_catalog_view(request, catalog_id):
    catalog = get_object_or_404(TyPptCatalog, id=catalog_id)

    # 递归删除目录及其所有子目录和文件
    def delete_directory(catalog):
        folder_path = catalog.path
        children = catalog.children.all()
        
        # 删除子目录
        for child in children:
            delete_directory(child)
        
        # 删除文件夹中的文件
        files = TyPptMain.objects.filter(catalog=catalog.id)
        for file in files:
            file_path = file.path
            if os.path.exists(file_path):
                os.remove(file_path)
            file.delete()

        # 删除文件系统中的文件夹
        if os.path.exists(folder_path):
            try:
                os.rmdir(folder_path)  # os.rmdir 仅在文件夹为空时删除
            except OSError:
                shutil.rmtree(folder_path)  # 使用 shutil.rmtree 递归删除

        # 删除数据库记录
        catalog.delete()
    
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

        # 更新子文件夹和PPT文件的路径信息
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
                    return HttpResponse(f'Error moving child folder {child.label}: {e}', status=500)

        update_children_paths(catalog, new_path)

        # 更新该文件夹及其子文件夹下所有PPT文件的路径信息
        def update_ppt_paths(catalog, new_path):
            ppts = TyPptMain.objects.filter(catalog=catalog.id)
            for ppt in ppts:
                old_ppt_path = ppt.path
                new_ppt_path = os.path.join(new_path, ppt.name)
                try:
                    if os.path.exists(old_ppt_path):
                        shutil.move(old_ppt_path, new_ppt_path)
                    ppt.path = new_ppt_path
                    ppt.save()
                except OSError as e:
                    return HttpResponse(f'Error moving PPT file {ppt.name}: {e}', status=500)

            for child in catalog.children.all():
                update_ppt_paths(child, os.path.join(new_path, child.label))

        update_ppt_paths(catalog, new_path)

        return redirect('catalog_list')
    else:
        return redirect('catalog_list')
    


def import_ppt_view(request):
    if request.method == 'POST':
        ppt_file = request.FILES['ppt_file']
        title = request.POST['title']
        lable = request.POST['lable']
        target_folder_id = request.POST['target_folder']

        target_folder = TyPptCatalog.objects.get(id=target_folder_id)
        target_path = target_folder.path

        # 将标签转换为逗号分隔的字符串格式
        lable_list = [label.strip() for label in lable.split(',')]
        lable_str = ','.join(lable_list)

        fs = FileSystemStorage(location=target_path)
        filename = fs.save(ppt_file.name, ppt_file)
        file_path = fs.path(filename)

        ppt_main = TyPptMain.objects.create(
            id=uuid.uuid4(),
            title=title,
            lable=lable_str,  # 使用转换后的标签字符串
            catalog=target_folder.id,
            name=ppt_file.name,
            type=ppt_file.name.split('.')[-1],
            size=ppt_file.size,
            path=file_path
        )

        return redirect('ppt_list')
    return redirect('ppt_list')


def get_catalog_tree(catalogs, parent=None, level=0):
    tree = []
    for catalog in catalogs:
        if catalog.parent_id == parent:
            indent = '&nbsp;' * level * 4  # 生成缩进字符串
            tree.append((catalog, indent))
            tree.extend(get_catalog_tree(catalogs, catalog.id, level + 1))
    return tree

def ppt_list_view(request):
    catalogs = TyPptCatalog.objects.all()
    catalog_tree = get_catalog_tree(catalogs)
    return render(request, 'ppt_list.html', {'catalog_tree': catalog_tree})

def catalog_detail_view(request, catalog_id):
    catalog = get_object_or_404(TyPptCatalog, id=catalog_id)
    ppts = TyPptMain.objects.filter(catalog=catalog_id)
    catalogs = TyPptCatalog.objects.all()
    catalog_tree = get_catalog_tree(catalogs)
    return render(request, 'ppt_list.html', {
        'catalogs': catalogs,
        'catalog_tree': catalog_tree,
        'ppts': ppts,
        'selected_catalog': catalog
    })

def delete_ppt_view(request):
    if request.method == 'POST':
        ppt_id = request.POST.get('ppt_id')
        ppt = get_object_or_404(TyPptMain, id=ppt_id)

        # 删除文件
        if os.path.exists(ppt.path):
            os.remove(ppt.path)

        # 获取父目录 ID，以便重定向时使用
        catalog_id = ppt.catalog

        # 删除数据库中的记录
        ppt.delete()

        return redirect('catalog_detail', catalog_id=catalog_id)
    
def move_ppt_view(request):
    if request.method == 'POST':
        ppt_id = request.POST.get('ppt_id')
        target_folder_id = request.POST.get('target_folder')

        ppt = get_object_or_404(TyPptMain, id=ppt_id)
        target_folder = get_object_or_404(TyPptCatalog, id=target_folder_id)

        old_path = ppt.path
        new_path = os.path.join(target_folder.path, os.path.basename(old_path))

        # 移动文件
        try:
            shutil.move(old_path, new_path)
        except Exception as e:
            return HttpResponse(f'移动失败: {e}', status=500)

        # 更新数据库记录
        ppt.path = new_path
        ppt.catalog = target_folder.id  # 只需要将目标文件夹的ID赋值给catalog字段
        ppt.save()

        return redirect('catalog_detail', catalog_id=ppt.catalog)
    
def edit_ppt_view(request):
    if request.method == 'POST':
        ppt_id = request.POST.get('ppt_id')
        new_title = request.POST.get('title')
        new_label = request.POST.get('label')
        new_name = request.POST.get('name')

        ppt = get_object_or_404(TyPptMain, id=ppt_id)
        old_path = ppt.path
        new_path = os.path.join(os.path.dirname(old_path), new_name)

        # 更新文件名
        if new_name != ppt.name:
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                return HttpResponse(f'重命名失败: {e}', status=500)

        # 更新数据库记录
        ppt.title = new_title
        ppt.lable = new_label  # 确保这里是正确的字段名，如果数据库字段名为`label`，请修改为`label`
        ppt.name = new_name
        ppt.path = new_path
        ppt.save()

        return redirect('catalog_detail', catalog_id=ppt.catalog)
    else:
        return redirect('ppt_list')


def split_ppt_view(request):
    if request.method == 'POST':
        ppt_id = request.POST.get('ppt_id')
        ppt = get_object_or_404(TyPptMain, id=ppt_id)

        file_path = ppt.path
        folder_path = os.path.dirname(file_path)
        output_folder_name = f"{os.path.splitext(ppt.name)[0]}_Single_Page"
        output_folder_path = os.path.join(folder_path, output_folder_name)
        os.makedirs(output_folder_path, exist_ok=True)

        presentation = Presentation()
        presentation.LoadFromFile(file_path)
        slide_count = len(presentation.Slides)

        parent_catalog = get_object_or_404(TyPptCatalog, id=ppt.catalog)

        catalog = TyPptCatalog.objects.create(
            label=output_folder_name,
            path=output_folder_path,
            parent_id=parent_catalog.id
        )

        client = OpenAI(
            api_key = "sk-qwEg1ba3qj8JNsUtErVmlDefkK9uRbW60MyEPHeO1d4Lt67y",
            base_url = "https://api.moonshot.cn/v1",
        )

        channel_layer = get_channel_layer()
        cache.set(f"split_progress_{ppt_id}", {'current_page': 0, 'total_pages': slide_count, 'ppt_name': ppt.name})

        for i in range(slide_count):
            slide_filename = f"{output_folder_name}_slide{i + 1}.pptx"
            output_file_path = os.path.join(output_folder_path, slide_filename)
            
            # 创建单页的PPT文件
            new_presentation = Presentation()
            new_slide = presentation.Slides[i]
           

            # 保存为临时PDF文件
            temp_pdf_fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
            os.close(temp_pdf_fd)
            new_slide.SaveToFile(temp_pdf_path, FileFormat.PDF)

            # 使用临时PDF文件内容生成标题
            try:
                title, lable = generate_title_from_pdf(client, temp_pdf_path)
            except AuthenticationError:
                return HttpResponse('Invalid Authentication', status=401)
            except RateLimitError:
                return HttpResponse('Rate limit reached. Please try again later.', status=429)

            # 保存当前幻灯片到文件
            new_slide.SaveToFile(output_file_path, FileFormat.Pptx2019)
            new_presentation.Dispose()

            # 保存拆分出来的PPT文件信息到数据库
            TyPptMain.objects.create(
                title=title,
                lable=lable,
                catalog=catalog.id,
                name=slide_filename,
                type="pptx",
                size=os.path.getsize(output_file_path),
                path=output_file_path
            )

            # 更新进度
            progress_data = {'current_page': i + 1, 'total_pages': slide_count, 'ppt_name': ppt.name}
            cache.set(f"split_progress_{ppt_id}", progress_data)
            async_to_sync(channel_layer.group_send)(
                f'progress_{ppt_id}',
                {
                    'type': 'progress_update',
                    'message': progress_data
                }
            )
            print(f'Sent progress update: {progress_data}') # Add this line to log the progress update

            # 删除临时PDF文件
            os.remove(temp_pdf_path)
            time.sleep(30)
        presentation.Dispose()

        # 删除进度缓存
        cache.delete(f"split_progress_{ppt_id}")

        return redirect('catalog_detail', catalog_id=ppt.catalog)

def split_progress_view(request):
    ppt_id = request.GET.get('ppt_id')
    progress = cache.get(f"split_progress_{ppt_id}", {'current_page': 0, 'total_pages': 0, 'ppt_name': '无任务'})
    return JsonResponse(progress)

def generate_title_from_pdf(client, temp_pdf_path):
    file_object = client.files.create(file=Path(temp_pdf_path), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text
    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {"role": "system", "content": file_content},
        {"role": "user", "content": "根据我上传的文件起一个10个字以内的名字，同时给5个描述内容的标签，注意要精简、准确，请不要自己过度解读，不要添加文件中不存在的内容。要求你回复内容，他们之间用逗号隔开，不要换行，不要有其它内容，请注意，一个名字，五个标签,数量要正确,返回Json格式"},
    ]

    retries = 3
    for i in range(retries):
        try:
            completion = client.chat.completions.create(model="moonshot-v1-32k", messages=messages, temperature=0.3)
            title_and_lable = completion.choices[0].message.content.strip()
            parsed_data = json.loads(title_and_lable)  
            title = parsed_data["name"]
            lables = parsed_data["tags"]
            lables_str = ",".join(lables)
            return title,lables_str
        except RateLimitError:
            if i < retries - 1:
                time.sleep(2 ** (i + 1))
            else:
                raise