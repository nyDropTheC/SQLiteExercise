import sqlite3
import sys

def create_tables ( database_cursor : sqlite3.Cursor ):
    database_cursor.execute ( """CREATE TABLE IF NOT EXISTS product( 
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL
    );""" )
    
    database_cursor.execute ( """CREATE TABLE IF NOT EXISTS order_details(
        order_id INTEGER PRIMARY KEY NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,

        FOREIGN KEY(product_id) REFERENCES product(product_id)
    );""" )

    database_cursor.execute ( """CREATE TABLE IF NOT EXISTS rack(
        rack_id INTEGER PRIMARY KEY NOT NULL,
        rack_name TEXT NOT NULL
    );""" )

    database_cursor.execute ( """CREATE TABLE IF NOT EXISTS product_rack(
        product_id INTEGER NOT NULL,
        rack_id INTEGER NOT NULL,
        is_main INTEGER NOT NULL,

        FOREIGN KEY(product_id) REFERENCES product(product_id),
        FOREIGN KEY(rack_id) REFERENCES rack(rack_id)
    );""" )

if __name__ == '__main__':
    if len ( sys.argv ) <= 1:
        print ( 'Usage: main.py 1;2;3;4;5' )
        sys.exit ( 1 )
    
    database_connection = sqlite3.connect ( 'datastorage.db' )
    database_cursor = database_connection.cursor ( )
    
    create_tables ( database_cursor )

    orders = sys.argv [ 1 ].split ( ';' )

    racks_by_product = { }
    by_rack = { }

    print ( f'Order gathering for {", ".join ( orders )}' )

    query_orders = f"""SELECT product.product_id, product_name, order_id, quantity FROM order_details 
                    INNER JOIN product ON order_details.product_id = product.product_id WHERE order_id IN ({', '.join ( ['?'] * len ( orders ) )})
            """

    query_racks = f"""SELECT DISTINCT product_rack.product_id, rack_name, is_main = 1 FROM product_rack
                    INNER JOIN order_details ON product_rack.product_id = order_details.product_id
                    INNER JOIN rack ON rack.rack_id = product_rack.rack_id WHERE order_id IN ({', '.join ( ['?'] * len ( orders ) )})
                    ORDER BY is_main = 1 DESC
            """

    for row in database_cursor.execute ( query_racks, orders ):
        if row [ 2 ] == 0:
            racks_by_product [ row [ 0 ] ] [ 'secondary' ].append ( row [ 1 ] )
        else:
            racks_by_product [ row [ 0 ] ] = { 'primary': row [ 1 ], 'secondary': [ ] }

    for row in database_cursor.execute ( query_orders, orders ):
        data = { 'productId': row [ 0 ], 'productName': row [ 1 ], 'orderId': row [ 2 ], 'quantity': row [ 3 ] }

        rack_key = racks_by_product [ data [ 'productId' ] ] [ 'primary' ]
        if not rack_key in by_rack:
            by_rack [ rack_key ] = [ ]

        by_rack [ rack_key ].append ( data )

    for rack_name in by_rack:
        print ( f'=== Rack {rack_name}' )
        for item in by_rack [ rack_name ]:
            print ( f"{item [ 'productName' ]} (id={item [ 'productId' ]})" )
            print ( f"Order {item [ 'orderId' ]}, {item [ 'quantity' ]}pcs" )
            if len ( racks_by_product [ item [ 'productId' ] ] [ 'secondary' ] ) > 0:
                print ( f"Secondary racks {', '.join ( racks_by_product [ item [ 'productId' ] ] [ 'secondary' ] )}" )

            print ( )

