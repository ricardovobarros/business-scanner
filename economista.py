from config import *


class Economista:
    def __init__(self, data=""):
        # attributes
        self.data = data
        self.balanco = pd.DataFrame()
        self.dr = pd.DataFrame()
        self.indices = pd.DataFrame()
        self.indices = pd.DataFrame()

        # call methods
        self.compute_balanco()
        self.compute_dr()
        self.compute_indices()

    def compute_balanco(self):
        # compute balanco
        self.capital_de_giro()
        self.credito_longo_prazo()
        self.ativo_permanente()
        self.capital_terceiros()
        self.debito_longo()
        self.capital_proprio()
        self.compte_adicional()

        pass

    def compute_dr(self):
        pass

    def compute_indices(self):
        pass

    def capital_de_giro(self):
        id_list = ["SFM", "SFD_01", "SDDG", "SDAG_01",
                   "SPA_01", "SFA", "SSEP", "SEA_01", "SAC_02"]

        self.balanco = self.data[self.data["id"].isin(id_list)]
        self.balanco["pas/ati"] = "passivo"
        self.balanco["tipo"] = "capital de terceiros"

        # cleaning strings
        self.balanco["descricao"] = self.balanco["descricao"].str.replace("- até 12 meses adiante", "")
        pass

    def credito_longo_prazo(self):
        id_list = ["SCPC", "SCRD", "SCCR_02"]
        df_lp = self.data[self.data["id"].isin(id_list)]
        df_lp["pas/ati"] = "ativo"
        df_lp["tipo"] = "crédito a longo prazo"

        # concatenate to the balanco dataframe
        self.balanco = pd.concat([self.balanco, df_lp], ignore_index=True)

        pass

    def ativo_permanente(self):
        id_list = ["VID", "SAEP", "VMNS", "VSET", "VVP"]
        df_ap = self.data[self.data["id"].isin(id_list)]
        df_ap["pas/ati"] = "ativo"
        df_ap["tipo"] = "ativo permanente"

        # concatenate to the balanco dataframe
        self.balanco = pd.concat([self.balanco, df_ap], ignore_index=True)

        pass

    def capital_terceiros(self):
        id_list = ["SFM", "SFD_01", "SDDG", "SDAG_01", "SPA_01", "SFA", "SSEP",
                   "SEA_01", "SAC_02"]
        df_ct = self.data[self.data["id"].isin(id_list)]
        df_ct["pas/ati"] = "passivo"
        df_ct["tipo"] = "capital de terceiros"

        # concatenate to the balanco dataframe
        self.balanco = pd.concat([self.balanco, df_ct], ignore_index=True)
        pass

    def debito_longo(self):
        #TODO: 1. modify the velue of debitos futuros. Parec um input ate agora
        id_list = ["SFM"]  # MODIFICAR'
        df_dl = self.data[self.data["id"].isin(id_list)]  # MODIFICAR
        df_dl["pas/ati"] = "passivo"
        df_dl["tipo"] = "debitos futuros de longo prazo"

        # concatenate to the balanco dataframe
        self.balanco = pd.concat([self.balanco, df_dl], ignore_index=True)
        pass

    def capital_proprio(self):
        # copute capital proprio
        ativos = self.balanco[self.balanco["pas/ati"] == "ativo"].sum(axis=0)[2:14]
        capital_de_terceiros = self.balanco[(self.balanco["pas/ati"] == "passivo")
                                            &(self.balanco["tipo"] == "capital de terceiros")].sum(axis=0)[2:14]
        debito_longo_prazo = self.balanco[self.balanco["tipo"] == "debitos futuros de longo prazo"].sum(axis=0)[2:14]
        lucro_liquido_final = 0 # TODO: modificar esse valor para valor real da DR
        capital_social_subscrito = 0 # TODO: modificar esse valor para valor real da DR
        capital_proprio = ativos - (capital_de_terceiros
                                    + debito_longo_prazo
                                    + lucro_liquido_final
                                    + capital_social_subscrito
                                    )

        # id_list = ["SFM"]  # MODIFICAR'
        # df_dl = self.data[self.data["id"].isin(id_list)]  # MODIFICAR
        # df_dl["pas/ati"] = "passivo"
        # df_dl["tipo"] = "debitos futuros de longo prazo"

        # concatenate to the balanco dataframe
        # self.balanco = pd.concat([self.balanco, df_dl], ignore_index=True)
        pass

    def compte_adicional(self):
        pass
