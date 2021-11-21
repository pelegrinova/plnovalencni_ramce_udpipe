# plnovalencni_ramce_udpipe
Skript sloužící k vytvoření (a uložení) plnovalenčních rámců (a frekvence jejich typů) na základě automatické syntaktické analýzy nástroje UDPipe. 

Metodologické poznámky:
- plnovalenční rámec obsahuje všechny přímé uzly závisející na určitém tvaru slovesa (kromě interpunkce a koordinovaných přísudků)
- jmenné přísudky nejsou zahrnuty (vzhledem k tomu, že v UDPipe je vrcholem jmenná část přísudku a plnovalenční rámec by pak neodpovídal valenci slovesa, ale jména)

- výstupem jsou dvě tabulky
    - tabulka obsahující typ plnovalenčního rámce a jeho frekvenci
    - tabulka obsahující lemma přísudku a valenční rámec (rámce), se kterým(i) se pojí
