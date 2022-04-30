from config import *


class Economista:
    def __init__(self, data=""):
        # attributes
        self.data = data
        self.balanco = pd.DataFrame()
        self.dr = pd.DataFrame()
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
        id_list = ["SC", "SB", "SAF", "SCC", "SCR", "SCCR_01", "SCA",
                   "SAAF", "SIR", "VEM"]

        self.balanco = self.data[self.data["id"].isin(id_list)]
        self.balanco["pas/ati"] = "ativo"
        self.balanco["tipo"] = "capital de giro"

        # cleaning strings
        # self.balanco["descricao"] = self.balanco["descricao"].str.replace("- até 12 meses adiante", "")
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
        # TODO: 1. modify the velue of debitos futuros. Parec um input ate agora
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
                                            & (self.balanco["tipo"] == "capital de terceiros")].sum(axis=0)[2:14]
        debito_longo_prazo = self.balanco[self.balanco["tipo"] == "debitos futuros de longo prazo"].sum(axis=0)[2:14]
        redultado_exercicio = 1  # TODO: modificar esse valor para valor real da DR
        capital_social_subscrito = 1  # TODO: modificar esse valor para valor real da DR
        capital_proprio = ativos - (capital_de_terceiros
                                    + debito_longo_prazo
                                    + redultado_exercicio
                                    + capital_social_subscrito
                                    )
        # transform in dataframe
        df_cp = pd.DataFrame(data=[capital_proprio.values], columns=capital_proprio.index)
        df_cp["pas/ati"] = "passivo"
        df_cp["tipo"] = "capital proprio"
        df_cp["descricao"] = "capital proprio estimado"
        df_cp["id"] = "CPEST"

        # include capital proprio in balanco
        self.balanco = pd.concat([self.balanco, df_cp])
        pass

    def compte_adicional(self):
        # compute difference active and passive
        ativos = self.balanco[self.balanco["pas/ati"] == "ativo"].sum(axis=0)[2:14]
        passivo = self.balanco[self.balanco["pas/ati"] == "passivo"].sum(axis=0)[2:14]
        dif_ati_pas = ativos - passivo
        df_dap = pd.DataFrame(data=[dif_ati_pas.values], columns=dif_ati_pas.index)
        df_dap["descricao"] = "diferenca entre ativo e passivo"
        df_dap["id"] = "DATPAS"

        # compute capital de giro %
        capital_giro = self.balanco[self.balanco["tipo"] == "capital de giro"].sum(axis=0)[2:14]
        capital_per = capital_giro / ativos
        df_cg = pd.DataFrame(data=[capital_per.values], columns=capital_per.index)
        df_cg["descricao"] = "capital de giro porcentagem"
        df_cg["id"] = "CAPGPOR"

        # Compute Estoque de mercadoria/capital de giro
        estoque_mercado = self.balanco[self.balanco["id"] == "VEM"].iloc[:, 2:14].squeeze()
        estoque_capital = estoque_mercado / capital_giro
        df_em = pd.DataFrame(data=[estoque_capital.values], columns=estoque_capital.index)
        df_em["descricao"] = "estoque/capital de giro"
        df_em["id"] = "ESDCG"

        # Compute clientes/capital de giro
        id_list = ["SCR", "SCCR_01", "SCA"]
        clientes = self.balanco[self.balanco["id"].isin(id_list)].iloc[:, 2:14].sum(axis=0)
        clientes_giro = clientes / capital_giro
        df_clig = pd.DataFrame(data=[clientes_giro.values], columns=clientes_giro.index)
        df_clig["descricao"] = "clientes/capital de giro"
        df_clig["id"] = "CDCG"

        # compute disponibilidades/capital de giro
        id_list_02 = ["SC", "SB"]
        disponivel = self.balanco[self.balanco["id"].isin(id_list_02)].iloc[:, 2:14].sum(axis=0)
        disp_capit = disponivel / capital_giro
        df_dv = pd.DataFrame(data=[disp_capit.values], columns=disp_capit.index)
        df_dv["descricao"] = "disponivel/capital de giro"
        df_dv["id"] = "DDCG"

        # estoques/ativos
        estoque_ativo = estoque_mercado / ativos
        df_ea = pd.DataFrame(data=[estoque_ativo.values], columns=estoque_ativo.index)
        df_ea["descricao"] = "estoque/ativos"
        df_ea["id"] = "EDAT"

        # grau de individamento
        capital_proprio = self.balanco[self.balanco["tipo"] == "capital proprio"].sum(axis=0)[2:14]
        capital_terceiros = self.balanco[self.balanco["tipo"] == "capital de terceiros"].sum(axis=0)[2:14]
        grau_individamento = capital_terceiros / capital_proprio
        df_gi = pd.DataFrame(data=[grau_individamento.values], columns=grau_individamento.index)
        df_gi["descricao"] = "grau de individamento"
        df_gi["id"] = "GDIND"

        # despesas totais
        despesas_totais = capital_terceiros
        df_dt = pd.DataFrame(data=[despesas_totais.values], columns=despesas_totais.index)
        df_dt["descricao"] = "despesas totais"
        df_dt["id"] = "DESTO"

        # append new data into balanco
        df_final = pd.concat([df_cg, df_dt, df_em, df_dap, df_clig, df_gi, df_dv, df_ea])
        df_final["pas/ati"] = "outros"
        df_final["tipo"] = "outros"
        self.balanco = pd.concat([self.balanco, df_final])

        pass
