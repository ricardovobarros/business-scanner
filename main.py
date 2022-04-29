from config import *
from economista import Economista
from utils import *

# import input excel
data = extract_data("data/input.xlsx")


economista = Economista(data)

