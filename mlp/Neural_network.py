import numpy as np
import random
import NNlib as nlb

class Neural:
    def __init__(self , data_matrix , batch_size , K_classes, n_hidden = 0 , n_h_neuron = 3 ):
        self.data = data_matrix

        for i in range (len(self.data[0])-1):
            # self.data[:,i] = (self.data[:,i] - np.min(self.data[:,i])) / (np.max(self.data[:,i])-np.min(self.data[:,i]))
            self.data[:,i] = (self.data[:,i] - np.mean(self.data[:,i])) / np.std(self.data[:,i])
            

        
        self.n_hidden = n_hidden
        self.n_h_neuron = n_h_neuron
        self.batch_size = batch_size
        self.nbInstances = len(data_matrix)
        self.nbFeatures = len(data_matrix[0])
        self.K_classes = K_classes        
        
        self.trainingSize = int(self.nbInstances * 0.75)
        self.testingSize = self.nbInstances - self.trainingSize
        self.trainingData = np.empty(shape = (self.trainingSize , self.nbFeatures))
        self.testingData = np.empty(shape = (self.testingSize , self.nbFeatures))		
		

        self.W1 = np.empty(shape = (self.nbFeatures - 1, K_classes) , dtype='float32')
        self.W1 = self.initMatrix(self.W1)

        self.W2 = np.empty(shape = (n_h_neuron , K_classes) , dtype='float32')
        self.W2 = self.initMatrix(self.W2)


        self.b1 = np.empty(shape = (1 , K_classes))          

		#copy data into training and testing set
        for i in range(self.trainingSize):
            for j in range(self.nbFeatures):    
                self.trainingData[i][j] = self.data[i][j]
				
        for i in range(self.testingSize):
            for j in range(self.nbFeatures):
                self.testingData[i][j] = self.data[i + self.trainingSize][j]
				
        # self.trainingData = (self.trainingData - np.mean(self.trainingData) / )
        # print(self.trainingData[:,:], end="\n")
        # print(self.testingData[:,-1])
        self.X_train = np.empty(shape = (self.batch_size,self.nbFeatures - 1))
        self.Y_train = np.empty(shape = (self.batch_size,self.K_classes))


        # self.X_train = (self.X_train - np.mean(self.X_train)) / np.std(self.X_train)

        self.X_test = self.data[self.trainingSize:, :-1]
        self.Y_test = self.data[self.trainingSize:,  -1]

        # print(self.X_test)
        # self.X_test  = (self.X_test - np.mean(self.X_test)) / np.std(self.X_test)

        one_hot = np.zeros((self.Y_test.shape[0], self.K_classes))

        for i in range(self.Y_test.shape[0]):
            one_hot[i, int(self.Y_test[i])] = 1
        self.Y_test = one_hot





    def initMatrix(self , A):
        self.A = A
        # random.seed(1000)
        for i in range(len(A)):
            for j in range(len(A[0])):  
                self.A[i][j] =  random.uniform(-.0001 , .0001)

        # print(self.A)
        return self.A     


    def create_one_hot(self , k , indexInBatch , matrixY):
		# print(matrixY,"\n\n")
        for i in range(len(matrixY[0])):
            if i == k:
                matrixY[indexInBatch][i] = 1
            else:
                matrixY[indexInBatch][i] = 0
        # print(matrixY,"\n\n")
        return matrixY


    def load_attributes_labels(self , dataset , X , Y , dataindex ,batch_size):
       
        X = dataset[dataindex : dataindex+batch_size , :-1]

        last_attribute_index = -1
        starting_index = dataindex
        for j in range(batch_size):
            self.create_one_hot(dataset[starting_index + j][last_attribute_index], indexInBatch = j , matrixY = Y)

        return X , Y


    def predict(self, X):
        
        H1 = X @ self.W1 + self.b1
        y = nlb.NNLib.sigmoid(H1)
        return y


    def feed_forward(self , X , W1 , b1):
        #using matrix multiplication sign -- @
        H1 = X @ W1 + b1
        #applying activation function
        y_hat = nlb.NNLib.sigmoid(H1)
        
        return y_hat
        

    def back_prop(self , y_hat , y , X):
        
        loss = 2 * (y_hat - y)
        # when function takes true it means it is derivative of func
        delta = loss * nlb.NNLib.sigmoid(y_hat, True)
        dW = delta.T @ X

        db = delta

        return dW , db

    
    def prediction_accuracy(self):
        acc = 0
        for i in range(len(self.X_test)):
            acc += nlb.NNLib.accuracy(self.predict(self.X_test[i]), self.Y_test[i])
            # print(self.Y_test[i])
        # print(self.Y_test)
        print(acc / len(self.X_test) * 100)


    
    def train_epoch(self , n_epoch):
        # self.X_train  , self.Y_train = self.load_attributes_labels(self.trainingData , self.X_train , self.Y_train , 0 , self.batch_size)
        
        epoch = n_epoch
        n_iteration = self.trainingSize/self.batch_size
        
        for j in range(n_epoch):
            np.random.shuffle(self.trainingData)
            # np.seterr(over='ignore')

            total_error = 0.
            for i in range(int(n_iteration)):
                self.X_train  , self.Y_train = self.load_attributes_labels(self.trainingData , self.X_train , 
                                        self.Y_train , self.batch_size * i , self.batch_size)

                for z in range(self.batch_size):
                   
                    # ---------------   FEED FORWARD -------------
                    
                    X = self.X_train[z]
                    
                    X = np.reshape(X , (1 ,  X.shape[0]))

                    y_hat  = self.feed_forward(X , self.W1 , self.b1)
                    
                    y = self.Y_train[z]
                    
                    # --------------- BACKPROPOGATION

                    # print(y_hat , "------" , y)

                    # print(y , y_hat)
                    error = np.mean((y_hat - y)**2)
                    # print(error)

                    total_error += error

                    dW , db = self.back_prop(y_hat , y , X )
                    
                    
                    # ----------UPDATE PARAMETERS -------------
                    n = .001
                    self.W1 -= n*dW.T
                    self.b1 -= n*db
                    # print(self.W1)
                # exit(0)
            print(total_error / (self.batch_size * n_iteration))
            acc = 0



            
            

            


        



        


        
        

