GROUPING_COLUMN = ["transport_area_number"]


def calc_route_product_summary(df):
    def find_unique_products(products):
        if len(products) == 1:
            products = [x.strip() for x in products[0].split(";")]
        else:
            unique_products = []
            for product in products:
                unique_products += [x.strip() for x in product.split(";")]
            products = list(set(unique_products))
        products.sort()
        return products

    route_product_summary = (
        df.sort_values(["Product Name"])
        .groupby(GROUPING_COLUMN)
        .agg(
            n_stops=("Ticket No", "count"),
            n_products=("Quantity", "sum"),
            product_types=("Product Name", "unique"),
        )
        .reset_index()
    )

    # route_product_summary = route_product_summary.assign(
    #     product_types=route_product_summary["product_types"].apply(find_unique_products)
    # )

    route_product_summary = route_product_summary.rename(
        columns={
            "transport_area_number": "Transport area",
            "n_stops": "Number of stops",
            "n_products": "Number of products",
            "product_types": "Product types",
        }
    )
    return route_product_summary
