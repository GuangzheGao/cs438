import matplotlib.pyplot as plt

with open("throughput") as f:
    data = f.read()
    data_list = data.split("\n")
    # print data_list
    for i in range(len(data_list) / 3):
        x_list = []
        y_list = []
        #print line.split()
        if len(data_list[0+i]) > 1:
            x_list.append(data_list[0+i].split(' ')[0])
            y_list.append(data_list[0+i].split(' ')[1])
        if len(data_list[3+i]) > 1:
            x_list.append(data_list[3+i].split(' ')[0])
            y_list.append(data_list[3+i].split(' ')[1])
        if len(data_list[6+i]) > 1:
            x_list.append(data_list[6+i].split(' ')[0])
            y_list.append(data_list[6+i].split(' ')[1])
        plt.plot(x_list, y_list, linestyle='--', marker='o', color='r')
plt.savefig("throughput.jpg")