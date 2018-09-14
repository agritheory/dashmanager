# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
import dashmanager

class TestDashmanager(unittest.TestCase):

	def test_getDashboardDomponents(self):
		fields = dashmanager.get_dashboard_components("Item")
		print (fields)
