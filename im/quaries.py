from django.db.models import Sum, F, Avg
from datetime import date
from .models import Sale, Inventory, WorkingDays, Product


def get_top_products_by_sales(n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date))
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products

def get_top_products_by_sales_manufacturer(manufacturer: str, n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date), product__manufacturer=manufacturer)
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products

def get_top_products_by_sales_category(category: str, n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date), product__category=category)
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products

def get_top_products_by_sales_subcategory(subcategory: str, n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date), product__subcategory=subcategory)
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products

def get_top_products_by_sales_region(region: str, n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date), region=region)
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products

def get_top_products_by_sales_client(client_type: str, n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date), client_type=client_type)
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products

def get_top_products_by_sales_manager(manager: str, n_top=10):
    start_date = date(2024, 1, 1)
    end_date   = date(2024, 12, 31)
    top_products = (
        Sale.objects.filter(sale_date__range=(start_date, end_date), manager=manager)
        .values('product__id', 'product__sku', 'product__name_short')
        .annotate(
            #total_sales_volume=Sum(F('quantity') * F('product__volume'))  # Multiply quantity by product volume
            total_sales_volume=Sum('sale_value')  # Multiply quantity by product volume
        )
        .order_by('-total_sales_volume')[:n_top]  # Order by total sales volume
    )
    return top_products


def get_product_sales(product, year, month=0):
    if month != 0:
        # Aggregate total sales across all stores
        total_sales = Sale.objects.filter(
            product=product,
            sale_date__year=year,
            sale_date__month=month
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0

        # Aggregate total sales for Novosibirsk
        total_sales_nsk = Sale.objects.filter(
            product=product,
            store__location="novosibirsk",
            sale_date__year=year,
            sale_date__month=month
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0

        # Aggregate total sales for Kemerovo
        total_sales_kem = Sale.objects.filter(
            product=product,
            store__location="kemerovo",
            sale_date__year=year,
            sale_date__month=month
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
    else:
        # Aggregate total sales across all stores
        total_sales = Sale.objects.filter(
            product=product,
            sale_date__year=year,
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0

        # Aggregate total sales for Novosibirsk
        total_sales_nsk = Sale.objects.filter(
            product=product,
            store__location="novosibirsk",
            sale_date__year=year,
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0

        # Aggregate total sales for Kemerovo
        total_sales_kem = Sale.objects.filter(
            product=product,
            store__location="kemerovo",
            sale_date__year=year,
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0

    # Return results as a tuple
    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months(year):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}
    
    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        weight = product_weights.get(product_id, 0)
        
        weighted_sales = sales_quantity * weight
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months_by_manufacturer(year: int, manufacturer: str):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}


    
    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year, product__manufacturer=manufacturer)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        
        if manufacturer != "sct":
            weight = product_weights.get(product_id, 0) 
            weighted_sales = sales_quantity * weight
        else:
            weighted_sales = sales_quantity
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months_by_category(year: int, category: str):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}


    
    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year, product__category=category)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        
        if category in ['масла', 'химия', 'автожидкости']:
            weight = product_weights.get(product_id, 0) 
            weighted_sales = sales_quantity * weight
        else:
            weighted_sales = sales_quantity
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months_by_subcategory(year: int, subcategory: str):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}


    
    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year, product__subcategory=subcategory)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        
        if subcategory not in [
            'лампы', 'фильтры воздушные', 'фильтры для АКП', 'фильтры масляные', 
            'фильтры салонные', 'фильтры топливные', 'щётки',
            ]:
            weight = product_weights.get(product_id, 0) 
            weighted_sales = sales_quantity * weight
        else:
            weighted_sales = sales_quantity
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months_by_region(year: int, region: str):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}

    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year, region=region)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        
        weight = product_weights.get(product_id, 0) 
        weighted_sales = sales_quantity * weight
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months_by_client(year: int, client_type: str):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}

    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year, client_type=client_type)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        
        weight = product_weights.get(product_id, 0) 
        weighted_sales = sales_quantity * weight
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months_by_manager(year: int, manager: str):
    """
    Optimized function to calculate total sales across all months for all stores,
    Novosibirsk stores, and Kemerovo stores.
    """
    # Pre-fetch product weights into a dictionary for quick lookup
    product_weights = {product.id: product.weight for product in Product.objects.all()}

    # Fetch sales data grouped by month, product, and location
    sales_data = (
        Sale.objects.filter(sale_date__year=year, manager=manager)
        .values('sale_date__month', 'product', 'store__location')
        .annotate(total_sales_quantity=Sum('quantity'))
    )
    
    # Initialize monthly sales lists
    total_sales     = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_nsk = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    total_sales_kem = {'sales': [0] * 12, 'av_sales': [0] * 12 }
    
    # Process the aggregated sales data
    for sale in sales_data:        
        month = sale['sale_date__month'] - 1  # Convert month to zero-indexed
        product_id = sale['product']
        location = sale['store__location']
        sales_quantity = sale['total_sales_quantity'] or 0
        
        weight = product_weights.get(product_id, 0) 
        weighted_sales = sales_quantity * weight
        
        # Add to total sales for the month
        total_sales['sales'][month] += weighted_sales
        if location == 'novosibirsk':
            total_sales_nsk['sales'][month] += weighted_sales
        elif location == 'kemerovo':
            total_sales_kem['sales'][month] += weighted_sales
    
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))
        total_sales['av_sales'][i-1] = total_sales['sales'][i-1] / wd_in_month
        total_sales_nsk['av_sales'][i-1] = total_sales_nsk['sales'][i-1] / wd_in_month
        total_sales_kem['av_sales'][i-1] = total_sales_kem['sales'][i-1] / wd_in_month

    return total_sales, total_sales_nsk, total_sales_kem

def get_sales_all_months2(year):
    total_sales_list = []; total_sales_nsk_list = [];     total_sales_kem_list = []
    for i in range(1, 13):
        # Aggregate total sales across all stores
        sales_month = 0
        for product in Product.objects.all():
            total_sales = Sale.objects.filter(
                product=product,
                sale_date__year=year,
                sale_date__month=i,
            ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
            sales_month += total_sales * product.weight
        total_sales_list.append(sales_month * product.weight )

        # Novosibirsk sales across all stores
        sales_month = 0
        for product in Product.objects.all():
            total_sales = Sale.objects.filter(
                product=product,
                store__location='novosibirsk',
                sale_date__year=year,
                sale_date__month=i,
            ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
            sales_month += total_sales * product.weight
        total_sales_nsk_list.append(sales_month * product.weight )

        # Kemerovo sales across all stores
        sales_month = 0
        for product in Product.objects.all():
            total_sales = Sale.objects.filter(
                product=product,
                store__location='kemerovo',
                sale_date__year=year,
                sale_date__month=i,
            ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
            sales_month += total_sales * product.weight
        total_sales_kem_list.append(sales_month * product.weight )

    return total_sales_list, total_sales_nsk_list, total_sales_kem_list

def get_product_sales_all_months(product, year):
    total_sales_list = {'sales': [], 'av_sales': []}
    total_sales_nsk_list = {'sales': [], 'av_sales': []}
    total_sales_kem_list = {'sales': [], 'av_sales': []}
    for i in range(1, 13):
        wd_in_month = len(WorkingDays.objects.filter(date__month=i, date__year=year))

        # Aggregate total sales across all stores
        total_sales = Sale.objects.filter(
            product=product,
            sale_date__year=year,
            sale_date__month=i,
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
        total_sales_list['sales'].append(total_sales)
        total_sales_list['av_sales'].append(total_sales / wd_in_month)

        # Aggregate total sales for Novosibirsk
        total_sales_nsk = Sale.objects.filter(
            product=product,
            store__location="novosibirsk",
            sale_date__year=year,     
            sale_date__month=i,       
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
        total_sales_nsk_list['sales'].append(total_sales_nsk)
        total_sales_nsk_list['av_sales'].append(total_sales_nsk / wd_in_month)

        # Aggregate total sales for Kemerovo
        total_sales_kem = Sale.objects.filter(
            product=product,
            store__location="kemerovo",
            sale_date__year=year,
            sale_date__month=i,
        ).aggregate(total_sales_quantity=Sum('quantity'))['total_sales_quantity'] or 0
        total_sales_kem_list['sales'].append(total_sales_kem)    
        total_sales_kem_list['av_sales'].append(total_sales_kem / wd_in_month)

    # Return results as a tuple
    return total_sales_list, total_sales_nsk_list, total_sales_kem_list

def get_weighted_av_inventory_all_months(product, year: int) -> list:
    """
    Returns a list of weighted average inventory of a given product and year
    based on the working days and inventory levels.
    """
    av_inv_list_nsk = []; av_inv_list_kem = []; av_inv_list = []
    
    for month in range(1, 13):  # Loop through each month
        # Get all working days for the month
        working_days = list(WorkingDays.objects.filter(date__year=year, date__month=month).order_by('date').values_list('date', flat=True))
        
        # Get all inventory records for the month, sorted by date
        inventory_records_nsk_main = (
            Inventory.objects.filter(
                product=product,
                store__name='Novosibirsk Main',
                date__year=year,
                date__month=month,
            )
            .values('date')
            .annotate(avg_inventory=Sum('inventory_level'))
            .order_by('date')
        )
        inventory_records_nsk_reserve = (
            Inventory.objects.filter(
                product=product,
                store__name='Novosibirsk Reserve',
                date__year=year,
                date__month=month,
            )
            .values('date')
            .annotate(avg_inventory=Sum('inventory_level'))
            .order_by('date')
        )
        inventory_records_kem = (
            Inventory.objects.filter(
                product=product,
                store__name='Kemerovo Main',
                date__year=year,
                date__month=month,
            )
            .values('date')
            .annotate(avg_inventory=Sum('inventory_level'))
            .order_by('date')
        )
        
        # Map inventory records to their dates
        inventory_map_nsk_main =    {record['date']: record['avg_inventory'] for record in inventory_records_nsk_main}
        inventory_map_nsk_reserve = {record['date']: record['avg_inventory'] for record in inventory_records_nsk_reserve}
        inventory_map_kem = {record['date']: record['avg_inventory'] for record in inventory_records_kem}

        # Initialize variables for weighted average calculation
        total_weighted_inventory = 0
        total_days = len(working_days)
        
        # Novosibirsk Main
        current_inventory_level = 0
        last_inventory_date = None
        for day in working_days:
            if day in inventory_map_nsk_main:  # If there's an inventory record for this day
                current_inventory_level = inventory_map_nsk_main[day]
                last_inventory_date = day
            
            # Use the current inventory level for this day
            total_weighted_inventory += current_inventory_level
        
        # Novosibirsk Reserve
        current_inventory_level = 0
        for day in working_days:
            if day in inventory_map_nsk_reserve:  # If there's an inventory record for this day
                current_inventory_level = inventory_map_nsk_reserve[day]
                last_inventory_date = day
            
            # Use the current inventory level for this day
            total_weighted_inventory += current_inventory_level        

        # Calculate the weighted average for the month
        weighted_average = total_weighted_inventory / total_days if total_days > 0 else 0
        av_inv_list_nsk.append(weighted_average)

        # Kemerovo
        total_weighted_inventory_kem = 0
        current_inventory_level = 0
        for day in working_days:
            if day in inventory_map_kem:  # If there's an inventory record for this day
                current_inventory_level = inventory_map_kem[day]
                last_inventory_date = day
            
            # Use the current inventory level for this day
            total_weighted_inventory_kem += current_inventory_level        

        # Calculate the weighted average for the month
        weighted_average_kem = total_weighted_inventory_kem / total_days if total_days > 0 else 0
        av_inv_list_kem.append(weighted_average_kem)

        # total
        av_inv_list.append(weighted_average + weighted_average_kem)
    
    return av_inv_list, av_inv_list_nsk, av_inv_list_kem

def get_weighted_av_inventory_all_months_all_products(year: int) -> tuple:
    """
    Returns lists of weighted average inventory (total, Novosibirsk, and Kemerovo) 
    for all products for a given year based on working days and inventory levels.
    """
    from collections import defaultdict

    av_inv_list = []  # Total weighted average inventory
    av_inv_list_nsk = []  # Novosibirsk (Main + Reserve) weighted average inventory
    av_inv_list_kem = []  # Kemerovo weighted average inventory

    # Loop through each month
    for month in range(1, 13):
        # Get all working days for the month
        working_days = list(
            WorkingDays.objects.filter(date__year=year, date__month=month)
            .order_by("date")
            .values_list("date", flat=True)
        )

        # Fetch inventory records for all relevant stores
        inventory_records = Inventory.objects.filter(
            date__year=year, date__month=month
        ).values("store__name", "date").annotate(avg_inventory=Sum("inventory_level"))

        # Group inventory records by store
        inventory_map = defaultdict(dict)
        for record in inventory_records:
            inventory_map[record["store__name"]][record["date"]] = record["avg_inventory"]

        # Stores to process
        stores = {
            "Novosibirsk Main": {"total": 0, "current_level": 0},
            "Novosibirsk Reserve": {"total": 0, "current_level": 0},
            "Kemerovo Main": {"total": 0, "current_level": 0},
        }

        total_days = len(working_days)

        # Process inventory for each working day
        for day in working_days:
            for store_name, store_data in stores.items():
                if day in inventory_map[store_name]:
                    store_data["current_level"] = inventory_map[store_name][day]
                store_data["total"] += store_data["current_level"]

        # Calculate weighted averages for each store
        weighted_nsk_main = stores["Novosibirsk Main"]["total"] / total_days if total_days > 0 else 0
        weighted_nsk_reserve = stores["Novosibirsk Reserve"]["total"] / total_days if total_days > 0 else 0
        weighted_kem = stores["Kemerovo Main"]["total"] / total_days if total_days > 0 else 0

        # Append results
        av_inv_list_nsk.append(weighted_nsk_main + weighted_nsk_reserve)
        av_inv_list_kem.append(weighted_kem)
        av_inv_list.append(weighted_nsk_main + weighted_nsk_reserve + weighted_kem)

    return av_inv_list, av_inv_list_nsk, av_inv_list_kem

def get_weighted_av_inventory_all_months_all_products_by_manufacturer(year: int, manufacturer: str) -> tuple:
    """
    Returns lists of weighted average inventory (total, Novosibirsk, and Kemerovo) 
    for all products for a given year based on working days and inventory levels.
    """
    from collections import defaultdict

    av_inv_list = []  # Total weighted average inventory
    av_inv_list_nsk = []  # Novosibirsk (Main + Reserve) weighted average inventory
    av_inv_list_kem = []  # Kemerovo weighted average inventory

    # Loop through each month
    for month in range(1, 13):
        # Get all working days for the month
        working_days = list(
            WorkingDays.objects.filter(date__year=year, date__month=month)
            .order_by("date")
            .values_list("date", flat=True)
        )

        # Fetch inventory records for all relevant stores
        inventory_records = Inventory.objects.filter(
            date__year=year, date__month=month, product__manufacturer=manufacturer
        ).values("store__name", "date").annotate(avg_inventory=Sum("inventory_level"))

        # Group inventory records by store
        inventory_map = defaultdict(dict)
        for record in inventory_records:
            inventory_map[record["store__name"]][record["date"]] = record["avg_inventory"]

        # Stores to process
        stores = {
            "Novosibirsk Main": {"total": 0, "current_level": 0},
            "Novosibirsk Reserve": {"total": 0, "current_level": 0},
            "Kemerovo Main": {"total": 0, "current_level": 0},
        }

        total_days = len(working_days)

        # Process inventory for each working day
        for day in working_days:
            for store_name, store_data in stores.items():
                if day in inventory_map[store_name]:
                    store_data["current_level"] = inventory_map[store_name][day]
                store_data["total"] += store_data["current_level"]

        # Calculate weighted averages for each store
        weighted_nsk_main = stores["Novosibirsk Main"]["total"] / total_days if total_days > 0 else 0
        weighted_nsk_reserve = stores["Novosibirsk Reserve"]["total"] / total_days if total_days > 0 else 0
        weighted_kem = stores["Kemerovo Main"]["total"] / total_days if total_days > 0 else 0

        # Append results
        av_inv_list_nsk.append(weighted_nsk_main + weighted_nsk_reserve)
        av_inv_list_kem.append(weighted_kem)
        av_inv_list.append(weighted_nsk_main + weighted_nsk_reserve + weighted_kem)

    return av_inv_list, av_inv_list_nsk, av_inv_list_kem

def get_weighted_av_inventory_all_months_all_products_by_category(year: int, category: str) -> tuple:
    """
    Returns lists of weighted average inventory (total, Novosibirsk, and Kemerovo) 
    for all products for a given year based on working days and inventory levels.
    """
    from collections import defaultdict

    av_inv_list = []  # Total weighted average inventory
    av_inv_list_nsk = []  # Novosibirsk (Main + Reserve) weighted average inventory
    av_inv_list_kem = []  # Kemerovo weighted average inventory

    # Loop through each month
    for month in range(1, 13):
        # Get all working days for the month
        working_days = list(
            WorkingDays.objects.filter(date__year=year, date__month=month)
            .order_by("date")
            .values_list("date", flat=True)
        )

        # Fetch inventory records for all relevant stores
        inventory_records = Inventory.objects.filter(
            date__year=year, date__month=month, product__category=category
        ).values("store__name", "date").annotate(avg_inventory=Sum("inventory_level"))

        # Group inventory records by store
        inventory_map = defaultdict(dict)
        for record in inventory_records:
            inventory_map[record["store__name"]][record["date"]] = record["avg_inventory"]

        # Stores to process
        stores = {
            "Novosibirsk Main": {"total": 0, "current_level": 0},
            "Novosibirsk Reserve": {"total": 0, "current_level": 0},
            "Kemerovo Main": {"total": 0, "current_level": 0},
        }

        total_days = len(working_days)

        # Process inventory for each working day
        for day in working_days:
            for store_name, store_data in stores.items():
                if day in inventory_map[store_name]:
                    store_data["current_level"] = inventory_map[store_name][day]
                store_data["total"] += store_data["current_level"]

        # Calculate weighted averages for each store
        weighted_nsk_main = stores["Novosibirsk Main"]["total"] / total_days if total_days > 0 else 0
        weighted_nsk_reserve = stores["Novosibirsk Reserve"]["total"] / total_days if total_days > 0 else 0
        weighted_kem = stores["Kemerovo Main"]["total"] / total_days if total_days > 0 else 0

        # Append results
        av_inv_list_nsk.append(weighted_nsk_main + weighted_nsk_reserve)
        av_inv_list_kem.append(weighted_kem)
        av_inv_list.append(weighted_nsk_main + weighted_nsk_reserve + weighted_kem)

    return av_inv_list, av_inv_list_nsk, av_inv_list_kem

def get_weighted_av_inventory_all_months_all_products_by_subcategory(year: int, subcategory: str) -> tuple:
    """
    Returns lists of weighted average inventory (total, Novosibirsk, and Kemerovo) 
    for all products for a given year based on working days and inventory levels.
    """
    from collections import defaultdict

    av_inv_list = []  # Total weighted average inventory
    av_inv_list_nsk = []  # Novosibirsk (Main + Reserve) weighted average inventory
    av_inv_list_kem = []  # Kemerovo weighted average inventory

    # Loop through each month
    for month in range(1, 13):
        # Get all working days for the month
        working_days = list(
            WorkingDays.objects.filter(date__year=year, date__month=month)
            .order_by("date")
            .values_list("date", flat=True)
        )

        # Fetch inventory records for all relevant stores
        inventory_records = Inventory.objects.filter(
            date__year=year, date__month=month, product__subcategory=subcategory
        ).values("store__name", "date").annotate(avg_inventory=Sum("inventory_level"))

        # Group inventory records by store
        inventory_map = defaultdict(dict)
        for record in inventory_records:
            inventory_map[record["store__name"]][record["date"]] = record["avg_inventory"]

        # Stores to process
        stores = {
            "Novosibirsk Main": {"total": 0, "current_level": 0},
            "Novosibirsk Reserve": {"total": 0, "current_level": 0},
            "Kemerovo Main": {"total": 0, "current_level": 0},
        }

        total_days = len(working_days)

        # Process inventory for each working day
        for day in working_days:
            for store_name, store_data in stores.items():
                if day in inventory_map[store_name]:
                    store_data["current_level"] = inventory_map[store_name][day]
                store_data["total"] += store_data["current_level"]

        # Calculate weighted averages for each store
        weighted_nsk_main = stores["Novosibirsk Main"]["total"] / total_days if total_days > 0 else 0
        weighted_nsk_reserve = stores["Novosibirsk Reserve"]["total"] / total_days if total_days > 0 else 0
        weighted_kem = stores["Kemerovo Main"]["total"] / total_days if total_days > 0 else 0

        # Append results
        av_inv_list_nsk.append(weighted_nsk_main + weighted_nsk_reserve)
        av_inv_list_kem.append(weighted_kem)
        av_inv_list.append(weighted_nsk_main + weighted_nsk_reserve + weighted_kem)

    return av_inv_list, av_inv_list_nsk, av_inv_list_kem
