==== LETTURA PICKLES ====

# open a file, where you ant to store the data
file = open('important', 'wb')

# dump information to that file
pickle.dump(x, file)

# close the file
file.close()




==== SCRITTURA PICKLES =====
file = open('important', 'rb')

# dump information to that file
data = pickle.load(file)

# close the file
file.close()