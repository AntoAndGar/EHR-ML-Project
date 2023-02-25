import pandas as pd
from datetime import date


def printSexInfo(dataset):
    print("Sex info")
    print(dataset["sesso"].unique())
    print(dataset["sesso"].isna().sum())
    print(sum(dataset["sesso"].isin(["M"])))


#    dataset['sesso'].plot(kind='kde')


def getDeaseasePercentage(dataset, deaseases):
    print("Deasease: ", deaseases)
    # print(dataset.columns)
    percent = "\nPercentage of deasease:\n"
    for deasease in deaseases:
        # print("Deasease: ", deasease)
        tempdataset = dataset[dataset["codiceamd"].isin([deasease])]
        tempdataset2 = tempdataset["key"].unique()
        percent += (
            deasease
            + ": "
            + str(len(tempdataset2) / len(dataset["key"].unique()) * 100)
            + "%\n"
        )
    print(percent)


def getInfoOnDiagnosi(df):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Info on diagnosi")
    dates = ["annodiagnosidiabete", "annonascita", "annoprimoaccesso", "annodecesso"]
    stampami = dict()
    for d in dates:
        df["extra"] = df["data"].dropna().str[:4]
        df["extra"] = df["extra"].astype(float)
        minor = (df[d].astype(float) < df["extra"]).sum()
        equal = (df[d].astype(float) == df["extra"]).sum()
        more = (df[d].astype(float) > df["extra"]).sum()
        stampami[d] = [minor, equal, more]

    print(stampami)


# import the data
df_diagnosi = pd.read_csv("sample/diagnosi.csv", header=0)

"""
AMD047: Myocardial infarction
AMD048: Coronary angioplasty
AMD049: Coronary bypass
AMD071: Ictus
AMD081: Lower limb angioplasty
AMD082: Peripheral By-pass Lower Limbs
AMD208: Revascularization of intracranial and neck vessels
AMD303: Ischemic stroke
"""
wanted_amd = [
    "AMD047",
    "AMD048",
    "AMD049",
    "AMD071",
    "AMD081",
    "AMD082",
    "AMD208",
    "AMD303",
]

df_diagnosi["key"] = (
    df_diagnosi["idana"].astype(str) + "-" + df_diagnosi["idcentro"].astype(str)
)

print("numero record presenti in diagnosi: ", len(df_diagnosi["key"]))
print("numero pazienti unici presenti in diagnosi: ", len(df_diagnosi["key"].unique()))

df_anagrafica_attivi = pd.read_csv("sample/anagraficapazientiattivi.csv", header=0)

df_anagrafica_attivi["key"] = (
    df_anagrafica_attivi["idana"].astype(str)
    + "-"
    + df_anagrafica_attivi["idcentro"].astype(str)
)

print("numero record presenti in anagrafica: ", len(df_anagrafica_attivi["key"]))
print(
    "numero pazienti unici in anagrafica: ", len(df_anagrafica_attivi["key"].unique())
)

print(
    "numero pazienti in anagrafica presenti in diagnosi:",
    len(
        set(df_anagrafica_attivi["key"].unique()).intersection(
            set(df_diagnosi["key"].unique())
        )
    ),
)

df_problemi_cuore = df_diagnosi[df_diagnosi["codiceamd"].isin(wanted_amd)]
print(
    "numero pazienti presenti in diagnosi con codice amd in lista (problemi al cuore): ",
    len(df_problemi_cuore["key"].unique()),
)
print("Valori presenti:", df_problemi_cuore["valore"].unique())

print(
    "numero pazienti con anno diagnosi diabete minore dell'anno di nascita: ",
    sum(
        df_anagrafica_attivi["annodiagnosidiabete"]
        < df_anagrafica_attivi["annonascita"]
    ),
)

print(
    "numero pazienti con anno primo accesso minore dell'anno di nascita: ",
    sum(df_anagrafica_attivi["annoprimoaccesso"] < df_anagrafica_attivi["annonascita"]),
)

print(
    "numero pazienti con anno decesso minore dell'anno di nascita: ",
    sum(df_anagrafica_attivi["annodecesso"] < df_anagrafica_attivi["annonascita"]),
)

# print(
#     "pazienti con anno decesso maggiore dell'anno di nascita: ",
#     df_anagrafica_attivi[
#         df_anagrafica_attivi["annodecesso"] < df_anagrafica_attivi["annonascita"]
#     ],
# )

print(
    "numero pazienti con anno decesso maggiore dell'anno 2022: ",
    sum(df_anagrafica_attivi["annodecesso"] > 2022),
)

print(
    "numero pazienti con anno di nascita negativo: ",
    sum(df_anagrafica_attivi["annonascita"] < 0),
)

print(
    "numero pazienti con anno primo accesso maggiore dell'anno decesso: ",
    sum(df_anagrafica_attivi["annoprimoaccesso"] > df_anagrafica_attivi["annodecesso"]),
)

# print(
#     "pazienti con anno primo accesso maggiore dell'anno decesso: ",
#     df_anagrafica_attivi[
#         df_anagrafica_attivi["annoprimoaccesso"] > df_anagrafica_attivi["annodecesso"]
#     ],
# )

print(
    "numero pazienti con anno diagnosi diabete maggiore dell'anno decesso: ",
    sum(
        df_anagrafica_attivi["annodiagnosidiabete"]
        > df_anagrafica_attivi["annodecesso"]
    ),
)

# print(
#     "pazienti con anno diagnosi diabete maggiore dell'anno decesso: ",
#     df_anagrafica_attivi[
#         df_anagrafica_attivi["annodiagnosidiabete"]
#         > df_anagrafica_attivi["annodecesso"]
#     ],
# )

print(
    "numero pazienti con anno diagnosi diabete a N/A: ",
    sum(df_anagrafica_attivi["annodiagnosidiabete"].isna()),
)

# in anagrafica abbiamo solo pazienti con diagnosi di diabete di tipo 2 valore 5 in 'tipodiabete'
# quindi possiamo fillare l'annodiagnosidiabete con l'annoprimoaccesso

print(
    sum(
        [
            1
            for el in df_anagrafica_attivi[
                df_anagrafica_attivi["annodiagnosidiabete"].isna()
                & df_anagrafica_attivi["annoprimoaccesso"].notnull()
            ]["key"]
        ]
    )
)


print("tipi possibili di diabete: ", df_anagrafica_attivi["tipodiabete"].unique())

aa_prob_cuore = pd.merge(
    df_anagrafica_attivi, df_problemi_cuore, on=["idcentro", "idana", "key"]
)

print(
    "numero pazienti con problemi al cuore: ",
    sum([1 for elem in aa_prob_cuore["key"].unique()]),
)


print("info dataframe pazienti con problemi al cuore: ")
print(aa_prob_cuore.info())

# questi son tutti a 0 quindi li commento
# print(sum(aa_prob_cuore["annodiagnosidiabete"] < aa_prob_cuore["annonascita"]))  # 0
# print(sum(aa_prob_cuore["annoprimoaccesso"] < aa_prob_cuore["annonascita"]))  # 0
# print(sum(aa_prob_cuore["annodecesso"] < aa_prob_cuore["annonascita"]))  # 0
# print(sum(aa_prob_cuore["annodecesso"] > 2022))  # 0
# print(sum(aa_prob_cuore["annonascita"] < 0))  # 0

# 7 pazienti hanno la data di primo accesso maggiore della data di decesso -> da scartare
print(
    "numero righe con data di primo accesso maggiore della data di decesso: ",
    sum(aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]),
)  # 14 righe di cui 7 unici

print(
    "numero pazienti unici con data di primo accesso maggiore della data di decesso: ",
    sum(
        [
            1
            for elem in aa_prob_cuore[
                aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]
            ]["key"].unique()
        ]
    ),
)

# 5 pazienti hanno la data di diagnosi di diabete maggiore della data di decesso -> da scartare
print(
    "numero righe con data di diagnosi di diabete maggiore della data di decesso: ",
    sum(aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]),
)  # 9 righe di cui 5 unici

print(
    "numero pazienti unici con data di diagnosi di diabete maggiore della data di decesso: ",
    sum(
        [
            1
            for elem in aa_prob_cuore[
                aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]
            ]["key"].unique()
        ]
    ),
)

print(
    "numero righe con anno diagnosi diabete a N/A: ",
    sum(aa_prob_cuore["annodiagnosidiabete"].isna()),
)  # 2234

print(
    "numero pazienti unici con anno diagnosi diabete a N/A: ",
    sum(
        [
            1
            for elem in aa_prob_cuore[aa_prob_cuore["annodiagnosidiabete"].isna()][
                "key"
            ].unique()
        ]
    ),
)  # 526

# in anagrafica abbiamo solo pazienti con diagnosi di diabete di tipo 2 valore 5 in 'tipodiabete'
# quindi possiamo fillare l'annodiagnosidiabete con l'annoprimoaccesso
print(
    "numero righe con anno diagnosi diabete a N/A ma con anno primo accesso presente: ",
    sum(
        [
            1
            for el in aa_prob_cuore[
                aa_prob_cuore["annodiagnosidiabete"].isna()
                & aa_prob_cuore["annoprimoaccesso"].notnull()
            ]["key"]
        ]
    ),
)  # 1797

getInfoOnDiagnosi(aa_prob_cuore)
# Sesso
printSexInfo(df_anagrafica_attivi)
# Deasease Distribution
getDeaseasePercentage(df_problemi_cuore, wanted_amd)

aa_prob_cuore.drop(
    aa_prob_cuore[
        aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]
    ].index,
    inplace=True,
)
print(sum([1 for elem in aa_prob_cuore["key"].unique()]))
aa_prob_cuore.drop(
    aa_prob_cuore[
        aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]
    ].index,
    inplace=True,
)

print("dopo scarto :")
print(sum([1 for elem in aa_prob_cuore["key"].unique()]))

# siccome più della metà dei pazienti che hanno problemi al cuore
# hanno l'anno di diagnosi di diabete minore dell'anno di primo accesso
# noi abbiamo deciso di fillare l'annodiagnosidiabete con l'anno primo accesso
print(
    sum(
        [
            1
            for elem in aa_prob_cuore[
                aa_prob_cuore["annodiagnosidiabete"] < aa_prob_cuore["annoprimoaccesso"]
            ]["key"].unique()
        ]
    )
)  # 27592

aa_prob_cuore.loc[
    aa_prob_cuore["annodiagnosidiabete"].isna()
    & aa_prob_cuore["annoprimoaccesso"].notnull(),
    "annodiagnosidiabete",
] = aa_prob_cuore["annoprimoaccesso"]

print("All filtered :")
aa_prob_cuore.dropna(subset="annodiagnosidiabete", inplace=True)
print(sum([1 for elem in aa_prob_cuore["key"].unique()]))  # 49829

# df_esami_par = pd.read_csv('sample/esamilaboratorioparametri.csv')
# df_esami_par_cal = pd.read_csv('sample/esamilaboratorioparametricalcolati.csv')
df_esami_stru = pd.read_csv("sample/esamistrumentali.csv")

wanted_amd_par = ["AMD004", "AMD005", "AMD006", "AMD007", "AMD008", "AMD009", "AMD111"]
wanted_stitch_par = ["STITCH001", "STITCH002", "STITCH003", "STITCH004", "STITCH005"]

aa_cuore_key = aa_prob_cuore[["idana", "idcentro"]]
aa_cuore_key = aa_cuore_key.drop_duplicates()

df_esami_stru = df_esami_stru.groupby(["idana", "idcentro"], as_index=False).agg(
    {"data": ["min", "max"]}
)
df_esami_stru.head()
### RIMUOVI I PAZIENTI CON TUTTI GLI EVENTI NELLO STESSO MESE
df_esami_stru["data_min"] = pd.to_datetime(
    df_esami_stru["data"]["min"], format="%Y-%m-%d"
)
df_esami_stru["data_max"] = pd.to_datetime(
    df_esami_stru["data"]["max"], format="%Y-%m-%d"
)

df_esami_stru.info()
df_esami_stru["diff"] = df_esami_stru["data_max"] - df_esami_stru["data_min"]
print(len(df_esami_stru))
print(len(df_esami_stru[df_esami_stru["diff"] < pd.Timedelta("30 days")]))
print(len(df_esami_stru[df_esami_stru["diff"] == pd.Timedelta("0 days")]))

df_esami_stru = df_esami_stru[df_esami_stru["diff"] > pd.Timedelta("30 days")]
df_esami_stru = df_esami_stru.sort_values(by=["diff"])
print(df_esami_stru.head())
print(df_esami_stru.tail())


###togliere dal dataframe principale ciò che non è in df_esami_stru
df_esami_stru_key = df_esami_stru[["idana", "idcentro"]].drop_duplicates()
aa_prob_cuore_filtered = pd.merge(
    aa_prob_cuore,
    df_esami_stru_key,
    on=["idana", "idcentro"],
    how="inner",
)
print(aa_prob_cuore_filtered)
print(len(aa_prob_cuore_filtered))
print(len(aa_prob_cuore_filtered[["idana", "idcentro"]].drop_duplicates()))
# int_df = pd.merge(d1, d2, how ='inner', on =['A', 'B'])


### TODO: Punto 4
df_esami_lab_par = pd.read_csv("sample/esamilaboratorioparametri.csv")

print("prima update: ")
amd004 = df_esami_lab_par[df_esami_lab_par["codiceamd"] == "AMD004"]["valore"]
print("numero AMD004 minori di 40: ", len(amd004[amd004.astype(float) < 40]))
print("numero AMD004 maggiori di 200: ", len(amd004[amd004.astype(float) > 200]))


df_esami_lab_par["valore"].update(
    df_esami_lab_par[df_esami_lab_par["codiceamd"] == "AMD004"]["valore"].clip(40, 200)
)
df_esami_lab_par["valore"].update(
    df_esami_lab_par[df_esami_lab_par["codiceamd"] == "AMD005"]["valore"].clip(40, 130)
)
df_esami_lab_par["valore"].update(
    df_esami_lab_par[df_esami_lab_par["codiceamd"] == "AMD007"]["valore"].clip(50, 500)
)
df_esami_lab_par["valore"].update(
    df_esami_lab_par[df_esami_lab_par["codiceamd"] == "AMD008"]["valore"].clip(5, 15)
)

print("dopo update: ")
amd004_dopo = df_esami_lab_par[df_esami_lab_par["codiceamd"] == "AMD004"]["valore"]

print("numero AMD004 minori di 40: ", len(amd004_dopo[amd004_dopo < 40]))
print(
    "numero AMD004 maggiori di 200: ", len(amd004_dopo[amd004_dopo.astype(float) > 200])
)

df_esami_lab_par_calcolati = pd.read_csv(
    "sample/esamilaboratorioparametricalcolati.csv"
)

print("prima update: ")

stitch002 = df_esami_lab_par_calcolati[
    df_esami_lab_par_calcolati["codicestitch"] == "STITCH002"
]["valore"]
print("numero STITCH001 minori di 30: ", len(stitch002[stitch002.astype(float) < 30]))
print(
    "numero STITCH001 maggiori di 300: ", len(stitch002[stitch002.astype(float) > 300])
)

df_esami_lab_par_calcolati["valore"].update(
    df_esami_lab_par_calcolati[
        df_esami_lab_par_calcolati["codicestitch"] == "STITCH002"
    ]["valore"].clip(30, 300)
)
df_esami_lab_par_calcolati["valore"].update(
    df_esami_lab_par_calcolati[
        df_esami_lab_par_calcolati["codicestitch"] == "STITCH003"
    ]["valore"].clip(60, 330)
)

stitch002_dopo = df_esami_lab_par_calcolati[
    df_esami_lab_par_calcolati["codicestitch"] == "STITCH002"
]["valore"]


print(
    "numero STITCH001 minori di 30: ",
    len(stitch002_dopo[stitch002_dopo < 30]),
)
print(
    "numero STITCH001 maggiori di 300: ",
    len(stitch002_dopo[stitch002_dopo.astype(float) > 300]),
)


### TODO: Punto 5

# questa roba che ho scritto non sembra funzionare come mi aspetterei
# print(
#     sum(
#         [
#             1
#             for elem in aa_prob_cuore_filtered[["idana", "idcentro"]]
#             .groupby(["idana", "idcentro"], group_keys=True)
#             .count()
#             < 2
#         ]
#     )
# )

# print(
#     aa_prob_cuore_filtered[["idana", "idcentro"]]
#     .groupby(["idana", "idcentro"], group_keys=True)
#     .count()
# )


### TODO: Punto 6