import pandas as pd
from datetime import datetime

from .models import Product
from im.utils_oracle import OracleAgent
from im.utils_stat import get_month_sales_by_location, calculate_sales_statistics, calculate_sales_global_statistics
from im.quaries import get_top_products_by_sales
import os
import pandas as pd
from datetime import datetime


def place_order(selected_months):
    """
    Place an order and save the results to an Excel file.

    Args:
        selected_months (list of tuple): List of (year, month) tuples for sales data inclusion.
                                         Example: [(2024, 10), (2024, 11)]

    Returns:
        pd.DataFrame: Order dataframe.
    """

    # Calculate Average day sales
    start_date = "2024-11-01"
    end_date   = "2024-12-16"
    statistics = calculate_sales_statistics(start_date, end_date)  # statistics[product.sku][store.name]['sales_mean'] = mean_sales
    calculate_sales_global_statistics(start_date, end_date)

    # Ensure output directory exists
    output_dir = "orders_excel"
    os.makedirs(output_dir, exist_ok=True)

    # Prepare date for filename
    date = datetime.today().strftime("%Y-%m-%d")

    # Initialize order dictionary
    order = {
        'sku': [],
        'name': [],
        'manufacturer': [],
        'item_weight': [],
        'order_nsk': [],
        'order_nsk_weight': [],
        'order_kem': [],
        'order_kem_weight': [],
        'inv_level': [],
        'inv_level_nsk': [],
        'inv_level_kem': [],
        # 'av_sales': [],
        'av_sales_nsk': [],
        'av_sales_kem': [],
    }

    # Add dynamic columns for selected months
    sales_columns = {}
    for year, month in selected_months:
        month_name = datetime(year, month, 1).strftime('%b').lower()  # e.g., "oct"
        sales_columns[f'sales_{month_name}'] = []
        sales_columns[f'sales_{month_name}_nsk'] = []
        sales_columns[f'sales_{month_name}_kem'] = []
    order.update(sales_columns)

    # Pre-fetch sales data for selected months
    sales_data_by_month = {
        (year, month): get_month_sales_by_location(year, month)
        for year, month in selected_months
    }

    # q =  get_top_products_by_sales(221)
    # skus = q.values_list('product__sku', flat=True)
    # mannol_products = Product.objects.filter(sku__in=skus)
    for product in Product.objects.all():
        agent = OracleAgent(product)
        actions = agent.get_actions()

        # Populate static product data
        order['sku'].append(product.sku)
        order['name'].append(product.name)
        order['manufacturer'].append(product.manufacturer)
        order['item_weight'].append(product.weight)

        # Calculate orders and weights
        order_nsk, order_kem = actions[0], actions[1]
        order['order_nsk'].append(order_nsk)
        order['order_kem'].append(order_kem)
        order['order_nsk_weight'].append(order_nsk * product.weight)
        order['order_kem_weight'].append(order_kem * product.weight)

        # Inventory levels
        inv_levels = agent._get_inventory_level()
        nsk_inv = inv_levels.get('nsk', 0)
        kem_inv = inv_levels.get('kem', 0)
        order['inv_level_nsk'].append(nsk_inv)
        order['inv_level_kem'].append(kem_inv)
        order['inv_level'].append(nsk_inv + kem_inv)

        # Average sales
        order['av_sales_nsk'].append(statistics[product.sku]['Novosibirsk Main']['sales_mean'])
        order['av_sales_kem'].append(statistics[product.sku]['Kemerovo Main']['sales_mean'])

        # Monthly sales
        for (year, month), sales_data in sales_data_by_month.items():
            month_name = datetime(year, month, 1).strftime('%b').lower()
            month_sales = sales_data.get(product.sku, {})
            order[f'sales_{month_name}_nsk'].append(month_sales.get('novosibirsk', 0))
            order[f'sales_{month_name}_kem'].append(month_sales.get('kemerovo', 0))
            order[f'sales_{month_name}'].append(
                month_sales.get('novosibirsk', 0) + month_sales.get('kemerovo', 0)
            )

    # Create dataframe and save to Excel
    df = pd.DataFrame(order)
    
    ######### save locally
    #output_path = os.path.join(output_dir, f'order_{date}.xlsx')
    #df.to_excel(output_path, index=False)
    #print(f"Order saved to {output_path}")

    df_nsk_order = df.query('order_nsk > 0')[['sku', 'name', 'order_nsk', 'order_nsk_weight']]
    df_kem_order = df.query('order_kem > 0')[['sku', 'name', 'order_kem', 'order_kem_weight']]

    return df, df_nsk_order, df_kem_order

def calculate_order_weight(df) -> dict:
    """
    Example output:
        {
            "nsk: 960,
            "kem": 0
        }
    """
    order_weight = {
        'nsk': df.order_nsk_weight.sum(), 
        'kem': df.order_kem_weight.sum(), 
        }
    order_weight_of_ones = {'nsk': 0, 'kem': 0}
    
      
    return order_weight, order_weight_of_ones
