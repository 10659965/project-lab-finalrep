import pandas as pd
from sklearn import datasets
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.multiclass import OneVsOneClassifier
#import excel file
dataframe = pd.read_excel('training_data.xlsx', header=0, names = ["minX", "minY", "minZ", "maxX", "maxY", "maxZ", "varX", "varY", "varZ", "minAcc", "maxAcc", "varAcc", "tempo", "passi","target"])
print(dataframe.shape)
X = dataframe.drop('target', axis = 1)
y = dataframe.target
#split train and test data: train data are used to train the model 75% while test data are used to test the model and asses its accuracy 25% of the data
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.20, stratify=y,random_state = 1)
#apply ML models and evaluation
#Il modello di ML che useremo è questo: Decision tree classifier
from sklearn.tree import DecisionTreeClassifier
#la variabile d_tree model è la variabile che contiene il modello allenato
dtree_model = DecisionTreeClassifier(max_depth = None).fit(X_train, y_train)
dtree_model.fit(X_train, y_train)
#dtree_predictions contiene il vettore delle predizioni sul dataframe X_test: nel nostro caso al posto di un dataframe in igresso questa funzione avrà un vettore
#il vettore sarà formato dai valori di max/min/std delle accelerezioni + passi e tempo della sessione
dtree_predictions = dtree_model.predict(X_test)
#l'accuratezza è semplicemente calcolato confrontando le predizioni del nostro modello con il target reale assegnato da noi
accuracy = metrics.accuracy_score(y_test, dtree_predictions)
#accuracy = dtree_model.score(X_test, y_test)
print("decision tree accuracy:  "+str(accuracy))
#qua crea la confusion matrix
cm = confusion_matrix(y_test, dtree_predictions)
print(cm)
#qua in teoria dovrebbe printare l'albero ma a me su pycharm non funziona, usando anaconda invece funziona e printa le soglie che utilizza per predirre i dati
from sklearn import tree
tree.plot_tree(dtree_model)
#SVM classifier: per completezza ho utilizzato anche diversi modelli di ML ma i tutor mi hanno consigliato di usare il decision tree
from sklearn.svm import SVC
svm_model_linear = SVC(kernel = 'linear', C = 1).fit(X_train, y_train)
svm_predictions = svm_model_linear.predict(X_test)
accuracy = svm_model_linear.score(X_test, y_test)
cm = confusion_matrix(y_test, svm_predictions)
print("SVM_linear accuracy:  "+str(accuracy))
print (cm)
#KNN classifier
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors = 5).fit(X_train, y_train)
accuracy = knn.score(X_test, y_test)
knn_predictions = knn.predict(X_test)
cm = confusion_matrix(y_test, knn_predictions)
print("KNN accuracy:  "+str(accuracy))
print (cm)
#Naive Bayes
from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB().fit(X_train, y_train)
gnb_predictions = gnb.predict(X_test)
accuracy = gnb.score(X_test, y_test)
print("Naive Bayes accuracy:  "+str(accuracy))
cm = confusion_matrix(y_test, gnb_predictions)
print (cm)
