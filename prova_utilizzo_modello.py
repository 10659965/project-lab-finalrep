#qua provo ad importare il modello creato nel precedente file e utilizzarlo per predirre un set di dati
import pandas as pd
from PD_multiclassification import dtree_model
#per provare le predizioni su un dataset uncomment questa riga, per provarle su una singola riga invece lascia così
#dataframe = pd.read_excel('acq_lore_no_target.xlsx', header=0, names = ["minX", "minY", "minZ", "maxX", "maxY", "maxZ", "varX", "varY", "varZ", "minAcc", "maxAcc", "varAcc", "tempo", "passi"])
dataframe = pd.read_excel('single.xlsx', header=0, names = ["minX", "minY", "minZ", "maxX", "maxY", "maxZ", "varX", "varY", "varZ", "minAcc", "maxAcc", "varAcc", "tempo", "passi"])
dtree_predictions = dtree_model.predict(dataframe)
print("The right prediction should be 2. Prediction is: " )
print(dtree_predictions)
