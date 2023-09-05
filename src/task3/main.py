import concurrent.futures
import multiprocessing
import model
import numpy as np
import pandas as pd
import re
import torch

from torch.utils.data import DataLoader, TensorDataset, random_split

PRESCRIZIONI = True
READ_DATA_PATH = "balanced_data"

if PRESCRIZIONI:
    file_names = [
        "anagraficapazientiattivi_b_pres",
        "diagnosi_b_pres",
        "esamilaboratorioparametri_b_pres",
        "esamilaboratorioparametricalcolati_b_pres",
        "esamistrumentali_b_pres",
        "prescrizionidiabetefarmaci_b_pres",
        "prescrizionidiabetenonfarmaci_b_pres",
        "prescrizioninondiabete_b_pres",
    ]
else:
    file_names = [
        "anagraficapazientiattivi_b",
        "diagnosi_b",
        "esamilaboratorioparametri_b",
        "esamilaboratorioparametricalcolati_b",
        "esamistrumentali_b",
        "prescrizionidiabetefarmaci_b",
        "prescrizionidiabetenonfarmaci_b",
        "prescrizioninondiabete_b",
    ]

def read_csv(filename):
    return pd.read_csv(filename, header=0)

# Read all the dataset concurrently and store them in a dictionary with the name of the file as key
with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    df_list = dict()
    for name in file_names:
        df_list[str(name)] = executor.submit(read_csv, f"{READ_DATA_PATH}/{name}.csv")

if PRESCRIZIONI:
    df_anagrafica = df_list["anagraficapazientiattivi_b_pres"].result()
    df_diagnosi = df_list["diagnosi_b_pres"].result()
    df_esami_lab_par = df_list["esamilaboratorioparametri_b_pres"].result()
    df_esami_lab_par_cal = df_list["esamilaboratorioparametricalcolati_b_pres"].result()
    df_esami_stru = df_list["esamistrumentali_b_pres"].result()
    df_pres_diab_farm = df_list["prescrizionidiabetefarmaci_b_pres"].result()
    df_pres_diab_no_farm = df_list["prescrizionidiabetenonfarmaci_b_pres"].result()
    df_pres_no_diab = df_list["prescrizioninondiabete_b_pres"].result()
else:
    df_anagrafica = df_list["anagraficapazientiattivi_b"].result()
    df_diagnosi = df_list["diagnosi_b"].result()
    df_esami_lab_par = df_list["esamilaboratorioparametri_b"].result()
    df_esami_lab_par_cal = df_list["esamilaboratorioparametricalcolati_b"].result()
    df_esami_stru = df_list["esamistrumentali_b"].result()
    df_pres_diab_farm = df_list["prescrizionidiabetefarmaci_b"].result()
    df_pres_diab_no_farm = df_list["prescrizionidiabetenonfarmaci_b"].result()
    df_pres_no_diab = df_list["prescrizioninondiabete_b"].result()

#######################################
############### STEP 1 ################
#######################################

# In this step we have considered records from table diagnosi as macro events
# While the other ones have been considered as micro events (esami and prescrizioni)
# So now we are going to delete the dates from the micro events
df_esami_lab_par = df_esami_lab_par.drop(columns="data")
df_esami_lab_par_cal = df_esami_lab_par_cal.drop(columns="data")
df_esami_stru = df_esami_stru.drop(columns="data")
df_pres_diab_farm = df_pres_diab_farm.drop(columns="data")
df_pres_diab_no_farm = df_pres_diab_no_farm.drop(columns="data")
df_pres_no_diab = df_pres_no_diab.drop(columns="data")

# Now we are going to prepare data for the model
all_events_concat = pd.concat(
    objs=(
        df_diagnosi,
        df_esami_lab_par, 
        df_esami_lab_par_cal, 
        df_esami_stru, 
        df_pres_diab_farm, 
        df_pres_diab_no_farm)
)

final_df = df_anagrafica.merge(all_events_concat, on=["idana", "idcentro"], how="inner")

final_df = final_df[:100]

# First we delete "idana" and "idcentro" as they don't give informations to the model
final_df = final_df.drop(columns=["idana", "idcentro"])

# Here we convert feature "sesso" into numeric feature
final_df["sesso"] = final_df["sesso"].replace(["M", "F"], [0.0, 1.0])

# Now we want to convert every date into a numeric progressive value
# We chose them as the number of months that have passed from the birth
final_df["annonascita"] = pd.to_datetime(final_df["annonascita"], format="%Y-%m-%d")
final_df["annodiagnosidiabete"] = pd.to_datetime(final_df["annodiagnosidiabete"], format="%Y-%m-%d")
final_df["annoprimoaccesso"] = pd.to_datetime(final_df["annoprimoaccesso"], format="%Y-%m-%d")
final_df["annodecesso"] = pd.to_datetime(final_df["annodecesso"], format="%Y-%m-%d")
final_df["data"] = pd.to_datetime(final_df["data"], format="%Y-%m-%d")

final_df["annodiagnosidiabete"] = (final_df["annodiagnosidiabete"] - final_df["annonascita"]) / pd.Timedelta(days=31)
final_df["annoprimoaccesso"] = (final_df["annoprimoaccesso"] - final_df["annonascita"]) / pd.Timedelta(days=31)
final_df["annodecesso"] = (final_df["annodecesso"] - final_df["annonascita"]) / pd.Timedelta(days=31)
final_df["data"] = (final_df["data"] - final_df["annonascita"]) / pd.Timedelta(days=31)

# We delete the date of the birth since would be zero for all records
final_df = final_df.drop(columns="annonascita")

# We also delete columns scolarita, statocivile and professione since they have a percentage of NaN values above 50%
final_df = final_df.drop(columns=["scolarita", "statocivile", "professione"])

# Now we substitute all categorical feature into a numeric one
amd_codes = final_df["codiceamd"].value_counts().index
final_df["codiceamd"] = final_df["codiceamd"].replace(amd_codes, np.arange(float(len(amd_codes))))

valore = final_df["valore"].value_counts().index
valore_string = [x for x in valore if re.search("[a-zA-Z]", str(x))]
final_df["valore"] = final_df["valore"].replace(valore_string, np.arange(float(len(valore_string))))
final_df["valore"] = final_df["valore"].astype("float64")

stitch_codes = final_df["codicestitch"].value_counts().index
final_df["codicestitch"] = final_df["codicestitch"].replace(stitch_codes, np.arange(float(len(stitch_codes))))

atc_codes = final_df["codiceatc"].value_counts().index
final_df["codiceatc"] = final_df["codiceatc"].replace(atc_codes, np.arange(float(len(atc_codes))))

drug_description = final_df["descrizionefarmaco"].value_counts().index
final_df["descrizionefarmaco"] = final_df["descrizionefarmaco"].replace(drug_description, np.arange(float(len(drug_description))))

# We convert boolean label into numeric value
final_df["label"] = final_df["label"].replace([False, True], [0.0, 1.0])

# And we replace all the remaining NaN values with the value -100 in order to be ignored by the model
final_df = final_df.fillna(-100)

# Reordering feature labels
final_df = final_df.reindex(columns=["sesso", "annodiagnosidiabete", "annoprimoaccesso", "annodecesso", "data", 
                                     "codiceamd", "valore", "codicestitch", "codiceatc", "quantita", "idpasto",
                                     "descrizionefarmaco", "label"])

data = final_df.drop('label',axis=1).values
labels = final_df['label'].values

# Create tensor dataset
dataset = TensorDataset(torch.FloatTensor(data),torch.LongTensor(labels))

# Split between train and test dataset
train_size = 0.8
test_size = 0.2
batch_size = 4

train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

data_loader = DataLoader(train_dataset, batch_size)

# Training step
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

input_size = 13
hidden_size = 32
num_layers = 1
num_classes = 2

model = model.Model(input_size, hidden_size, num_layers, num_classes)

criterion = torch.nn.CrossEntropyLoss()

learning_rate = 0.1

optimizer = torch.optim.Adam(model.parameters(), learning_rate)

num_epochs = 1

def train(num_epochs, data_loader, device, criterion, optimizer):
    for epoch in range(num_epochs):
        for i, (inputs, labels) in enumerate(data_loader):
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(inputs)

            loss = criterion(outputs, labels)
            loss.backward()

            optimizer.step()

            if (i+1) % 10 == 0:
                print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                    .format(epoch+1, num_epochs, i+1, len(dataset)//4, loss.item()))
                
train(num_epochs, data_loader, device, criterion, optimizer)
