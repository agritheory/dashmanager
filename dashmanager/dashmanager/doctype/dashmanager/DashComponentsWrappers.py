

class ChartModel:
    def __init__(self):
        # self.datasets = dataset
        # self.labelsets = labelsets
        self.settings = {
			"type": 'axis-mixed', ##// or 'bar', 'line', 'pie', 'percentage'
			"height": 300,
			"colors": ['purple', '#ffa3ef', 'light-blue']
		}
        self.datasets = []
    
    def setLabels(self, labels): 
        if not isinstance(labels, ChartLabel):
            raise Exception("Only List of ChartLabelSet accepted")
        
        if not len (labels.getLabels()) > 0:
            raise Exception("Empty Labels Passed")
        
        self.labels = labels

    def addDataSets(self, dataset ):
        if not isinstance(dataset, ChartDataSet):
            raise Exception("Dataset should be of type ChartDataSet")
        self.datasets.append(dataset.getDataSets())
    
    def generateChartModelObject (self):
        return {
            "data": {
                "labels":self.labels.getLabels(),
                "datasets":self.datasets#, 
                #"yMarkers": [{ "label": "Marker", "value": 70,"options": { "labelPos": 'left' }}],
				#"yRegions": [{ "label": "Region", "start": -10, "end": 50,"options": { "labelPos": 'right' }}]
            },
            "title": self.settings["title"],
			"type": self.settings["type"], ##// or 'bar', 'line', 'pie', 'percentage'
			"height": self.settings["height"],
			"colors": self.settings["colors"]
        }
    
    def setSettings(self, settingsDict):
        for setting in settingsDict:
            self.settings[setting] = settingsDict[setting]

    
    
    
class ChartDataSet:
    def __init__(self, name, values, chartType):
        self.name = name
        self.values = values
        self.chartType = chartType
    
    def getDataSets(self):
        if not isinstance(self.values, list):
            raise Exception("Values should be array of numbers")
        
        return {
            "name": self.name,
            "values":self.values,
            "chartType":self.chartType
        }


class ChartLabel:
    def __init__(self, labels):
        self.labels = labels
    
    def getLabels(self):
        if not isinstance(self.labels, list):
            raise Exception("Chart Labels are not List of Strings")
        return self.labels

class Table:
    def __init__ (self, cols, rows):
        if not isinstance(cols, list):
            raise Exception("Cols can be list only.")
        if not isinstance(rows, list):
            raise Exception("Rows can be list of list only.")
        
        ## other validations if required.... 

        self.cols = cols
        self.rows = rows
        self.settings = {
            "rowno":True
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
    def __init__ (self, listitems):
        self.listitems = []
        self.settings={
			"type":"ordered",
			"bullets":True,
			"hasvalues":True
		}

        if listitems and isinstance(listitems, list):
            for item in listitems:
                self.listitems.append(item.__dict__)
             
    
    def setSettings(self, settingsDict):
        for setting in settingsDict:
            self.settings[setting] = settingsDict[setting]
    
    def generateListModelObject(self):
        print ("Items:", self.listitems)
        return {
            "listitems": self.listitems,
            "settings":self.settings
        }

class ListItem:
    def __init__ (self, item, value):
        self.item = item
        self.value = value

class SummaryValue:
    def __init__ (self, value, caption):
        self.value = value
        self.caption = caption
    
    def generateSummaryValueObject(self):
        return {
			"caption": self.caption,
			"value":self.value
		}
        