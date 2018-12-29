# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.utils.data import fmt_money


def zero_currency(amount):
	d = frappe.defaults.get_defaults()
	if amount:
		return fmt_money(amount, int(d["currency_precision"]), d["currency"])
	else:
		return fmt_money(0, int(d["currency_precision"]), d["currency"])


# Hook Methods for Item Doctype

def item_sales_last_30(doc):
	"""	Returns the last sales of Item X for in last 30 calendar days """
	return zero_currency(frappe.db.sql("""
	SELECT SUM(net_amount) as net_amount
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date > %(after)s
	""", {"doc": doc,
	"after": datetime.date.today() - datetime.timedelta(days=31)},
		as_dict=True)[0]["net_amount"])


def item_qty_last_30(doc):
	""" Returns the quantity of Item X sold in last 30 calendar days """
	return int(frappe.db.sql("""
	SELECT SUM(qty) as qty
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date > %(after)s
	""", {"doc": doc,
	"after": datetime.date.today() - datetime.timedelta(days=31)},
		as_dict=True)[0]["qty"])



def item_sales_last_60(doc):
	""" Returns summary value of Item X for in last 60 calendar days """
	return zero_currency(frappe.db.sql("""
	SELECT SUM(net_amount) as net_amount
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date > %(after)s
	""", {"doc": doc,
	"after": datetime.date.today() - datetime.timedelta(days=61)},
		as_dict=True)[0]["net_amount"])

def item_sales_last_365(doc):
	""" Returns the last sales of Item X for in last 365 calendar days """
	return zero_currency(frappe.db.sql("""
	SELECT SUM(net_amount) as net_amount
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date > %(after)s
	""", {"doc": doc,
	"after": datetime.date.today() - datetime.timedelta(days=365)},
		as_dict=True)[0]["net_amount"])


def item_sales_ytd(doc):
	""" Returns the sales of Item X since begingging of fiscal year """
	from erpnext.accounts.utils import get_fiscal_year
	return zero_currency(frappe.db.sql("""
	SELECT SUM(net_amount) as net_amount
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date > %(after)s
	""", {"doc": doc,
	"after": get_fiscal_year(datetime.date.today())[1]},
		as_dict=True)[0]["net_amount"])


def total_open_purchase_orders(doc):
	""" Totals all purchase orders of Item X before today """
	return zero_currency(frappe.db.sql("""
	SELECT SUM(`tabPurchase Order Item.net_amount`) as net_amount,
	FROM `tabPurchase Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date <%(before)s
	""", {"doc": doc,
	"after": datetime.date(datetime.date.today().year, 1, 1)}, as_dict=True))


def returns_ytd(doc):
	""" Returns quantity of returns start since fiscal year start """
	from erpnext.accounts.utils import get_fiscal_year
	return int(frappe.db.sql("""
	SELECT SUM(qty) as qty
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND is_return = 1
	AND transaction_date between %(after)s and %(before)s
	""", {"doc": doc, "after": get_fiscal_year(datetime.date.today())[1],
	"before": datetime.date.today()}, as_dict=True))


def days_of_inventory_28(doc):
	""" Returns quantity of item sold in the last 28 days (per day), divided by current inventory balance """
	from erpnext.stock.utils import get_stock_balance
	sales = float(frappe.db.sql("""
	SELECT SUM(qty) as item_qty_last_30
	FROM `tabSales Order Item`
	WHERE item_code = %(doc)s
	AND transaction_date > %(after)s
	""", {"doc": doc,
	"after": datetime.date.today() - datetime.timedelta(days=29)},
		as_dict=True)[0]["qty"] / 28)
	warehouses = map(lambda x: x["name"], frappe.get_list("Warehouse"))
	return sales / reduce(get_stock_balance(doc, warehouses))



def inventory_turns(doc):
	""" Returns average inventory level per day	"""
	last_year = datetime.date.today().replace(year=datetime.date.today().year - 1)
	stock_ledger_entries = frappe.db.sql("""
		SELECT item_code, stock_value, name, warehouse
		FROM `tabStock Ledger Entry` sle
		WHERE posting_date between %(after) and %(before)
		AND item_code = %(item_code)
	""", {"item_code": doc, "after": last_year,
	"before": datetime.date.today()}, as_dict=1)
	sle_map = {}
	for sle in stock_ledger_entries:
		if not (sle.item_code, sle.warehouse) in sle_map:
			sle_map[(sle.item_code, sle.warehouse)] = float(sle.stock_value)
	return sum(sle_map.values()) / sales
