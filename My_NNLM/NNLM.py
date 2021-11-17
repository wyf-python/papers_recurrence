"""
original from:
https://github.com/graykode/nlp-tutorial/blob/master/1-1.NNLM
"""
import torch
import torch.nn as nn
import torch.optim as optim


def make_batch():
    input_batch = []
    target_batch = []

    for sen in sentences:
        # space tokenizer
        word = sen.split()
        # create (1~n-1) as input
        input = [word_dict[n] for n in word[:-1]]
        # create (n) as target, We usually call this 'casual language model'
        target = word_dict[word[-1]]

        input_batch.append(input)
        target_batch.append(target)

    return input_batch, target_batch


class NNLM(nn.Module):
    def __init__(self):
        super(NNLM, self).__init__()
        self.C = nn.Embedding(n_class, m)
        self.H = nn.Linear(n_step * m, n_hidden, bias=False)
        self.d = nn.Parameter(torch.ones(n_hidden))
        self.U = nn.Linear(n_hidden, n_class, bias=False)
        self.W = nn.Linear(n_step * m, n_class, bias=False)
        self.b = nn.Parameter(torch.ones(n_class))

    def forward(self, X):
        # X : [batch_size, n_step, m]
        X = self.C(X)
        # [batch_size, n_step * m]
        X = X.view(-1, n_step * m)
        # [batch_size, n_hidden]
        tanh = torch.tanh(self.d + self.H(X))
        # [batch_size, n_class]
        output = self.b + self.W(X) + self.U(tanh)
        return output


if __name__ == '__main__':
    # number of steps, n-1 in paper
    n_step = 2
    # number of hidden size, h in paper
    n_hidden = 2
    # embedding size, m in paper
    m = 2

    sentences = ["i like dog", "i love coffee", "i hate milk"]

    word_list = " ".join(sentences).split()
    word_list = list(set(word_list))
    word_dict = {w: i for i, w in enumerate(word_list)}
    number_dict = {i: w for i, w in enumerate(word_list)}
    # number of Vocabulary
    n_class = len(word_dict)

    model = NNLM()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    input_batch, target_batch = make_batch()
    input_batch = torch.LongTensor(input_batch)
    target_batch = torch.LongTensor(target_batch)

    # Training
    for epoch in range(5000):
        optimizer.zero_grad()
        output = model(input_batch)

        # output : [batch_size, n_class], target_batch : [batch_size]
        loss = criterion(output, target_batch)
        if (epoch + 1) % 1000 == 0:
            print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.6f}'.format(loss))

        loss.backward()
        optimizer.step()

    # Predict
    predict = model(input_batch).data.max(1, keepdim=True)[1]

    # Test
    print([sen.split()[:2] for sen in sentences], '->', [number_dict[n.item()] for n in predict.squeeze()])
