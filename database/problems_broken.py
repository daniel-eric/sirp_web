import sqlite3
from database.db_config import DB_NAME

def adicionar_problemaBD(titulo, descricao, autor, contato, areas):
    tentativas = 3
    sucesso = False
    status = "EM ABERTO"

    while tentativas > 0 and not sucesso:    
        try:
            sql = '''INSERT INTO problems (título, descricao, autor, contato, areas, status) 
                     VALUES (?, ?, ?, ?, ?, ?)'''
            
            valores = titulo, descricao, autor, contato, f"[{areas}]", status
            
            cursor.execute(sql, valores)
            id = cursor.lastrowid
            banco.commit()
            print(f"Problema {id} salvo com sucesso!")
            sleep(3)
            sucesso= True
            banco.commit() # <--- O SEGREDO ESTÁ AQUI
            return id
        
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print("⚠️ Banco ocupado (Locked). Tentando novamente em 3s...")
                tentativas -= 1
                sleep(3)
            else:
                print(f"❌ Erro operacional: {e}")
                sleep(3)
                break
        except sqlite3.Error as erro:
            print(f"❌ Erro crítico no SQLite: {erro}")
            sleep(3)
            break

    if not sucesso:
        print("🛑 Não foi possível salvar os dados após várias tentativas.")


def mostrar_problemaBD(id_problema):
    tentativas = 3
    sucesso = False
    
    while tentativas > 0 and not sucesso:    
        try:
            cursor.execute("SELECT * FROM problemas WHERE id = ?", (id_problema,))
            #fetchone() pega a primeira (e única) linha encontrada
            resultado = cursor.fetchone()
            
            if resultado:
                return resultado
            else:
                print(f"⚠️ Problema com ID {id_problema} não encontrado.")
                sleep(3)
                return None

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print("⚠️ Banco ocupado (Locked). Tentando novamente em 3s...")
                tentativas -= 1
                sleep(3)
            else:
                print(f"❌ Erro operacional: {e}")
                sleep(3)
                break
        except sqlite3.Error as erro:
            print(f"❌ Erro crítico no SQLite: {erro}")
            sleep(3)
            break

    if not sucesso: 
        print("🛑 Não foi possível recuperar os dados.")

        
def listar_problemasBD():
    tentativas = 3
    sucesso = False
    cabecalho()
    while tentativas > 0 and not sucesso:    
        try:
            cursor.execute("SELECT id, título, areas FROM problemas")
            problemas = cursor.fetchall()
            
            limpar_tela()
            print(f"{divisoria_grossa()} FEED DE PROBLEMAS RURALINDA {divisoria_grossa()}")
            
            if problemas:
                for p in problemas:
                    # p[0] = id, p[1] = título, p[2] = areas
                    print(f"\n  {p[0]:02d} 📌 {p[1]}")
                    print(f"          Setor: {p[2]}") 
                    print(f"  {divisoria()}")
                
                sucesso = True
                escolher_problema()
            else:
                print("\n📭 O feed está vazio no momento.")
                print(divisoria())
                sucesso = True

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print(f"❌ Erro de operação: {e}")
                print("⚠️ Banco ocupado. Tentando novamente...")
                tentativas -= 1
                sleep(3)
            else:
                print(f"❌ Erro de acesso: {e}")
                sleep(3)
                break
        except sqlite3.Error as erro:
            print(f"❌ Erro no banco de dados: {erro}")
            sleep(3)
            break

    if not sucesso: 
        print("🛑 Falha ao carregar o feed. Verifique a conexão com o banco.")
        sleep(3)




def deletar_problemaBD(id_problema):
    """
    Remove permanentemente um relato de problema do banco de dados.
    Args:
        id_problema (int): O número de identificação do problema.
    Returns:
        bool: True se o problema foi deletado, False se o ID não foi encontrado.
    """
    tentativas = 3
    sucesso = False
    
    while tentativas > 0 and not sucesso:    
        try:
            cursor.execute("DELETE FROM problemas WHERE id = ?", (id_problema,))
            
            # 2. Verificamos se alguma linha foi REALMENTE afetada
            if cursor.rowcount > 0:
                banco.commit()
                sucesso = True
                print(f"✅ Problema #{id_problema} excluído com sucesso!")
                banco.commit()
                sleep(3)
            else:
                print(f"⚠️ O ID #{id_problema} não existe no banco de dados.")
                sleep(3)
                return None# Sai da função pois não há o que tentar de novo

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print("⚠️ Banco ocupado. Tentando novamente...")
                tentativas -= 1
                sleep(3)
            else:
                print(f"❌ Erro operacional: {e}")
                sleep(3)
                break
        except sqlite3.Error as erro:
            print(f"❌ Erro crítico: {erro}")
            sleep(3)
            break

    if not sucesso and tentativas == 0:
        print("🛑 Falha técnica: não conseguimos acessar o banco para deletar.")
        sleep(3)


def buscar_problemas_userlogBD(autor_nome):
    """Retorna todos os problemas escritos por um usuário específico."""
    try:
        # Filtramos pelo nome do autor que está logado na sessão
        cursor.execute("SELECT id, título, areas FROM problemas WHERE autor = ?", (autor_nome,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar seus relatos: {e}")
        return []

def atualizar_coluna_problemaBD(id_p, coluna, novo_valor):
    """Atualiza uma informação específica de um problema no banco."""
    try:
        # Usamos f-string na coluna apenas porque nomes de colunas não aceitam '?' 
        # mas como o valor vem de um menu fixo, é seguro.
        sql = f"UPDATE problemas SET {coluna} = ? WHERE id = ?"
        cursor.execute(sql, (novo_valor, id_p))
        banco.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao atualizar: {e}")
        return False


def escolher_problema():
    while True:
        id_problema = input("\nDigite o número para ler detalhes (ou '0' para voltar): ")
        if id_problema != '0':
            try:
                # 1. Busca o problema no banco usando o ID digitado
                p = mostrar_problemaBD(int(id_problema))
                
                if p:
                    limpar_tela()
                    # 2. Exibe os detalhes usando os índices da tupla 'p'
                    print(f"""
                            \n{divisoria_grossa()}
                            \n--- DETALHES DO PROBLEMA #{p[0]:02d} ---
                            \n{divisoria_grossa()}

                            \nTÍTULO:    {p[1]}
                            \nSETOR:     {p[5]}
                            \nSTATUS:    {p[6]}

                            \nDESCRIÇÃO: {p[2]}

                            \nAUTOR:     {p[3]}
                            \nCONTATO:   {p[4]} 

                            \n{divisoria()}""")
                    
                    input("\nPressione ENTER para voltar ao feed...")
                    limpar_tela()
                    listar_problemasBD() # Recarrega o feed para o usuário ver as opções de novo
                
            except ValueError:
                print("❌ Erro: Digite apenas números para selecionar o problema.")
                sleep(2)

        elif id_problema == '0': 
            limpar_tela()
            print("Retornando para o Menu...")
            sleep(2)
            tela_menu()
            break

        else:
            print("Insira um valor válido. Tente novamente.")


def reportar_novo_problema(nome, email):
    limpar_tela()

    print(f"\n{divisoria_grossa()} REPORTADOR DE PROBLEMA {divisoria_grossa()}\n")

    titulo = input("Título curto (até 70 caracteres): ")

    while len(titulo) == 0 or len(titulo) > 70:
        if len(titulo) == 0:
            print("Você deve escrever um título.")
        else:
            print(f"Máximo de 70 caracteres. Excedeu {len(titulo) - 70}.")
        titulo = input("Título curto: ")

    descricao = input("Descreva o problema: ")

    while len(descricao) == 0:
        print("Descrição inválida.")
        descricao = input("Descreva o problema: ")

    print(f"\n[ TECNOLOGIA, AGRÁRIA, SAÚDE, SOCIAIS, EXATAS ]")
    areas = input("Quais dessas áreas ou outra seu problema está inserido? ").upper()
    adicionar_problemaBD(titulo, descricao, nome, email, areas)
    


def mudar_status_problemaBD(id_problema, novo_status):
    status_permitidos = ["EM ABERTO", "EM DESENVOLVIMENTO", "RESOLVIDO", "NÃO RESOLVIDO"]
    
    if novo_status.upper() not in status_permitidos:
        print(f"🛑 Erro: '{novo_status}' não é um status válido.")
        return False

    tentativas = 3
    while tentativas > 0:
        try:
            sql = "UPDATE problemas SET status = ? WHERE id = ?"
            cursor.execute(sql, (novo_status.upper(), id_problema))
            banco.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Status do problema #{id_problema} mudou para {novo_status.upper()}!")
                return True
            return False

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                tentativas -= 1
            else: break
    return False


def atualizar_campo_problemaBD(id_problema, atributo, novo_valor):
    tentativas = 3
    sucesso = False
    
    colunas_permitidas = ['título', 'descricao', 'autor', 'contato', 'areas', 'status']
    if atributo not in colunas_permitidas:
        print(f"🛑 Erro: O atributo '{atributo}' não existe na tabela de problemas.")
        return False

    while tentativas > 0 and not sucesso:
        try:
            sql = f"UPDATE problemas SET {atributo} = ? WHERE id = ?"
            cursor.execute(sql, (novo_valor, id_problema))
            banco.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ O campo '{atributo}' do problema #{id_problema} foi atualizado!")
                sucesso = True
                return True
            else:
                print(f"⚠️ Problema #{id_problema} não localizado.")
                return False

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                tentativas -= 1
            else:
                break
        except sqlite3.Error as erro:
            print(f"❌ Erro crítico ao alterar problema: {erro}")
            break
            
    return False