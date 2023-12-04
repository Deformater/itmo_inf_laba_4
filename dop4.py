import datetime

from main import Parser as MainParser
from dop1 import Parser as DopParser1
from dop2 import Parser as DopParser2
# from main import Parser as MainParser

def time_measure(parser):
    start_time = datetime.datetime.now()
    for _ in range(1000):
        parser.convert()
    
    end_time = datetime.datetime.now()
    
    delta = end_time - start_time
    print(delta.total_seconds() * 100)


time_measure(MainParser("shedule.xml", MainParser.Formats.XML, MainParser.Formats.JSON))
time_measure(DopParser1("shedule.xml", DopParser1.Formats.XML, DopParser1.Formats.JSON))
time_measure(DopParser2("shedule.xml", DopParser2.Formats.XML, DopParser2.Formats.JSON))
