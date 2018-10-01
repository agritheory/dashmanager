

class ChartModel:
    def __init__(self, settings):
        # self.datasets = dataset
        # self.labelsets = labelsets
        self.settings = settings
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
