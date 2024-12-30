from django.db import models

class WorkingDays(models.Model):
    date = models.DateField(help_text="Working day", unique=True)
    
    def __str__(self):
        return self.date.strftime("%Y-%m-%d")


class Store(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    location = models.CharField(max_length=50, blank=True, null=True, help_text="Store location")
    capacity = models.FloatField(help_text="Maximum storage capacity in cubic units")
    lead_time_mean = models.FloatField(help_text="Mean lead time for deliveries in days")
    lead_time_std = models.FloatField(help_text="Standard deviation of lead time in days")
    container_cost = models.FloatField(help_text="Cost per container")
    container_capacity = models.FloatField(help_text="Capacity of one container in cubic units")
    ordering_cost_kg = models.FloatField(help_text="Cost per kg for ordering products")
    holding_cost_kg = models.FloatField(help_text="Cost per kg for holding inventory")

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    name_short = models.CharField(max_length=50, blank=True, null=True)

    manufacturer = models.CharField(max_length=50, default="")
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    weight = models.FloatField(help_text="Weight of the product in kg")
    volume = models.FloatField(help_text="Volume of the product in cubic units")
    order_pack = models.PositiveIntegerField(blank=False, default=1)
    S_days = models.FloatField(default=30, help_text="For how many days should I order a product")

    def __str__(self):
        return self.sku


class ProductStoreData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_data')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='product_data')

    # Inventory and Metrics
    inventory_level = models.PositiveIntegerField(default=0, help_text="Current inventory level in this store")
    total_sales = models.PositiveIntegerField(default=0, help_text="Total sales quantity in this store")
    average_demand = models.FloatField(default=0, help_text="Average daily demand in this store")
    demand_std = models.FloatField(default=0, help_text="Demand standard deviation in this store")

    # Cost Attributes
    shortage_cost_item = models.FloatField(help_text="Cost per item for shortages in this store")
    lost_demand_cost_item = models.FloatField(help_text="Cost per item for lost demand in this store")

    last_calculated = models.DateTimeField(auto_now=True, help_text="Last time metrics were calculated")

    def __str__(self):
        return f"{self.product.name} data for {self.store.name}"


class ProductGlobalData(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='global_data')

    # Aggregated Metrics Across All Stores
    total_inventory = models.PositiveIntegerField(default=0, help_text="Total inventory across all stores")
    total_sales = models.PositiveIntegerField(default=0, help_text="Total sales across all stores")
    average_demand = models.FloatField(default=0, help_text="Combined average daily demand across all stores")
    demand_std = models.FloatField(default=0, help_text="Combined demand standard deviation across all stores")

    last_calculated = models.DateTimeField(auto_now=True, help_text="Last time metrics were calculated")

    def __str__(self):
        return f"Global data for {self.product.name}"


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories', db_index=True)
    store  = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventories', db_index=True)    
    date = models.DateField(help_text="Date of the inventory record", db_index=True)
    inventory_level = models.FloatField(help_text="Current stock level of the product in the store")

    def __str__(self):
        return f"Inventory of {self.product.sku} at {self.store.name} on {self.date}"

class Region(models.Model):
    title     = models.CharField(max_length=50)
    title_rus = models.CharField(max_length=50)
   
    def __str__(self):
        return self.title

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')
    client_type = models.CharField(max_length=50, blank=True, null=True)
    category    = models.CharField(max_length=50, blank=True, null=True)
    manager     = models.CharField(max_length=50, blank=True, null=True)
    region      = models.CharField(max_length=50, blank=True, null=True)
    #region      = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    quantity    = models.IntegerField(help_text="Quantity of the product sold")
    cost        = models.FloatField(null=True, blank=True)
    sale_value  = models.FloatField(null=True, blank=True)
    sale_date   = models.DateField(help_text="Date of the sale")

    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name} at {self.store.name} on {self.sale_date}"


class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(help_text="Quantity of the product ordered")
    order_date = models.DateField(help_text="Date the order was placed")
    expected_delivery_date = models.DateField(help_text="Expected delivery date for the order")

    def __str__(self):
        return f"Order of {self.quantity} {self.product.name} for {self.store.name} on {self.order_date}"


class Backlog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='backlog')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='backlog')
    quantity = models.PositiveIntegerField(help_text="Quantity of the product backlog")
    backlog_date = models.DateField(help_text="Date of the backlog")

    def __str__(self):
        return f"Backlog of {self.quantity} {self.product.name} at {self.store.name} on {self.backlog_date}"


class Demand(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='demand')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='demand')
    quantity = models.PositiveIntegerField(help_text="Quantity of the product demand")
    demand_date = models.DateField(help_text="Date of the demand")

    def __str__(self):
        return f"Demand of {self.quantity} {self.product.name} at {self.store.name} on {self.demand_date}"


class ProductStoreStatistics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    sales_mean = models.FloatField(null=True, blank=True, help_text="Mean sales for the product at the store")
    sales_std = models.FloatField(null=True, blank=True, help_text="Sales standard deviation for the product at the store")
    S = models.FloatField(null=True, blank=True, help_text="S: max threshold")


class ProductStatistics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sales_mean = models.FloatField(null=True, blank=True, help_text="Mean sales for the product at the store")
    sales_std = models.FloatField(null=True, blank=True, help_text="Sales standard deviation for the product at the store")
    S = models.FloatField(null=True, blank=True, help_text="S: max threshold")