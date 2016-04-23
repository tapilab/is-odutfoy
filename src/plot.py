import matplotlib.pyplot as plt

def plot(X, y):
    for i in range(X.shape[1]):
        plt.figure(i)
        plt.plot(list(X[:, i]), list(y), 'o')
        plt.show()


