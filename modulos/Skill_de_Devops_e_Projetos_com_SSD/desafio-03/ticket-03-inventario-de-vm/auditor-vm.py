#!/usr/bin/env python3
"""
Auditor de VM - Ferramenta de inventário e drift por SSH
Audita uma VM por SSH e compara com o baseline do parque da Metacortex
"""

import sys
import json
import paramiko
import yaml
from datetime import datetime
from typing import Dict, List, Any

class AuditorVM:
    def __init__(self, baseline_path: str = "baseline.yaml"):
        self.baseline = self.carregar_baseline(baseline_path)

    def carregar_baseline(self, path: str) -> Dict:
        """Carrega o baseline YAML"""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {path} não encontrado")
            sys.exit(3)
        except yaml.YAMLError as e:
            print(f"Erro: Baseline inválido: {e}")
            sys.exit(3)

    def conectar_ssh(self, host: str, usuario: str, chave_privada: str, porta: int = 22):
        """Conecta ao host via SSH"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=usuario, key_filename=chave_privada, port=porta, timeout=10)
            return client
        except paramiko.AuthenticationException:
            print(f"Erro: Falha de autenticação em {host}")
            sys.exit(2)
        except paramiko.SSHException as e:
            print(f"Erro: Falha de conexão SSH em {host}: {e}")
            sys.exit(2)
        except Exception as e:
            print(f"Erro: Conexão com {host} falhou: {e}")
            sys.exit(2)

    def executar_comando(self, ssh_client, comando: str, timeout: int = 30) -> str:
        """Executa comando no host remoto"""
        try:
            stdin, stdout, stderr = ssh_client.exec_command(comando, timeout=timeout)
            return stdout.read().decode('utf-8')
        except paramiko.SSHException as e:
            raise Exception(f"Erro ao executar comando '{comando}': {e}")

    def coletar_identificacao(self, ssh_client) -> Dict:
        """Coleta identificação do host"""
        hostname = self.executar_comando(ssh_client, "hostname").strip()
        return {
            "hostname": hostname,
            "coletado_em": datetime.utcnow().isoformat() + "Z"
        }

    def coletar_so(self, ssh_client) -> Dict:
        """Coleta informações do sistema operacional"""
        try:
            output = self.executar_comando(ssh_client, "cat /etc/os-release")
            linhas = output.split('\n')
            info = {}
            for linha in linhas:
                if '=' in linha:
                    chave, valor = linha.split('=', 1)
                    info[chave.strip()] = valor.strip('"')
            return {
                "distribuicao": info.get("ID", "desconhecido"),
                "versao": info.get("VERSION_ID", "desconhecido")
            }
        except Exception:
            return {"distribuicao": "nao_verificado", "versao": "nao_verificado"}

    def coletar_kernel(self, ssh_client) -> Dict:
        """Coleta versão do kernel"""
        try:
            versao = self.executar_comando(ssh_client, "uname -r").strip()
            return {"versao": versao}
        except Exception:
            return {"versao": "nao_verificado"}

    def coletar_servicos(self, ssh_client) -> Dict:
        """Coleta serviços ativos e proibidos"""
        servicos = {"ativos": [], "proibidos": []}
        try:
            # Serviços ativos
            output = self.executar_comando(ssh_client, "systemctl list-units --type=service --state=running --no-pager")
            for linha in output.split('\n'):
                if linha and not linha.startswith('UNIT'):
                    nome = linha.split()[0]
                    servicos["ativos"].append({"nome": nome, "tipo": "service"})

            # Sockets escutando (tipo socket)
            output = self.executar_comando(ssh_client, "systemctl list-units --type=socket --state=listening --no-pager")
            for linha in output.split('\n'):
                if linha and not linha.startswith('UNIT'):
                    nome = linha.split()[0]
                    servicos["proibidos"].append({"nome": nome, "tipo": "socket"})
        except Exception as e:
            print(f"Aviso: Não foi possível coletar serviços: {e}")
        return servicos

    def coletar_swap(self, ssh_client) -> Dict:
        """Coleta status do swap"""
        try:
            output = self.executar_comando(ssh_client, "swapon --show")
            if "Filename" in output:
                # Swap habilitado
                for linha in output.split('\n'):
                    if "Size" in linha:
                        tamanho = linha.split()[1]
                        return {"habilitado": True, "tamanho": tamanho}
            return {"habilitado": False}
        except Exception:
            return {"habilitado": "nao_verificado"}

    def coletar_portas(self, ssh_client) -> List[Dict]:
        """Coleta portas em escuta"""
        portas = []
        try:
            output = self.executar_comando(ssh_client, "ss -tulpn")
            for linha in output.split('\n'):
                if linha and not linha.startswith("State"):
                    partes = linha.split()
                    if len(partes) >= 5:
                        portas.append({
                            "porta": int(partes[3]),
                            "bind": partes[4],
                            "processo": partes[6] if len(partes) > 6 else "desconhecido"
                        })
        except Exception as e:
            print(f"Aviso: Não foi possível coletar portas: {e}")
        return portas

    def coletar_chaves_ssh(self, ssh_client) -> Dict:
        """Coleta chaves SSH autorizadas"""
        chaves = []
        try:
            output = self.executar_comando(ssh_client, "cat ~/.ssh/authorized_keys")
            for linha in output.split('\n'):
                if linha.strip():
                    # Verificar se chave foi emitida pela plataforma
                    if "platform@metacortex-platform" in linha or "platform" in linha.lower():
                        chaves.append({"identificacao": "platform@metacortex-platform"})
                    else:
                        chaves.append({"identificacao": "desconhecida"})
        except Exception as e:
            print(f"Aviso: Não foi possível coletar chaves SSH: {e}")
        return {"quantidade": len(chaves), "chaves": chaves}

    def coletar_ssh_root(self, ssh_client) -> Dict:
        """Coleta configuração de login de root"""
        try:
            output = self.executar_comando(ssh_client, "grep PermitRootLogin /etc/ssh/sshd_config")
            if "PermitRootLogin" in output:
                valor = output.split()[-1]
                return {"login_de_root": valor == "yes"}
            return {"login_de_root": "nao_verificado"}
        except Exception:
            return {"login_de_root": "nao_verificado"}

    def coletar_ntp(self, ssh_client) -> Dict:
        """Coleta status de sincronização NTP"""
        try:
            output = self.executar_comando(ssh_client, "timedatectl status")
            sincronizado = "System clock synchronized: yes" in output
            mecanismo = "systemd-timesyncd" if "systemd-timesyncd" in output else "desconhecido"
            return {"sincronizado": sincronizado, "mecanismo": mecanismo}
        except Exception:
            return {"sincronizado": "nao_verificado", "mecanismo": "nao_verificado"}

    def validar_conformidade(self, inventario: Dict) -> List[Dict]:
        """Valida inventário contra baseline"""
        conformidade = []
        esperado = self.baseline.get("esperado", {})
        severidade = self.baseline.get("severidade", {})

        # Validação de SO
        so = inventario.get("so", {})
        distrib_esperado = esperado.get("so", {}).get("distribuicao")
        versao_esperada = esperado.get("so", {}).get("versao_minima")

        if so.get("distribuicao") != distrib_esperado:
            severidade_reg = self._get_severidade("so.distribuicao", severidade)
            conformidade.append({
                "regra": "so.distribuicao",
                "esperado": distrib_esperado,
                "encontrado": so.get("distribuicao"),
                "veredito": "desvio",
                "severidade": severidade_reg
            })
        else:
            conformidade.append({
                "regra": "so.distribuicao",
                "esperado": distrib_esperado,
                "encontrado": so.get("distribuicao"),
                "veredito": "conforme"
            })

        # Validação de versão do SO
        if so.get("versao") != "nao_verificado":
            versao_encontrada = so.get("versao", "")
            # Comparação simplificada de versão
            if versao_encontrada < versao_esperada:
                severidade_reg = self._get_severidade("so.versao_minima", severidade)
                conformidade.append({
                    "regra": "so.versao_minima",
                    "esperado": versao_esperada,
                    "encontrado": versao_encontrada,
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": "so.versao_minima",
                    "esperado": versao_esperada,
                    "encontrado": versao_encontrada,
                    "veredito": "conforme"
                })
        else:
            conformidade.append({
                "regra": "so.versao_minima",
                "esperado": versao_esperada,
                "encontrado": "nao_verificado",
                "veredito": "nao_verificado",
                "motivo": "versão do SO não pôde ser coletada"
            })

        # Validação de kernel
        kernel = inventario.get("kernel", {})
        versao_kernel_esperada = esperado.get("kernel", {}).get("versao_minima")
        if kernel.get("versao") != "nao_verificado":
            versao_kernel_encontrada = kernel.get("versao", "")
            if versao_kernel_encontrada < versao_kernel_esperada:
                severidade_reg = self._get_severidade("kernel.versao_minima", severidade)
                conformidade.append({
                    "regra": "kernel.versao_minima",
                    "esperado": versao_kernel_esperada,
                    "encontrado": versao_kernel_encontrada,
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": "kernel.versao_minima",
                    "esperado": versao_kernel_esperada,
                    "encontrado": versao_kernel_encontrada,
                    "veredito": "conforme"
                })
        else:
            conformidade.append({
                "regra": "kernel.versao_minima",
                "esperado": versao_kernel_esperada,
                "encontrado": "nao_verificado",
                "motivo": "versão do kernel não pôde ser coletada"
            })

        # Validação de serviços
        servicos = inventario.get("servicos", {})
        servicos_ativos_esperados = set(esperado.get("servicos", {}).get("ativos", []))
        servicos_proibidos_esperados = set(esperado.get("servicos", {}).get("proibidos", []))
        servicos_ativos_encontrados = {s["nome"] for s in servicos.get("ativos", [])}
        servicos_proibidos_encontrados = {s["nome"] for s in servicos.get("proibidos", [])}

        # Serviços ativos
        for servico in servicos_ativos_esperados:
            if servico in servicos_ativos_encontrados:
                conformidade.append({
                    "regra": f"servicos.ativos.{servico}",
                    "esperado": f"{servico} ativo",
                    "encontrado": f"{servico} ativo",
                    "veredito": "conforme"
                })
            else:
                severidade_reg = self._get_severidade("servicos.ativos", severidade)
                conformidade.append({
                    "regra": f"servicos.ativos.{servico}",
                    "esperado": f"{servico} ativo",
                    "encontrado": "ausente",
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })

        # Serviços proibidos
        for servico in servicos_proibidos_esperados:
            if servico in servicos_proibidos_encontrados:
                severidade_reg = self._get_severidade("servicos.proibidos", severidade)
                conformidade.append({
                    "regra": f"servicos.proibidos.{servico}",
                    "esperado": f"{servico} proibido",
                    "encontrado": f"{servico} ativo",
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": f"servicos.proibidos.{servico}",
                    "esperado": f"{servico} proibido",
                    "encontrado": "ausente",
                    "veredito": "conforme"
                })

        # Validação de swap
        swap = inventario.get("swap", {})
        swap_esperado = esperado.get("swap", {}).get("habilitado")
        if swap.get("habilitado") != "nao_verificado":
            if swap["habilitado"] != swap_esperado:
                severidade_reg = self._get_severidade("swap.habilitado", severidade)
                conformidade.append({
                    "regra": "swap.habilitado",
                    "esperado": swap_esperado,
                    "encontrado": swap["habilitado"],
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": "swap.habilitado",
                    "esperado": swap_esperado,
                    "encontrado": swap["habilitado"],
                    "veredito": "conforme"
                })
        else:
            conformidade.append({
                "regra": "swap.habilitado",
                "esperado": swap_esperado,
                "encontrado": "nao_verificado",
                "motivo": "status do swap não pôde ser coletado"
            })

        # Validação de portas
        portas = inventario.get("portas_em_escuta", [])
        portas_publicas_esperadas = set(esperado.get("portas_em_escuta", {}).get("publicas_permitidas", []))
        portas_internas_esperadas = set(esperado.get("portas_em_escuta", {}).get("somente_rede_interna", []))

        for porta_info in portas:
            porta = porta_info["porta"]
            bind = porta_info["bind"]

            # Porta pública permitida
            if porta in portas_publicas_esperadas:
                if bind == "0.0.0.0":
                    conformidade.append({
                        "regra": f"portas_em_escuta.publicas_permitidas.{porta}",
                        "esperado": f"{porta} na rede interna",
                        "encontrado": f"{porta} em {bind}",
                        "veredito": "conforme"
                    })
                else:
                    severidade_reg = self._get_severidade("portas_em_escuta.somente_rede_interna", severidade)
                    conformidade.append({
                        "regra": f"portas_em_escuta.publicas_permitidas.{porta}",
                        "esperado": f"{porta} na rede interna",
                        "encontrado": f"{porta} em {bind}",
                        "veredito": "desvio",
                        "severidade": severidade_reg
                    })
            else:
                severidade_reg = self._get_severidade("portas_em_escuta.publicas_permitidas", severidade)
                conformidade.append({
                    "regra": f"portas_em_escuta.publicas_permitidas.{porta}",
                    "esperado": f"{porta} não permitida",
                    "encontrado": f"{porta} em {bind}",
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })

            # Porta só rede interna
            if porta in portas_internas_esperadas:
                if bind != "0.0.0.0":
                    conformidade.append({
                        "regra": f"portas_em_escuta.somente_rede_interna.{porta}",
                        "esperado": f"{porta} na rede interna",
                        "encontrado": f"{porta} em {bind}",
                        "veredito": "conforme"
                    })
                else:
                    severidade_reg = self._get_severidade("portas_emescuta.somente_rede_interna", severidade)
                    conformidade.append({
                        "regra": f"portas_em_escuta.somente_rede_interna.{porta}",
                        "esperado": f"{porta} na rede interna",
                        "encontrado": f"{porta} em {bind}",
                        "veredito": "desvio",
                        "severidade": severidade_reg
                    })

        # Validação de chaves SSH
        chaves = inventario.get("chaves_ssh", {})
        emitidas_por = esperado.get("chaves_ssh", {}).get("emitidas_por")
        if chaves.get("quantidade", 0) > 0:
            todas_emitidas_pela_plataforma = all(
                c.get("identificacao") == emitidas_por
                for c in chaves.get("chaves", [])
            )
            if not todas_emitidas_pela_plataforma:
                severidade_reg = self._get_severidade("chaves_ssh.emitidas_por", severidade)
                conformidade.append({
                    "regra": "chaves_ssh.emitidas_por",
                    "esperado": emitidas_por,
                    "encontrado": "nem todas emitidas pela plataforma",
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": "chaves_ssh.emitidas_por",
                    "esperado": emitidas_por,
                    "encontrado": "todas emitidas pela plataforma",
                    "veredito": "conforme"
                })
        else:
            conformidade.append({
                "regra": "chaves_ssh.emitidas_por",
                "esperado": emitidas_por,
                "encontrado": "nenhuma chave",
                "veredito": "nao_verificado",
                "motivo": "não foi possível coletar chaves SSH"
            })

        # Validação de SSH root
        ssh = inventario.get("ssh", {})
        root_esperado = esperado.get("ssh", {}).get("login_de_root")
        if ssh.get("login_de_root") != "nao_verificado":
            if ssh["login_de_root"] != root_esperado:
                severidade_reg = self._get_severidade("ssh.login_de_root", severidade)
                conformidade.append({
                    "regra": "ssh.login_de_root",
                    "esperado": root_esperado,
                    "encontrado": ssh["login_de_root"],
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": "ssh.login_de_root",
                    "esperado": root_esperado,
                    "encontrado": ssh["login_de_root"],
                    "veredito": "conforme"
                })
        else:
            conformidade.append({
                "regra": "ssh.login_de_root",
                "esperado": root_esperado,
                "encontrado": "nao_verificado",
                "motivo": "configuração de SSH não pôde ser coletada"
            })

        # Validação de NTP
        ntp = inventario.get("ntp", {})
        ntp_esperado = esperado.get("ntp", {}).get("sincronizado")
        if ntp.get("sincronizado") != "nao_verificado":
            if ntp["sincronizado"] != ntp_esperado:
                severidade_reg = self._get_severidade("ntp.sincronizado", severidade)
                conformidade.append({
                    "regra": "ntp.sincronizado",
                    "esperado": ntp_esperado,
                    "encontrado": ntp["sincronizado"],
                    "veredito": "desvio",
                    "severidade": severidade_reg
                })
            else:
                conformidade.append({
                    "regra": "ntp.sincronizado",
                    "esperado": ntp_esperado,
                    "encontrado": ntp["sincronizado"],
                    "veredito": "conforme"
                })
        else:
            conformidade.append({
                "regra": "ntp.sincronizado",
                "esperado": ntp_esperado,
                "encontrado": "nao_verificado",
                "motivo": "status de NTP não pôde ser coletado"
            })

        return conformidade

    def _get_severidade(self, regra: str, severidade: Dict) -> str:
        """Helper para obter severidade de uma regra"""
        for severidade in ["critico", "alto", "medio"]:
            if regra in severidade.get(severidade, []):
                return severidade
        return "alto"  # default

    def auditor(self, endereco: str, usuario: str, chave_privada: str):
        """Executa auditoria completa"""
        # Adicionar endereço ao contexto
        endereco_host = endereco

        try:
            ssh_client = self.conectar_ssh(endereco, usuario, chave_privada)

            # Coletar inventário
            inventario = {
                "so": self.coletar_so(ssh_client),
                "kernel": self.coletar_kernel(ssh_client),
                "servicos": self.coletar_servicos(ssh_client),
                "swap": self.coletar_swap(ssh_client),
                "portas_em_escuta": self.coletar_portas(ssh_client),
                "chaves_ssh": self.coletar_chaves_ssh(ssh_client),
                "ssh": self.coletar_ssh_root(ssh_client),
                "ntp": self.coletar_ntp(ssh_client)
            }

            ssh_client.close()

            # Validar conformidade
            conformidade = self.validar_conformidade(inventario)

            # Gerar resumo
            resumo = self._gerar_resumo(conformidade)

            # Dados completos
            dados = {
                "host": {
                    "endereco": endereco,
                    "hostname": inventario.get("so", {}).get("distribuicao", "desconhecido"),
                    "coletado_em": datetime.utcnow().isoformat() + "Z"
                },
                "inventario": inventario,
                "conformidade": conformidade,
                "resumo": resumo
            }

            return dados

        except Exception as e:
            print(f"Erro durante auditoria: {e}")
            sys.exit(2)

    def _gerar_resumo(self, conformidade: List[Dict]) -> Dict:
        """Gera resumo da conformidade"""
        resumo = {"conforme": 0, "desvio": 0, "nao_verificado": 0, "por_severidade": {"critico": 0, "alto": 0, "medio": 0}}

        for item in conformidade:
            veredito = item.get("veredito")
            if veredito == "conforme":
                resumo["conforme"] += 1
            elif veredito == "desvio":
                resumo["desvio"] += 1
                severidade = item.get("severidade", "alto")
                resumo["por_severidade"][severidade] = resumo["por_severidade"].get(severidade, 0) + 1
            elif veredito == "nao_verificado":
                resumo["nao_verificado"] += 1

        return resumo

    def gerar_json(self, dados: Dict) -> str:
        """Gera saída JSON"""
        return json.dumps(dados, indent=2)

    def gerar_markdown(self, dados: Dict) -> str:
        """Gera saída Markdown"""
        host = dados["host"]
        inventario = dados["inventario"]
        conformidade = dados["conformidade"]
        resumo = dados["resumo"]

        md = f"""# Inventário de {host['hostname']} ({host['endereco']})
Coletado em {host['coletado_em']} · baseline v{self.baseline.get('versao', 1)}

## Desvios

| Severidade | Regra | Esperado | Encontrado |
|---|---|---|---|
"""

        # Adicionar desvios
        desvios = [c for c in conformidade if c["veredito"] == "desvio"]
        for item in desvios:
            md += f"| {item['severidade'].capitalize()} | {item['regra']} | {item['esperado']} | {item['encontrado']} |\n"

        md += "\n## Não verificado\n\n"
        md += "| Regra | Motivo |\n|---|---|\n"

        # Adicionar não verificados
        nao_verificados = [c for c in conformidade if c["veredito"] == "nao_verificado"]
        for item in nao_verificados:
            md += f"| {item['regra']} | {item.get('motivo', 'Não especificado')} |\n"

        md += "\n## Conforme\n\n"
        conformes = [c for c in conformidade if c["veredito"] == "conforme"]
        md += " · ".join([c["regra"] for c in conformes])

        return md

def main():
    if len(sys.argv) < 4:
        print("Uso: python auditor-vm.py <endereco> <usuario> <chave_privada> [baseline.yaml]")
        sys.exit(1)

    endereco = sys.argv[1]
    usuario = sys.argv[2]
    chave_privada = sys.argv[3]
    baseline_path = sys.argv[4] if len(sys.argv) > 4 else "baseline.yaml"

    auditor = AuditorVM(baseline_path)
    dados = auditor.auditor(endereco, usuario, chave_privada)

    # Gerar JSON
    print(dados["gerar_json(dados)])

    # Gerar Markdown (se desejado)
    # print(dados["gerar_markdown(dados)])

    # Código de saída
    if dados["resumo"]["desvio"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
