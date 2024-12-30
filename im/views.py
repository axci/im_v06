from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout


from io import BytesIO
from datetime import datetime
import pandas as pd
import tempfile
import os
from itertools import accumulate


from .models import Product, Store, Sale, Inventory, WorkingDays
from .forms import ExcelUploadForm, ExcelUploadSaleForm, ExcelUploadInventoryForm, ExcelUploadWorkingDaysForm
from .utils import DemandGenerator  # Adjust import if DemandGenerator is in a different location
from .utils_stat import calculate_sales_statistics, calculate_sales_global_statistics
from .utils_place_order import place_order
from .quaries import (
    get_top_products_by_sales, get_product_sales, get_product_sales_all_months, get_weighted_av_inventory_all_months,
    get_sales_all_months, get_weighted_av_inventory_all_months_all_products, get_sales_all_months_by_manufacturer, 
    get_weighted_av_inventory_all_months_all_products_by_manufacturer, 
    get_weighted_av_inventory_all_months_all_products_by_category, get_sales_all_months_by_category,
    get_sales_all_months_by_subcategory, get_weighted_av_inventory_all_months_all_products_by_subcategory,
    get_top_products_by_sales_manufacturer, get_top_products_by_sales_category, get_top_products_by_sales_subcategory,
    get_sales_all_months_by_region, get_top_products_by_sales_region,
    get_sales_all_months_by_client, get_top_products_by_sales_client,
    get_sales_all_months_by_manager, get_top_products_by_sales_manager,
    )
from .utils_seasonality import test_seasonality
from .process_excel import make_flat_table, make_flat_table_inv


def file_iterator(data, chunk_size=512):
    for i in range(0, len(data), chunk_size):
        yield data[i:i+chunk_size]

def homepage(request):
    today = str(datetime.today().date())
    products_form  = ExcelUploadForm()
    sales_form     = ExcelUploadSaleForm()
    inventory_form = ExcelUploadInventoryForm()
    wd_form        = ExcelUploadWorkingDaysForm()
    if request.method == "POST":
        if 'upload_products' in request.POST:
            products_form = ExcelUploadForm(request.POST, request.FILES)
            if products_form.is_valid():
                file = request.FILES['file']
                try:
                    df = pd.read_excel(file, engine='openpyxl')                
                    for _, row in df.iterrows():
                        Product.objects.create(
                            sku=row['SKU'],
                            name=row['name'],
                            name_short=row['name_short'],
                            weight=row['weight'],
                            volume=row['volume'],
                            order_pack=row['order_pack'],
                            manufacturer=row['manufacturer'],
                            category=row['category'],
                            subcategory=row['subcategory'],
                        )
                        messages.success(request, f"{row['SKU']} uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
        elif 'upload_sales' in request.POST:
            sales_form = ExcelUploadSaleForm(request.POST, request.FILES)
            if sales_form.is_valid():
                file = request.FILES['file']
                try:
                    data = pd.read_excel(file, engine='openpyxl')                
                    df = make_flat_table(data)
                    for _, row in df.iterrows():
                        try:
                            product = Product.objects.get(sku=row['SKU'])
                            store = Store.objects.get(name=row['store'])
                        except Product.DoesNotExist:
                            messages.error(request, f"Product with SKU {row['SKU']} not found.")
                            continue
                        Sale.objects.create(
                            product=product,
                            store=store,
                            quantity=row['quantity'],
                            sale_date=row['sale_date'],                            
                            cost=row['cost'],                            
                            sale_value=row['sale_value'],                            
                            client_type=row['client_type'],                            
                            region=row['region'],                            
                            manager=row['manager'],                            
                        )
                    messages.success(request, "Sales data uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
        elif 'upload_inventory' in request.POST:
            inventory_form = ExcelUploadInventoryForm(request.POST, request.FILES)
            if inventory_form.is_valid():
                file = request.FILES['file']
                try:
                    data = pd.read_excel(file, engine='openpyxl')                
                    df = make_flat_table_inv(data)
                    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date

                    for _, row in df.iterrows():
                        try:
                            product = Product.objects.get(sku=row['SKU'])
                            store = Store.objects.get(name=row['store'])
                        except Product.DoesNotExist:
                            messages.error(request, f"Product with SKU {row['SKU']} not found.")
                            continue
                        Inventory.objects.create(
                            product=product,
                            store=store,
                            inventory_level=row['end'],
                            date=row['date'],                            
                        )
                    messages.success(request, "Inventory data uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
        elif 'upload_working_days' in request.POST:
            wd_form = ExcelUploadWorkingDaysForm(request.POST, request.FILES)
            if wd_form.is_valid():
                file = request.FILES['file']
                try:
                    data = pd.read_excel(file, engine='openpyxl')                
                    for _, row in data.iterrows():                    
                        WorkingDays.objects.create(  
                            date=row['date'],                            
                        )
                    messages.success(request, "Working days uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")

        if 'place_order' in request.POST:
            selected_months = [(2024, 10), (2024, 11), (2024, 12)]  # Replace as needed
            df, df_nsk, df_kem = place_order(selected_months)

            # Create an Excel file with multiple sheets
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='All Orders', index=False)
                df_nsk.to_excel(writer, sheet_name='Novosibirsk', index=False)
                df_kem.to_excel(writer, sheet_name='Kemerovo', index=False)
            output.seek(0)

            # Return the Excel file as an HTTP response
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="orders_{today}.xlsx"'
            return response    
    else:
        form = ExcelUploadForm()
    
    top_products = get_top_products_by_sales(n_top=12)

    context = {
        'products_form': products_form, 
        'sales_form': sales_form,
        'inventory_form': inventory_form,
        'wd_form': wd_form,
        'top_products': top_products,
        }
    return render(request, 'im/index.html', context)

def homepage_rus(request):          
    
    top_products = get_top_products_by_sales(n_top=12)

    context = {
        'top_products': top_products,
        }
    return render(request, 'im/index_rus.html', context)

def sales(request):
    months = 12
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months(year=2024)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months(year=2023)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total; dif_perc = (sales24_total / sales23_total - 1) * 100
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total; dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    dif_abs_kem = sales_kem24_total - sales_kem23_total; dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months_all_products(year=2024)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    inv_sales_ratio24 = [a / b for a, b in zip(inv24, sales24['sales'])]
    inv_sales_nsk_ratio24 = [a / b for a, b in zip(inv_nsk24, sales_nsk24['sales'])]
    inv_sales_kem_ratio24 = [a / b for a, b in zip(inv_kem24, sales_kem24['sales'])]
    li = [1, 2, 3]

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'inv_sales_ratio24': inv_sales_ratio24, 'inv_sales_nsk_ratio24': inv_sales_nsk_ratio24, 'inv_sales_kem_ratio24': inv_sales_kem_ratio24,
        'li': li,
    }
    return render(request, 'im/sales.html', context)

def sales_rus(request):
    months = 12    
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months(year=2024)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months(year=2023)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total; dif_perc = (sales24_total / sales23_total - 1) * 100
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total; dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    dif_abs_kem = sales_kem24_total - sales_kem23_total; dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months_all_products(year=2024)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    inv_sales_ratio24 = [a / b for a, b in zip(inv24, sales24['sales'])]
    inv_sales_nsk_ratio24 = [a / b for a, b in zip(inv_nsk24, sales_nsk24['sales'])]
    inv_sales_kem_ratio24 = [a / b for a, b in zip(inv_kem24, sales_kem24['sales'])]
    li = [1, 2, 3]

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'inv_sales_ratio24': inv_sales_ratio24, 'inv_sales_nsk_ratio24': inv_sales_nsk_ratio24, 'inv_sales_kem_ratio24': inv_sales_kem_ratio24,
        'li': li,
    }
    return render(request, 'im/sales_rus.html', context)

# Sales by Manufacturer
def sales_man_rus(request, manufacturer):
    months = 12    
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months_by_manufacturer(year=2024, manufacturer=manufacturer)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months_by_manufacturer(year=2023, manufacturer=manufacturer)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total
    if sales23_total != 0:
        dif_perc = (sales24_total / sales23_total - 1) * 100
    else:
        dif_perc = 0
    
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total
    if sales_nsk23_total != 0:
        dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    else:
        dif_perc_nsk = ''
    dif_abs_kem = sales_kem24_total - sales_kem23_total
    if sales_kem23_total != 0:
        dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    else:
        dif_perc_kem = 0
    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months_all_products_by_manufacturer(year=2024, manufacturer=manufacturer)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    li = [1, 2, 3]
    if manufacturer != 'sct':
        unit_of_measurement = 'кг'
    else:
        unit_of_measurement = 'шт'

    top_products = get_top_products_by_sales_manufacturer(manufacturer=manufacturer, n_top=8) 

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'li': li,
        'title': manufacturer, 'unit_of_measurement': unit_of_measurement, 'top_products': top_products,
    }
    return render(request, 'im/sales_man_rus.html', context)

# Sales by Category
def sales_cat_rus(request, category):
    months = 12
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months_by_category(year=2024, category=category)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months_by_category(year=2023, category=category)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total
    if sales23_total != 0:
        dif_perc = (sales24_total / sales23_total - 1) * 100
    else:
        dif_perc = 0
    
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total
    if sales_nsk23_total != 0:
        dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    else:
        dif_perc_nsk = ''
    dif_abs_kem = sales_kem24_total - sales_kem23_total
    if sales_kem23_total != 0:
        dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    else:
        dif_perc_kem = 0
    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months_all_products_by_category(year=2024, category=category)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    li = [1, 2, 3]
    if category  in ['масла', 'химия', 'автожидкости']:
        unit_of_measurement = 'кг'
    else:
        unit_of_measurement = 'шт'

    top_products = get_top_products_by_sales_category(category=category, n_top=8)

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'li': li,
        'title': category, 'unit_of_measurement': unit_of_measurement, 'top_products': top_products,
    }
    return render(request, 'im/sales_cat_rus.html', context)

# Sales by SubCategory
def sales_subcat_rus(request, subcategory):
    months = 12
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months_by_subcategory(year=2024, subcategory=subcategory)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months_by_subcategory(year=2023, subcategory=subcategory)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total
    if sales23_total != 0:
        dif_perc = (sales24_total / sales23_total - 1) * 100
    else:
        dif_perc = 0
    
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total
    if sales_nsk23_total != 0:
        dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    else:
        dif_perc_nsk = ''
    dif_abs_kem = sales_kem24_total - sales_kem23_total
    if sales_kem23_total != 0:
        dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    else:
        dif_perc_kem = 0
    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months_all_products_by_subcategory(year=2024, subcategory=subcategory)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    li = [1, 2, 3]
    if subcategory not in [
            'лампы', 'фильтры воздушные', 'фильтры для АКП', 'фильтры масляные', 
            'фильтры салонные', 'фильтры топливные', 'щётки',
            ]:
        unit_of_measurement = 'кг'
    else:
        unit_of_measurement = 'шт'

    top_products = get_top_products_by_sales_subcategory(subcategory=subcategory, n_top=8)

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'li': li,
        'title': subcategory, 'unit_of_measurement': unit_of_measurement, 'top_products': top_products,
    }
    return render(request, 'im/sales_subcat_rus.html', context)

# Sales by Region
def sales_region_rus(request, region):
    months = 12
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months_by_region(year=2024, region=region)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months_by_region(year=2023, region=region)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total
    if sales23_total != 0:
        dif_perc = (sales24_total / sales23_total - 1) * 100
    else:
        dif_perc = 0
    
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total
    if sales_nsk23_total != 0:
        dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    else:
        dif_perc_nsk = ''
    dif_abs_kem = sales_kem24_total - sales_kem23_total
    if sales_kem23_total != 0:
        dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    else:
        dif_perc_kem = 0
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']),  )
    li = [1, 2, 3]
    unit_of_measurement = 'кг'   

    top_products = get_top_products_by_sales_region(region=region, n_top=8)

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'max_y_in_store': max_y_in_store,
        'li': li,
        'title': region, 'unit_of_measurement': unit_of_measurement, 'top_products': top_products,
    }
    return render(request, 'im/sales_region_rus.html', context)

# Sales by Client Type
def sales_client_rus(request, client_type):
    months = 12
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months_by_client(year=2024, client_type=client_type)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months_by_client(year=2023, client_type=client_type)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total
    if sales23_total != 0:
        dif_perc = (sales24_total / sales23_total - 1) * 100
    else:
        dif_perc = 0
    
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total
    if sales_nsk23_total != 0:
        dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    else:
        dif_perc_nsk = ''
    dif_abs_kem = sales_kem24_total - sales_kem23_total
    if sales_kem23_total != 0:
        dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    else:
        dif_perc_kem = 0
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']),  )
    li = [1, 2, 3]
    unit_of_measurement = 'кг'   

    top_products = get_top_products_by_sales_client(client_type=client_type, n_top=8)

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'max_y_in_store': max_y_in_store,
        'li': li,
        'title': client_type, 'unit_of_measurement': unit_of_measurement, 'top_products': top_products,
    }
    return render(request, 'im/sales_client_rus.html', context)

# Sales by Manager
def sales_manager_rus(request, manager):
    months = 12
    sales24, sales_nsk24, sales_kem24 = get_sales_all_months_by_manager(year=2024, manager=manager)
    sales23, sales_nsk23, sales_kem23 = get_sales_all_months_by_manager(year=2023, manager=manager)
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 

    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])
    dif_abs = sales24_total - sales23_total
    if sales23_total != 0:
        dif_perc = (sales24_total / sales23_total - 1) * 100
    else:
        dif_perc = 0
    
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total
    if sales_nsk23_total != 0:
        dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100
    else:
        dif_perc_nsk = ''
    dif_abs_kem = sales_kem24_total - sales_kem23_total
    if sales_kem23_total != 0:
        dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100
    else:
        dif_perc_kem = 0
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']),  )
    li = [1, 2, 3]
    unit_of_measurement = 'кг'   

    top_products = get_top_products_by_sales_manager(manager=manager, n_top=8)

    context = {
        'sales24': sales24['sales'], 'sales_nsk24': sales_nsk24['sales'], 'sales_kem24': sales_kem24['sales'],
        'sales23': sales23['sales'], 'sales_nsk23': sales_nsk23['sales'], 'sales_kem23': sales_kem23['sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,

        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'max_y_in_store': max_y_in_store,
        'li': li,
        'title': manager, 'unit_of_measurement': unit_of_measurement, 'top_products': top_products,
    }
    return render(request, 'im/sales_manager_rus.html', context)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'im/product_list.html', {'products': products})
    
def product_detail_search(request):
    sku = request.GET.get('sku')  # Get the SKU from the query parameters
    if sku:
        try:
            # Try to find the product by SKU
            product = Product.objects.get(sku=sku)
            return redirect('im:product_detail_rus', id=product.id)  # Redirect to the product detail page
        except Product.DoesNotExist:
            # Render the search page with an error if SKU is not found
            return render(request, 'im/product_search.html', {
                'error': f'Товар с артикулом "{sku}" не найден.'
            })
    else:
        # Render the search page with a message if no SKU is entered
        return render(request, 'im/product_search.html', {
            'error': 'No SKU entered. Please provide an SKU to search.'
        })   
    
def product_detail(request, id):
    months = 11
    product = get_object_or_404(Product, id=id)
    sales, sales_nsk, sales_kem = get_product_sales(product, year=2024, month=11)    
    sales24, sales_nsk24, sales_kem24 = get_product_sales_all_months(product, year=2024, )
    sales23, sales_nsk23, sales_kem23 = get_product_sales_all_months(product, year=2023, )
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 
    
    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])

    dif_abs = sales24_total - sales23_total; dif_perc = (sales24_total / sales23_total - 1) * 100 if sales23_total > 0 else "-"
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total; dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100 if sales_nsk23_total > 0 else "-"
    dif_abs_kem = sales_kem24_total - sales_kem23_total; dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100 if sales_kem23_total > 0 else "-"

    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months(product, year=2024)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    # Inventory
    inv_sales_ratio24 = [a / b if b>0 else 0 for a, b in zip(inv24, sales24['sales'])]
    inv_sales_nsk_ratio24 = [a / b if b>0 else 0 for a, b in zip(inv_nsk24, sales_nsk24['sales'])]
    inv_sales_kem_ratio24 = [a / b if b>0 else 0 for a, b in zip(inv_kem24, sales_kem24['sales'])]
    
    # seasonality
    stat, p_value, seasonal_dec = test_seasonality(sales24['av_sales'], sales23['av_sales'])
    stat_nsk, p_value_nsk, seasonal_dec_nsk = test_seasonality(sales_nsk24['av_sales'], sales_nsk23['av_sales'])
    stat_kem, p_value_kem, seasonal_dec_kem = test_seasonality(sales_kem24['av_sales'], sales_kem23['av_sales'])
    p_values = [{"i": 1, "p_value": p_value_nsk}, {"i": 2, "p_value": p_value_kem}, {"i": 3, "p_value": p_value}]
    kruskal_stats = [{"i": 1, "kruskal": stat_nsk}, {"i": 2, "kruskal": stat_kem}, {"i": 3, "kruskal": stat}]

    li = [1, 2, 3]
    context = {
        'product': product,
        'sales': sales,
        'sales_nsk': sales_nsk,
        'sales_kem': sales_kem,
        'sales24': sales24['sales'],
        'sales24_avg': sales24['av_sales'],
        'sales_nsk24': sales_nsk24['sales'],
        'sales_nsk24_avg': sales_nsk24['av_sales'],
        'sales_kem24': sales_kem24['sales'],
        'sales_kem24_avg': sales_kem24['av_sales'],
        'sales23': sales23['sales'],
        'sales23_avg': sales23['av_sales'],
        'sales_nsk23': sales_nsk23['sales'],
        'sales_nsk23_avg': sales_nsk23['av_sales'],
        'sales_kem23': sales_kem23['sales'],
        'sales_kem23_avg': sales_kem23['av_sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,
        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'inv_sales_ratio24': inv_sales_ratio24, 'inv_sales_nsk_ratio24': inv_sales_nsk_ratio24, 'inv_sales_kem_ratio24': inv_sales_kem_ratio24,
        'kruskal_stats': kruskal_stats, 'p_values': p_values,
        'seasonal_dec': seasonal_dec, 'seasonal_dec_nsk': seasonal_dec_nsk, 'seasonal_dec_kem': seasonal_dec_kem,

        'li': li,
    }
    return render(request, 'im/product.html', context)

def product_detail_rus(request, id):
    months = 11
    product = get_object_or_404(Product, id=id)
    sales, sales_nsk, sales_kem = get_product_sales(product, year=2024, month=11)    
    sales24, sales_nsk24, sales_kem24 = get_product_sales_all_months(product, year=2024, )
    sales23, sales_nsk23, sales_kem23 = get_product_sales_all_months(product, year=2023, )
    sales24_cum = list(accumulate(sales24['sales'])); sales23_cum = list(accumulate(sales23['sales']))
    sales_nsk24_cum = list(accumulate(sales_nsk24['sales'])); sales_nsk23_cum = list(accumulate(sales_nsk23['sales'])); 
    sales_kem24_cum = list(accumulate(sales_kem24['sales'])); sales_kem23_cum = list(accumulate(sales_kem23['sales'])); 
    
    sales_nsk24_total = sum(sales_nsk24['sales'][:months]); sales_kem24_total = sum(sales_kem24['sales'][:months]); sales24_total = sum(sales24['sales'][:months])
    sales_nsk23_total = sum(sales_nsk23['sales'][:months]); sales_kem23_total = sum(sales_kem23['sales'][:months]); sales23_total = sum(sales23['sales'][:months])

    dif_abs = sales24_total - sales23_total; dif_perc = (sales24_total / sales23_total - 1) * 100 if sales23_total > 0 else "-"
    dif_abs_nsk = sales_nsk24_total - sales_nsk23_total; dif_perc_nsk = (sales_nsk24_total / sales_nsk23_total - 1) * 100 if sales_nsk23_total > 0 else "-"
    dif_abs_kem = sales_kem24_total - sales_kem23_total; dif_perc_kem = (sales_kem24_total / sales_kem23_total - 1) * 100 if sales_kem23_total > 0 else "-"

    inv24, inv_nsk24, inv_kem24 = get_weighted_av_inventory_all_months(product, year=2024)
    max_y_in_store = max(max(sales_nsk24['sales']), max(sales_nsk23['sales']), max(sales_kem24['sales']), max(sales_kem23['sales']), 
                        max(inv_nsk24), max(inv_kem24))
    # Inventory
    inv_sales_ratio24 = [a / b if b>0 else 0 for a, b in zip(inv24, sales24['sales'])]
    inv_sales_nsk_ratio24 = [a / b if b>0 else 0 for a, b in zip(inv_nsk24, sales_nsk24['sales'])]
    inv_sales_kem_ratio24 = [a / b if b>0 else 0 for a, b in zip(inv_kem24, sales_kem24['sales'])]

    li = [1, 2, 3]
    context = {
        'product': product,
        'sales': sales,
        'sales_nsk': sales_nsk,
        'sales_kem': sales_kem,
        'sales24': sales24['sales'],
        'sales24_avg': sales24['av_sales'],
        'sales_nsk24': sales_nsk24['sales'],
        'sales_nsk24_avg': sales_nsk24['av_sales'],
        'sales_kem24': sales_kem24['sales'],
        'sales_kem24_avg': sales_kem24['av_sales'],
        'sales23': sales23['sales'],
        'sales23_avg': sales23['av_sales'],
        'sales_nsk23': sales_nsk23['sales'],
        'sales_nsk23_avg': sales_nsk23['av_sales'],
        'sales_kem23': sales_kem23['sales'],
        'sales_kem23_avg': sales_kem23['av_sales'],
        'sales_nsk24_cum': sales_nsk24_cum, 'sales_nsk23_cum': sales_nsk23_cum,
        'sales_kem24_cum': sales_kem24_cum, 'sales_kem23_cum': sales_kem23_cum,
        'sales24_cum': sales24_cum, 'sales23_cum': sales23_cum,
        'sales_nsk24_total': sales_nsk24_total, 'sales_kem24_total': sales_kem24_total, 'sales24_total': sales24_total,
        'sales_nsk23_total': sales_nsk23_total, 'sales_kem23_total': sales_kem23_total, 'sales23_total': sales23_total,
        'dif_abs': dif_abs, 'dif_abs_nsk': dif_abs_nsk, 'dif_abs_kem': dif_abs_kem,
        'dif_perc': dif_perc, 'dif_perc_nsk': dif_perc_nsk, 'dif_perc_kem': dif_perc_kem,
        'inv24': inv24, 'inv_nsk24': inv_nsk24, 'inv_kem24': inv_kem24,
        'max_y_in_store': max_y_in_store,
        'inv_sales_ratio24': inv_sales_ratio24, 'inv_sales_nsk_ratio24': inv_sales_nsk_ratio24, 'inv_sales_kem_ratio24': inv_sales_kem_ratio24,
        'li': li,
    }
    return render(request, 'im/product_rus.html', context)

def store_list(request):
    stores = Store.objects.all()
    return render(request, 'im/store_list.html', {'stores': stores})

def simulate_demand(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)

        # Define generator arguments
        generator_args = {
            'distribution': 'normal',  # Or another supported distribution
            'mean': 50,               # Replace with product-specific logic if needed
            'std': 10,                # Replace with product-specific logic if needed
            'period_length': 200,
        }

        # Simulate demand
        generator = DemandGenerator(generator_args)
        demand = generator.simulate_demand()

        return JsonResponse({'demand': demand.tolist()})  # Convert NumPy array to list for JSON serialization

    return JsonResponse({'error': 'Invalid request'}, status=400)

def upload_excel(request):
    products_form  = ExcelUploadForm()
    sales_form     = ExcelUploadSaleForm()
    inventory_form = ExcelUploadInventoryForm()
    wd_form        = ExcelUploadWorkingDaysForm()
    if request.method == "POST":
        if 'upload_products' in request.POST:
            products_form = ExcelUploadForm(request.POST, request.FILES)
            if products_form.is_valid():
                file = request.FILES['file']
                try:
                    df = pd.read_excel(file, engine='openpyxl')                
                    for _, row in df.iterrows():
                        Product.objects.create(
                            sku=row['SKU'],
                            name=row['name'],
                            weight=row['weight'],
                            volume=row['volume'],
                            order_pack=row['order_pack'],
                            manufacturer=row['manufacturer'],
                        )
                        messages.success(request, f"{row['SKU']} uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
        elif 'upload_sales' in request.POST:
            sales_form = ExcelUploadSaleForm(request.POST, request.FILES)
            if sales_form.is_valid():
                file = request.FILES['file']
                try:
                    data = pd.read_excel(file, engine='openpyxl')                
                    df = make_flat_table(data)
                    for _, row in df.iterrows():
                        try:
                            product = Product.objects.get(sku=row['SKU'])
                            store = Store.objects.get(name=row['store'])
                        except Product.DoesNotExist:
                            messages.error(request, f"Product with SKU {row['SKU']} not found.")
                            continue
                        Sale.objects.create(
                            product=product,
                            store=store,
                            quantity=row['quantity'],
                            sale_date=row['sale_date'],                            
                        )
                    messages.success(request, "Sales data uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
        elif 'upload_inventory' in request.POST:
            inventory_form = ExcelUploadInventoryForm(request.POST, request.FILES)
            if inventory_form.is_valid():
                file = request.FILES['file']
                try:
                    data = pd.read_excel(file, engine='openpyxl')                
                    df = make_flat_table_inv(data)
                    for _, row in df.iterrows():
                        try:
                            product = Product.objects.get(sku=row['SKU'])
                            store = Store.objects.get(name=row['store'])
                        except Product.DoesNotExist:
                            messages.error(request, f"Product with SKU {row['SKU']} not found.")
                            continue
                        Inventory.objects.create(
                            product=product,
                            store=store,
                            inventory_level=row['end'],
                            date=row['date'],                            
                        )
                    messages.success(request, "Inventory data uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
        elif 'upload_working_days' in request.POST:
            wd_form = ExcelUploadWorkingDaysForm(request.POST, request.FILES)
            if wd_form.is_valid():
                file = request.FILES['file']
                try:
                    data = pd.read_excel(file, engine='openpyxl')                
                    for _, row in data.iterrows():                    
                        WorkingDays.objects.create(  
                            date=row['date'],                            
                        )
                    messages.success(request, "Working days uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
    else:
        form = ExcelUploadForm()
    
    context = {
        'products_form': products_form, 
        'sales_form': sales_form,
        'inventory_form': inventory_form,
        'wd_form': wd_form,
        }
    return render(request, 'im/upload_excel.html', context)

## UPDATE STATS
@csrf_exempt
def calculate_statistics_view(request):
    """
    View to trigger the calculation of sales statistics.
    """
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Validate input dates
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if start_date > end_date:
            return JsonResponse({'error': 'Start date must be earlier than end date.'}, status=400)

        # Trigger the statistics calculation
        statistics = calculate_sales_statistics(start_date, end_date)
        statistics_global = calculate_sales_global_statistics(start_date, end_date)

        return JsonResponse({'message': 'Statistics calculated successfully!', 'data': statistics, 'data_global': statistics_global})

    return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)

def calculate_statistics_form(request):
    """
    Render the form for calculating sales statistics.
    """
    return render(request, 'im/calculate_statistics.html')

def place_order_view(request):
    table_data = None  
    if request.method == 'POST':  # Triggered when the button is clicked
        # Example: Selected months can come from a form or be predefined
        selected_months = [(2024, 10), (2024, 11), (2024, 12)]  # Replace as needed
        
        # Call your function
        df = place_order(selected_months)
        table_data = df.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries

        # Save the Excel to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            temp_filename = tmp.name
            df.to_excel(temp_filename, index=False)
        
        # Serve the file as a download
        with open(temp_filename, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="order.xlsx"'
        os.remove(temp_filename)  # Clean up the temporary file
        return response
    
    # Render the page for GET request
    return render(request, 'im/place_order.html', {'table_data': table_data})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('im:homepage_rus')
    else:
        form = AuthenticationForm()
    return render(request, 'im/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('im:homepage_rus')

def custom_403_view(request):
    return render(request, 'im/403_forbidden.html', status=403)

