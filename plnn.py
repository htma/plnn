import torch
import numpy as np
import matplotlib.pyplot as plt

import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from torch.autograd import Variable
from torchvision import datasets, transforms

from data_loader import MyCustomDataset

from hidden_neuron_status import neuron_active, build_RGB
#from generate_data import generate_batches

dtype = torch.float
batch_size = 10
device = torch.device("cpu")

class PLNN(torch.nn.Module):
    def __init__(self, D_in, H1, H2, H3, D_out):
        super(PLNN, self).__init__()
        self.hidden1 = nn.Linear(D_in, H1)
        self.hidden2 = nn.Linear(H1, H2)
        self.hidden3 = nn.Linear(H2, H3)
        self.output = nn.Linear(H3, D_out)
        # Create random Tensors for  weights.
        # Setting requires_grad=True indicates that we want to compute
        # gradients w.r.t. these Tensors during the backward pass.
        # self.w1 = torch.randn(D_in, H1, device=device, dtype=dtype, requires_grad=True)
        # self.w2 = torch.randn(H1, H2, device=device, dtype=dtype, requires_grad=True)
        # self.w3 = torch.randn(H2, H3, device=device, dtype=dtype, requires_grad=True)
        # self.w4 = torch.randn(H3, D_out, device=device, dtype=dtype, requires_grad=True)
        

    def forward(self, x):
        #state = np.zeros((batch_size, 2)) # the states of all hidden layers
        # Forward pass
        h1 = self.hidden1(x)
        h1_state = neuron_active(h1)
    
        h1_relu = h1.clamp(min=0)
        h2 = self.hidden2(h1_relu)
        h2_state = neuron_active(h2)
        state = np.concatenate((h1_state, h2_state), axis=1)
        print('state2 shape is ', state.shape)
        
        h2_relu = h2.clamp(min=0)
        h3 = self.hidden3(h2_relu)
        h3_state = neuron_active(h3)
        state = np.concatenate((state, h3_state), axis=1)
        print('state3 shape is ', state.shape)

        h3_relu = h3.clamp(min=0)
        y_pred = self.output(h3_relu)
        
        return state, F.log_softmax(y_pred, dim=1)

def main():
    D_in, D_out = 2, 2
    H1, H2, H3 = 4, 16, 2
    model = PLNN(D_in, H1, H2, H3, D_out)
    criterion = nn.NLLLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
   
    
    print(model)
    #batches = generate_batches(N)

    train_loader = torch.utils.data.DataLoader(
        MyCustomDataset('./data/dataset.csv',
                        transform=transforms.Compose([
                            transforms.ToTensor()])),
        batch_size=10,shuffle=False)    

    # define  an unit circle
    theta = np.linspace(0, 2*np.pi, 100)
    a, b = 1 * np.cos(theta), 1 * np.sin(theta)
  
    # training
    for epoch in range(10):
        fig, ax = plt.subplots()
        for batch_idx, (data, target)  in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            state,predictions = model(data)
            print('state is ', state)
            loss = criterion(predictions, target)
            loss.backward()
            optimizer.step()

            # printing training results

            # if batch_idx % 10 == 0:
            #     print('Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
            #         epoch, batch_idx*len(data), len(train_loader.dataset), 100.*batch_idx/len(train_loader),  loss.item()))

                
            # painting training  results
            ndata = data.numpy()
            for x in ndata:
                rect = plt.Rectangle(x, 0.1, 0.1, fc=build_RGB(state))
                ax.add_patch(rect)

        plt.plot(a, b, linestyle='-', linewidth=2, label='Circle')
        ax.set(xlabel='$x_1$', ylabel='$x_2$', title='Train data')
        ax.xaxis.set_ticks([-1.5, -1.2, -0.9, -0.6,-0.3, 0, 0.3,0.6,0.9,1.2,1.5])
        ax.yaxis.set_ticks([-1.5, -1.2, -0.9, -0.6,-0.3, 0, 0.3,0.6,0.9,1.2,1.5])
    
        ax.grid(True)
#        plt.show()

if __name__ == '__main__':
    main()
