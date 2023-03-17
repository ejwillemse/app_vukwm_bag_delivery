GROUPING_COLUMN = ["Transport Area"]


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
            n_stops=("Site Bk", "nunique"),
            n_products=("Quantity", "sum"),
            product_types=("Product Name", "unique"),
        )
        .reset_index()
    )

    route_product_summary = route_product_summary.rename(
        columns={
            "n_stops": "Number of stops",
            "n_products": "Number of products",
            "product_types": "Product types",
        }
    )
    return route_product_summary


def day_summary(df):
    return (
        df.groupby(["Required Date"])
        .agg(
            **{
                "Uncompleted stops": ("Site Bk", "nunique"),
            }
        )
        .reset_index()
    )


def profile_type_summary(df):
    return (
        df.assign(
            **{
                "Delivery vehicle type": (df["Transport Area"] == 2).replace(
                    {True: "Bicycle", False: "Van or Bicycle"}
                )
            }
        )
        .groupby(["Delivery vehicle type"])
        .agg(
            **{
                "Uncompleted stops": ("Site Bk", "nunique"),
            }
        )
        .reset_index()
    )


def product_type_summary(df):
    return (
        df.groupby(["Product Name"])
        .agg(
            **{
                "Number of items": ("Quantity", "sum"),
            }
        )
        .reset_index()
    )
