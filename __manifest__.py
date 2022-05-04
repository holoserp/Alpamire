# -*- coding: utf-8 -*-
{
    'name': "alpamire",
    'summary': """
        Alpamire""",
    'description': """
        Customs Alpamire
    """,
    'version': '1.0',
    'depends': [
                'account',
                'product_brand',
                'sale',
                'sale_commission',
                'sale_order_type',
                'stock',
                'stock_barcode',
                ],
    'data': [
        'security/security.xml',
        # 'views/account_move_views.xml',
        'views/account_report.xml',
        'views/product_brand_view.xml',
        'views/product_views.xml',
        'views/report_invoice.xml',
        'views/sale_order_views.xml',
        'views/stock_backorder_views.xml',
        'report/report_sale_take_inventory.xml',
        'report/sale_report.xml',
        # 'wizard/stock_backorder_confirmation_views.xml',
        # 'security/ir.model.access.csv',
        # 'views/report_financial.xml',

        'import_libraries.xml',
    ],
    'qweb': [
        "static/src/xml/qweb_templates.xml",
    ],
}
