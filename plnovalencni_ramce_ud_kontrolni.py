## import potřebných knihoven
from conllu import parse 
import requests
import csv
from locale import LC_NUMERIC
from locale import setlocale

# nastavení "lokality"
setlocale(LC_NUMERIC, "cs_CZ.UTF-8")

# 1. možnost načítání dat: text potřebuju prohnat UDPipem
# zpracování na webu udpipe
data_z_webu = requests.post('http://lindat.mff.cuni.cz/services/udpipe/api/process', data={'tokenizer': "", 'tagger': "", 'parser': ""}, files={"data": open("Dopisy.txt", encoding="UTF-8")}) # odešle požadavek na web
data = data_z_webu.json()['result'] 

# # # uložení výsledků z webu z udpipu
with open("vysledek_udpipe.txt", encoding="UTF-8", mode="w") as soubor: 
    print(data, file=soubor)

# 2. možnost načítání dat: načítám CONLLU výsledek
# with open("vysledek_udpipe.txt", encoding="UTF-8") as soubor:
#         data = soubor.read()

# přechroustání conllu formátu
parsovani = parse(data)


def hledani_predikatu(veta, id_veta): 
    morfo_kategorie_predikatu = ("VB", "Vp", "Vi", "Vs")
    morfo_kategorie_predikatu_jmennych = ("VB", "Vp", "Vs")
    veta_predikaty = []
    veta_predikaty_lemma = []
    veta_s_predikatem_id = []
    plnovalencni_ramce_prazdne = []
 
    for token in veta:
        if token["upos"] == "VERB" and token["xpos"][0:2] in morfo_kategorie_predikatu: 
            veta_predikaty.append(token["id"])

        elif token["upos"] == "AUX" and token["xpos"][0:2] in morfo_kategorie_predikatu_jmennych:
            pomocne_id_headu = token["head"]
            for token_pomocny in veta:
                if token_pomocny["id"] == pomocne_id_headu and token["upos"] == "VERB":
                    veta_predikaty.append(token["id"])
                else:
                    pass 

    veta_hotove_predikaty = sorted(set(veta_predikaty)) 

    for predikat in veta_hotove_predikaty:
        plnovalencni_ramce_prazdne.append([])
        veta_predikaty_lemma += [token["lemma"] for token in veta if token["id"] == predikat] 
        veta_s_predikatem_id += [id_veta for token in veta if token["id"] == predikat]
        print(veta_s_predikatem_id)
        print(veta_predikaty_lemma)

    return veta_hotove_predikaty, veta_predikaty_lemma, plnovalencni_ramce_prazdne, veta_s_predikatem_id


def vytvareni_plnovalecnich_ramcu(veta, id_predikaty, ramce_veta):
    for x, id_pred in enumerate(id_predikaty):
        for token in veta:
            if token["head"] == id_pred and token["deprel"] != "conj":
                ramce_veta[x].append(token["deprel"])
                
    serazene_ramce_veta = []            
    for ramec in ramce_veta:
        serazene_ramce_veta.append(sorted(ramec))

    return serazene_ramce_veta


def ramec_k_zapisu(ramec):
    ramec_string = "[" + ", ".join(ramec) + "]"
    return ramec_string


# chystání proměnných
id_predikaty = []
lemma_predikaty = []
vety_s_pred_id = []
plnovalencni_ramce = []
id_veta = 1

# spouštění cyklu: prochází každou větu a vytváří plnovalenční rámce
for veta in parsovani:
    veta = veta.filter(xpos=lambda x: x != "Z:-------------") # odfiltrování interpunkce

    # hledá predikáty
    veta_id_predikaty, veta_lemma_predikaty, pozice_do_ramcu, veta_s_pred_id = hledani_predikatu(veta, id_veta)

    # vytváří plnovalenční rámce
    plnovalencni_ramce_veta = vytvareni_plnovalecnich_ramcu(veta, veta_id_predikaty, pozice_do_ramcu)

    # ukládá výsledky pro jednotlivé věty do proměnné pro celý text
    id_predikaty.append(veta_id_predikaty) 
    lemma_predikaty.append(veta_lemma_predikaty)
    vety_s_pred_id.append(veta_s_pred_id)
    plnovalencni_ramce.append(plnovalencni_ramce_veta)
    id_veta += 1

# frekvence rámců
plnovalencni_ramce_vsechny = []
for ramce_veta in plnovalencni_ramce:
    for ramec_klauze in ramce_veta:
        plnovalencni_ramce_vsechny.append(tuple(sorted(ramec_klauze))) 

frekvence_plnovalencnich_ramcu = {}
for klic in plnovalencni_ramce_vsechny:
    if klic not in frekvence_plnovalencnich_ramcu:
        frekvence_plnovalencnich_ramcu[klic] = 0
    frekvence_plnovalencnich_ramcu[klic] += 1

# seřazení podle frekvence
serazene_frce = sorted(frekvence_plnovalencnich_ramcu.items(), key=lambda x: x[1], reverse=True)

# uložení frekvencí do souboru
with open("frekvence_rámců.csv", "wt") as csvfile: 
    vysledek_frekvence = csv.writer(csvfile, delimiter=';',lineterminator='\n')
    vysledek_frekvence.writerow(["typ rámce", "frce", "délka rámce"])
    for polozka in serazene_frce:
        ramec = ramec_k_zapisu(polozka[0])
        vysledek_frekvence.writerow([ramec, polozka[1], ramec.count(",")+1])

# spárování lemmatu predikátu a jeho plnovalenčního rámce 
lemma_a_jeho_ramec = []
for x, lemmata_veta in enumerate(lemma_predikaty):
    for y, lemma in enumerate(lemmata_veta):
        lemma_a_jeho_ramec.append((lemma, plnovalencni_ramce[x][y], vety_s_pred_id[x][y]))  

# uložení spárovaného lemmatu a rámce do souboru
with open("lemma_a_rámec.csv", "wt") as csvfile:
    vysledek_sparovani = csv.writer(csvfile, delimiter=';',lineterminator='\n')
    vysledek_sparovani.writerow(["lemma", "rámec", "id_věty"])
    for x, polozka in enumerate(lemma_a_jeho_ramec):
        ramec = ramec_k_zapisu(polozka[1])
        vysledek_sparovani.writerow([polozka[0], ramec, polozka[2]])
        print(vety_s_pred_id)
