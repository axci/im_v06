from .models import Inventory, Store, ProductStoreStatistics
from collections import defaultdict


class OracleAgent:
    def __init__(self, product):
        """
        product: (Product class)
        """
        self.product = product
        self.stores = ['nsk', 'kem']

    def get_actions(self, verbose=False) -> list:
        """
        """
        actions = [0, 0]
        inv_levels: dict = self._get_inventory_level()  # {'nsk': 51, 'kem': 6}
        future_demand = self._predict_demand()  # {'nsk': 396, 'kem': 5}        
        S = self._get_S()
        target_inventory = {}
        
        for i, store in enumerate(self.stores):
            if store == 'kem':
                target_inventory[store] = max(S[store] - inv_levels[store] + future_demand[store], 0)
            elif store == 'nsk':
                target_inventory[store] = max(
                    S[store] - inv_levels['nsk'] - inv_levels['kem'] + future_demand['nsk'] + future_demand['kem'], 0
                    )
            actions[i] = self._get_correct_quantity(target_inventory[store]) 
        if verbose:
            for store in self.stores:
                print(f'{store}: S = {S[store]}, Inv = {inv_levels[store]}, FutDem = {future_demand[store]}')
        return actions
    
    def _get_correct_quantity(self, target_inventory: int) -> int:
        pack_size: int = self.product.order_pack  # how many in 1 pack 
        order = (target_inventory // pack_size) * pack_size
        rest = target_inventory % pack_size
        if (rest / pack_size) > 0.4:
            order += pack_size
        return order

    def _predict_demand(self) -> dict:
        """
        Example output:
            {'nsk': 396, 'kem': 5}
        """
        sale_stores = {'nsk': 'Novosibirsk Main', 'kem': 'Kemerovo Main' }
        future_demand = {}
        for store, store_name in sale_stores.items():
            sales_mean = ProductStoreStatistics.objects.filter(
                product=self.product, store=Store.objects.get(name=store_name)
                ).first().sales_mean
            lead_time = Store.objects.get(name=store_name).lead_time_mean
            future_demand[store] = round(sales_mean * lead_time)

        return future_demand
    
    def _get_mean_demand(self) -> dict:
        """
        Example output:
            {'nsk': 24.2185, 'kem': 5.212}
        """
        sale_stores = {'nsk': 'Novosibirsk Main', 'kem': 'Kemerovo Main' }
        mean_demand = {}
        for store, store_name in sale_stores.items():
            sales_mean = ProductStoreStatistics.objects.filter(
                product=self.product, store=Store.objects.get(name=store_name)
                ).first().sales_mean
            mean_demand[store] = sales_mean  
        return mean_demand
    
    def _get_S(self) -> dict:
        mean_demand = self._get_mean_demand()
        S = {}
        S['nsk'] = int((mean_demand['nsk'] + mean_demand['kem']) * (self.product.S_days + 10 )  )  #### <-- changed
        S['kem'] = int(mean_demand['kem'] * (self.product.S_days - 10))
        return S

    def _get_inventory_level(self) -> dict:
        """
        Returns:
            inv_levels: (dict), inventory level for each city
        """

        # Define stores grouped by city
        city_stores = {
            'nsk': ["Novosibirsk Main", "Novosibirsk Reserve", "Novosibirsk Transit"],
            'kem': ["Kemerovo Main", "Kemerovo Transit"]
        }

        # Initialize inventory levels
        inv_levels = defaultdict(int)

        # Query the latest inventory for each store
        for city, stores in city_stores.items():
            for store_name in stores:
                store = Store.objects.filter(name=store_name).first()
                if store:
                    inventory = Inventory.objects.filter(product=self.product, store=store).order_by('-date').first()
                    inv_levels[city] += inventory.inventory_level if inventory else 0

        return dict(inv_levels)

    def _get_number_of_packs(self, order_quantity_good: int) -> int:
        packs_number = round(order_quantity_good / self.store_env.env_config['order_pack'])
        return packs_number


    
