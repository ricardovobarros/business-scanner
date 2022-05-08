from config import *


class Economista:
    def __init__(self, data="", simples=False):
        # attributes
        self.repeted_ids = []
        self.data = data
        self.balanco = pd.DataFrame()
        self.dr = pd.DataFrame()
        self.dr_unique = pd.DataFrame()
        self.indices = pd.DataFrame()
        self.id_unique = []
        self.id_nonunique = []
        if simples:
            self.irpj = 1
        else:
            self.irpj = 0  # TODO: definir valor para empresa simples

        # call methods
        self.compute_dr()
        self.compute_dr_unique()
        self.compute_balanco()
        self.compute_indices()

    def compute_balanco(self):
        # compute balanco
        self.capital_de_giro()
        self.credito_longo_prazo()
        self.ativo_permanente()
        self.capital_terceiros()
        self.debito_longo()
        self.capital_proprio()
        self.compute_adicional()

        pass

    def compute_dr(self):
        # list the entries that have unique code
        id_list_unique = ["LS", "C", "TR", "IM", "SM", "CT", "CN", "IC", "PI",
                          "CO", "IS", "SN", "CV", "CI", "PL", "JMRC", "RAF", "ORF",
                          "DF_01", "GG_21", "GG_22", "DF_02", "PCNPJ", "GG_19",
                          "GG_20", "MK_01", "DL", "VI", "AS", "REB", "RET", "RES",
                          "DL", "OEO"]

        # list entries that have no unique code
        id_list_nonunique = ["PE", "GG", "MK", "DF", "IN"]

        # assign to attributes of the class
        self.id_unique = id_list_unique
        self.id_nonunique = id_list_nonunique

        # get values for unique list
        df_unique = self.data[self.data["id"].isin(id_list_unique)]
        df_nonunique = self.data[self.data["id"].str.contains('|'.join(id_list_nonunique))]

        # sum non unique values and rename them
        names = ["PE", "GG", "MK", "DF", "IN"]
        description = ["Pessoal e Encargos", "Gastos Gerais", "Marketing", "Despesas Financeiras",
                       "Investimentos Totais"]

        # compute receita bruta
        id_list_rb = ["LS", "C", "TR", "IM", "SM", "CT", "CN"]
        self.dr = pd.concat([self.dr, df_unique[df_unique["id"].isin(id_list_rb)]])
        df = self.dr.sum(axis=0).squeeze()
        df.loc["descricao"] = "Receita Bruta"
        df.loc["id"] = "DR_RB"
        df = pd.DataFrame(data=[df.values], columns=df.index)
        self.dr = pd.concat([self.dr, df])

        # deducao sobre receitas
        id_list_dsr = ["IC", "PI", "CO", "IS", "SN"]
        df1 = df_unique[df_unique["id"].isin(id_list_dsr)]
        s = df1.sum(axis=0).squeeze()
        s.loc["descricao"] = "Deducao Sobre Receita"
        s.loc["id"] = "DR_DSR"
        s = pd.DataFrame(data=[s.values], columns=s.index)
        self.dr = pd.concat([self.dr, df1, s])

        # compute receita liquida
        df_values = self.dr[self.dr["id"].isin(["DR_RB", "DR_DSR"])].iloc[:, 2:14]
        df2 = df_values.iloc[0, :] - df_values.iloc[1, :]
        df2.loc["id"] = "DR_RL"
        df2.loc["descricao"] = "Receita Liquida"
        df2 = pd.DataFrame(data=[df2.values], columns=df2.index)
        self.dr = pd.concat([self.dr, df2])

        # compute custo variavel
        id_list_cv = ["CV", "CI"]
        df3 = df_unique[df_unique["id"].isin(id_list_cv)]
        s = df3.sum(axis=0).squeeze()
        s.loc["descricao"] = "Custo Variavel"
        s.loc["id"] = "DR_CV"
        s = pd.DataFrame(data=[s.values], columns=s.index)
        self.dr = pd.concat([self.dr, df3, s])

        # compute margem de contribuicao
        df_values = self.dr[self.dr["id"].isin(["DR_RL", "DR_CV"])].iloc[:, 2:14]
        df4 = df_values.iloc[0, :] - df_values.iloc[1, :]
        df4.loc["id"] = "DR_MC"
        df4.loc["descricao"] = "Margen de Contribuicao"
        df4 = pd.DataFrame(data=[df4.values], columns=df4.index)
        self.dr = pd.concat([self.dr, df4])

        # Despesa fixa
        id_list_df_var = ["PE", "GG", "MK", "DF"]
        id_list_df = ["PL"]
        df5 = df_nonunique[df_nonunique["id"].str.contains('|'.join(id_list_df_var))]
        df5 = pd.concat([df5, df_unique[df_unique["id"].isin(id_list_df)]])
        s = df5.sum(axis=0).squeeze()
        s.loc["descricao"] = "Despesa Fixa"
        s.loc["id"] = "DR_DF"
        s = pd.DataFrame(data=[s.values], columns=s.index)
        self.dr = pd.concat([self.dr, df5, s])

        # Lucro Bruto
        df_values = self.dr[self.dr["id"].isin(["DR_MC", "DR_DF"])].iloc[:, 2:14]
        df6 = df_values.iloc[0, :] - df_values.iloc[1, :]
        df6.loc["id"] = "DR_LB"
        df6.loc["descricao"] = "Lucro Bruto Operacional"
        df6 = pd.DataFrame(data=[df6.values], columns=df6.index)
        self.dr = pd.concat([self.dr, df6])

        # Receitas Financeiras
        id_list_rf = ['JMRC', 'RAF', 'ORF']
        df7 = df_unique[df_unique["id"].isin(id_list_rf)]
        s = df7.sum(axis=0).squeeze()
        s.loc["descricao"] = "Receitas Financeiras"
        s.loc["id"] = "DR_RF"
        s = pd.DataFrame(data=[s.values], columns=s.index)
        self.dr = pd.concat([self.dr, df7, s])

        # Despesas Financeiras
        id_list_dff = ['DF_01', 'GG_21', 'GG_22', 'DF_02']
        df8 = df_unique[df_unique["id"].isin(id_list_dff)]
        s = df8.sum(axis=0).squeeze()
        s.loc["descricao"] = "Despesas Financeiras"
        s.loc["id"] = "DR_DFIN"
        s = pd.DataFrame(data=[s.values], columns=s.index)
        self.dr = pd.concat([self.dr, df8, s])

        # Compute Resultado da Tesouraria
        id_list_ct = ['VI', 'AS', 'REB', 'RET', 'RES', 'DL', 'OEO']
        df_ct = df_unique[df_unique["id"].isin(id_list_ct)]
        s_ct = df_ct.sum(axis=0).squeeze()
        s_ct.loc["descricao"] = "Resultado de Caixa Tesouraria"
        s_ct.loc["id"] = "DR_RCT"
        s_ct = pd.DataFrame(data=[s_ct.values], columns=s_ct.index)

        # Lucro Bruto antes do IRPJ e CSLL
        df_values = self.dr[self.dr["id"].isin(["DR_LB", "DR_RF"])].iloc[:, 2:14]
        df9 = df_values.iloc[0, :] - df_values.iloc[1, :] + s_ct.iloc[:, 2:14]
        df9 = df9.squeeze()
        df9["id"] = "DR_LBIC"
        df9["descricao"] = "Lucro Bruto antes do IRPJ e CSLL"
        df9 = pd.DataFrame(data=[df9.values], columns=df9.index)
        self.dr = pd.concat([self.dr, df9])

        # adionar IRPJ/CSS

        # Lucro Liquido Final
        df10 = self.dr[self.dr["id"] == "DR_LBIC"].iloc[:, 2:14] # - self.irpj  # TODO: Compute simples () and add to the dr table
        df10["id"] = "DR_LLF"
        df10["descricao"] = "Lucro Liquido Final"
        self.dr = pd.concat([self.dr, df10])

        # Resultado de Caixa de tesouraria
        id_list_ctup = ['PCNPJ', 'GG_19', 'GG_20', 'MK_01', 'PL', 'DL']
        id_list_ctup_var = "IN"
        df_ctupin = df_nonunique[df_nonunique["id"].str.contains(id_list_ctup_var)]
        df_ctup = pd.concat([df, df_unique[df_unique["id"].isin(id_list_ctup)]])
        s_ctup = df_ctup.sum(axis=0).squeeze()
        self.dr = pd.concat([self.dr, df_ctup, df_ctupin, df_ct, s_ct])

        # Ponto de equilibrio economico
        df_dr = self.dr[self.dr["id"].str.contains("DR_")]
        s_mc = df_dr[df_dr["id"] == "DR_MC"].iloc[:, 2:14] / df_dr[df_dr["id"] == "DR_RL"].iloc[:, 2:14]
        s_lucro_desejado = self.data[self.data["id"] == "LD"].iloc[:, 2:14]

        # compute pontos de equilibrio
        s_pef = df_dr[df_dr["id"] == "DR_DF"].iloc[:, 2:14] / s_mc

        s_pee = pd.concat([df_dr[df_dr["id"] == "DR_DF"].iloc[:, 2:14], s_lucro_desejado]).sum(axis=0) / s_mc
        s_pec = pd.concat([df_dr[df_dr["id"] == "DR_DF"].iloc[:, 2:14],
                           df_dr[df_dr["id"] == "DR_RF"].iloc[:, 2:14] * (-1),
                           df_dr[df_dr["id"] == "DR_DFIN"].iloc[:, 2:14],
                           df_ctup.iloc[:, 2:14], df_ctupin.iloc[:, 2:14],
                           df_ct.iloc[:, 2:14] * (-1)
                           ]).sum(axis=0) / s_mc

        # name pontos de equilibrio
        s_pef["id"] = "DR_PEF"
        s_pee["id"] = "DR_PEE"
        s_pec["id"] = "DR_PEC"
        s_pef["descricao"] = "Ponto de Equilibrio Financeiro"
        s_pee["descricao"] = "Ponto de Equilibrio Economico"
        s_pec["descricao"] = "Ponto de Equilibrio de Caixa"

        # add pontos de equilibrio
        self.dr = pd.concat([self.dr, s_pef, s_pee, s_pec]).reset_index(drop=True)

        pass

    def compute_dr_unique(self):
        df = pd.DataFrame(self.dr["id"].value_counts() > 1)
        self.repeted_ids = df[df["id"] == True].index
        self.dr_unique = self.dr.drop_duplicates("id")
        pass

    def compute_indices(self):
        pass

    def capital_de_giro(self):
        id_list = ["SC", "SB", "SAF", "SCR", "SCCR_01", "SCA",
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
        df_ct.loc[:, "pas/ati"] = "passivo"
        df_ct.loc[:, "tipo"] = "capital de terceiros"

        # concatenate to the balanco dataframe
        self.balanco = pd.concat([self.balanco, df_ct], ignore_index=True)
        pass

    def debito_longo(self):
        id_list = ["DFLP"]
        df_dl = self.data[self.data["id"].isin(id_list)]
        df_dl["pas/ati"] = "passivo"
        df_dl["tipo"] = "debitos futuros de longo prazo"

        # concatenate to the balanco dataframe
        self.balanco = pd.concat([self.balanco, df_dl], ignore_index=True)
        pass

    def capital_proprio(self):
        # copute capital proprio
        id_list = ["CSSB"]
        ativos = self.balanco[self.balanco["pas/ati"] == "ativo"].sum(axis=0)[2:14]
        capital_de_terceiros = self.balanco[(self.balanco["pas/ati"] == "passivo")
                                            & (self.balanco["tipo"] == "capital de terceiros")].sum(axis=0)[2:14]
        debito_longo_prazo = self.balanco[self.balanco["tipo"] == "debitos futuros de longo prazo"].sum(axis=0)[2:14]
        resultado_exercicio = self.dr[self.dr["id"] =="DR_LLF"].iloc[:, 2:14].squeeze()  # TODO: modificar esse valor para valor real da DR
        capital_social_subscrito = self.data[self.data["id"].isin(id_list)].iloc[:, 2:14].squeeze()
        capital_proprio = ativos - (capital_de_terceiros
                                    + debito_longo_prazo
                                    + resultado_exercicio
                                    + capital_social_subscrito
                                    )
        # transform in dataframe
        df_cp = pd.DataFrame(data=[capital_proprio.values], columns=capital_proprio.index)
        df_cp["pas/ati"] = "passivo"
        df_cp["tipo"] = "capital proprio"
        df_cp["descricao"] = "capital proprio estimado"
        df_cp["id"] = "CPEST"

        # adicione capital social subscrito
        df_cs = pd.DataFrame(data=[capital_social_subscrito.values], columns=capital_social_subscrito.index)
        df_cs["pas/ati"] = "passivo"
        df_cs["tipo"] = "capital proprio"
        df_cs["descricao"] = "capital social subscrito"
        df_cs["id"] = "CSSB"

        # add resultado de exercicio
        df_re = pd.DataFrame(data=[resultado_exercicio.values], columns=resultado_exercicio.index)
        df_re["pas/ati"] = "passivo"
        df_re["tipo"] = "capital proprio"
        df_re["descricao"] = "Resultado do exercicio"
        df_re["id"] = "RDEE"

        # include capital proprio in balanco
        self.balanco = pd.concat([self.balanco, df_cp, df_re, df_cs])
        pass

    def compute_adicional(self):
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
        self.balanco = pd.concat([self.balanco, df_final]).reset_index(drop=True)

        pass


