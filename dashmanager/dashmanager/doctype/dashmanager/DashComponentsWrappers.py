

class ChartModel:
	def __init__(self):
		# self.datasets = dataset
		# self.labelsets = labelsets
		self.settings = {
			"type": 'axis-mixed',  # 'bar', 'line', 'pie', 'percentage'
			"height": 300,
			"colors": ['purple', '#ffa3ef', 'light-blue']
		}
		self.datasets = []

	def setLabels(self, labels):
		if not isinstance(labels, ChartLabel):
			raise Exception("Only List of ChartLabelSet accepted")
		if not len(labels.getLabels()) > 0:
			raise Exception("Empty Labels Passed")
		self.labels = labels

	def addDataSets(self, dataset):
		if not isinstance(dataset, ChartDataSet):
			raise Exception("Dataset should be of type ChartDataSet")
		self.datasets.append(dataset.getDataSets())

	def generateChartModelObject(self):
		return {
			"data": {
				"labels": self.labels.getLabels(),
				"datasets": self.datasets
				# "yMarkers": [{ "label": "Marker", "value": 70,"options": { "labelPos": 'left' }}],
				# "yRegions": [{ "label": "Region", "start": -10, "end": 50,"options": { "labelPos": 'right' }}]
			},
			"title": self.settings["title"],
			"type": self.settings["type"],  # 'bar', 'line', 'pie', 'percentage'
			"height": self.settings["height"]  # ,
			# "colors": self.settings["colors"]
		}

	def setSettings(self, settingsDict):
		for setting in settingsDict:
			self.settings[setting] = settingsDict[setting]


class ChartDataSet:
	def __init__(self, values, name=None, chartType=None):
		self.name = name
		self.values = values
		self.chartType = chartType

	def getDataSets(self):
		if not isinstance(self.values, list):
			raise Exception("Values should be array of numbers")
		datasets = {
			"name": self.name,
			"values": self.values
		}
		if self.chartType:
			datasets["chartType"] = self.chartType
		return datasets


class ChartLabel:
	def __init__(self, labels):
		self.labels = labels

	def getLabels(self):
		if not isinstance(self.labels, list):
			raise Exception("Chart Labels are not List of Strings")
		return self.labels


class Table:
	max_table_rows = 10
	max_table_cols = 5

	def __init__(self, cols, rows):
		if not isinstance(cols, list):
			raise Exception("Columns can be list only.")
		if not isinstance(rows, list):
			raise Exception("Rows can be list of list only.")
		# other validations if required....

		self.cols = cols[0:self.max_table_cols]
		self.rows = rows[0:self.max_table_rows]
		self.settings = {
			"rowno": True,
			"displayheader": True,
			"knowmoretext": "+" + str(len(rows) - len(self.rows)) + " more rows",
			"overflow": (len(rows) > len(self.rows)),
			"height": 200  # default height
		}

	def setSettings(self, settingsDict):
		for setting in settingsDict:
			self.settings[setting] = settingsDict[setting]

	def generateTableModelObject(self):
		return {
			"columns": self.cols,
			"rows": self.rows,
			"settings": self.settings
		}


class List:
	max_list_items = 10

	def __init__(self, listitemarr):
		self.listitems = []

		if listitemarr and isinstance(listitemarr, list):
			for item in listitemarr[0:self.max_list_items]:
				self.listitems.append(item.__dict__)

		self.settings = {
			"type": "ordered",
			"bullets": True,
			"hasvalues": True,
			"knowmoretext": "+" + str(len(listitemarr) - len(self.listitems)) + " more rows",
			"overflow": (len(listitemarr) > len(self.listitems)),
			"height": 200,
			"indicator": False
		}

	def setSettings(self, settingsDict):
		for setting in settingsDict:
			self.settings[setting] = settingsDict[setting]

	def generateListModelObject(self):
		return {
			"listitems": self.listitems,
			"settings": self.settings
		}


class ListItem:
	def __init__(self, item, value, color=None):
		self.item = item
		self.value = value
		self.color = color
		if color:
			if self.color not in ["red", "green", "orange", "purple", "darkgrey",
				"black", "yellow", "lightblue", "blue"]:
				raise Exception("You can only pass red, green, orange, purple, \
					darkgrey,black,yellow,lightblue, blue as colors, \
					you passed: " + str(self.color))


class SummaryValue:
	def __init__(self, value, caption):
		self.value = value
		self.caption = caption

	def generateSummaryValueObject(self):
		return {
			"caption": self.caption,
			"value": self.value
		}


class StatusField:
	def __init__(self, label, color, status):
		self.color = color
		self.label = label
		self.status = status

		if self.color not in ["red", "green", "orange", "purple", "darkgrey",
			"black", "yellow", "lightblue", "blue"]:
			raise Exception("You can only pass red, green, orange, purple, \
				darkgrey,black,yellow,lightblue, blue as colors, \
				you passed: " + str(self.color))

	def generateStatusfieldObject(self):
		return {
			"label": self.label,
			"color": self.color,
			"status": self.status
		}
