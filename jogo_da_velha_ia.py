import random
import sys

# Compatibilidade entre PyQt6 e PyQt5
try:
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QGridLayout, QPushButton, QLabel,
        QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QButtonGroup
    )
    from PyQt6.QtCore import QTimer, Qt
except Exception:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QGridLayout, QPushButton, QLabel,
        QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QButtonGroup
    )
    from PyQt5.QtCore import QTimer, Qt

# Ajustes para diferenças entre enums em PyQt5/PyQt6
try:
    _ = Qt.AlignmentFlag.AlignCenter
except Exception:
    # PyQt5 usa Qt.AlignCenter
    Qt.AlignmentFlag = Qt

try:
    _ = QFrame.Shape.VLine
except Exception:
    # PyQt5 usa QFrame.VLine
    QFrame.Shape = QFrame

# Importa as regras e a interface da IA dos outros arquivos
from minimax import melhor_jogada, verificar_vencedor, tabuleiro_cheio
from painel_neuronios import PainelNeuronios

JOGADOR_HUMANO = "X"
JOGADOR_IA = "O"
ATRASO_ENTRE_ANALISES_MS = 300

DIFICULDADES = {
    "Fácil": 0.75,
    "Mediano": 0.4,
    "Difícil": 0.15,
    "Minimax": 0.0,
}
DIFICULDADE_PADRAO = "Mediano"

class PainelPensamentoIA(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label_titulo = QLabel("Aguardando sua jogada...")
        layout.addWidget(self.label_titulo)
        self.painel = PainelNeuronios()
        layout.addWidget(self.painel)
        self.setLayout(layout)

    def iniciar_analise(self):
        self.painel.iniciar_analise()
        self.label_titulo.setText("Analisando jogadas possíveis com Minimax...")

    def adicionar_avaliacao(self, posicao, pontuacao):
        self.painel.adicionar_avaliacao(posicao, pontuacao)

    def mostrar_escolha(self, posicao, pontuacao):
        self.label_titulo.setText(f"Melhor jogada encontrada: posição {posicao} (pontuação {pontuacao})")
        self.painel.mostrar_escolha(posicao, pontuacao)

    def reiniciar(self):
        self.painel.reiniciar()
        self.label_titulo.setText("Aguardando sua jogada...")


class JanelaJogo(QWidget):
    def __init__(self):
        super().__init__()
        
        # EXERCÍCIO 2: Título da janela modificado
        self.setWindowTitle("Super Jogo da Velha com IA")
        
        self.painel_ia = PainelPensamentoIA()
        self.tabuleiro = [""] * 9
        self.botoes = []
        self.jogo_ativo = True
        self.dificuldade_atual = DIFICULDADE_PADRAO
        self.probabilidade_aleatoria = DIFICULDADES[DIFICULDADE_PADRAO]
        
        # EXERCÍCIO 3: Variáveis do Placar Permanente
        self.placar_jogador = 0
        self.placar_ia = 0
        self.placar_empates = 0
        
        self.montar_interface()

    def montar_interface(self):
        layout_principal = QHBoxLayout()
        layout_jogo = QVBoxLayout()

        # EXERCÍCIO 3: Adicionando o QLabel do Placar Permanente na tela
        self.label_placar = QLabel(f"Jogador: {self.placar_jogador} | IA: {self.placar_ia} | Empates: {self.placar_empates}")
        self.label_placar.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        self.label_placar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_jogo.addWidget(self.label_placar)

        layout_jogo.addWidget(QLabel("Dificuldade da IA:"))
        layout_dificuldade = QHBoxLayout()
        self.grupo_dificuldade = QButtonGroup(self)
        self.grupo_dificuldade.setExclusive(True)

        for nome in DIFICULDADES:
            botao = QPushButton(nome)
            botao.setCheckable(True)
            botao.setChecked(nome == self.dificuldade_atual)
            botao.clicked.connect(lambda _, n=nome: self.selecionar_dificuldade(n))
            self.grupo_dificuldade.addButton(botao)
            layout_dificuldade.addWidget(botao)

        layout_jogo.addLayout(layout_dificuldade)

        # EXERCÍCIO 2: Adicionando o QLabel que mostra de quem é a vez
        self.label_status = QLabel("Sua vez")
        self.label_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_jogo.addWidget(self.label_status)

        grade = QGridLayout()
        for i in range(9):
            botao = QPushButton("")
            botao.setFixedSize(80, 80)
            botao.setStyleSheet("font-size: 24px;")
            botao.clicked.connect(lambda _, pos=i: self.jogada_humano(pos))
            self.botoes.append(botao)
            grade.addWidget(botao, i // 3, i % 3)

        layout_jogo.addLayout(grade)

        # EXERCÍCIO 2: Botão alterado para "Nova partida"
        botao_nova_partida = QPushButton("Nova partida")
        botao_nova_partida.setStyleSheet("font-size: 16px; padding: 10px;")
        botao_nova_partida.clicked.connect(self.reiniciar)
        layout_jogo.addWidget(botao_nova_partida)
        
        layout_jogo.addStretch()

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.VLine)

        layout_principal.addLayout(layout_jogo)
        layout_principal.addWidget(separador)
        layout_principal.addWidget(self.painel_ia)

        self.setLayout(layout_principal)

    def selecionar_dificuldade(self, nome):
        self.dificuldade_atual = nome
        self.probabilidade_aleatoria = DIFICULDADES[nome]

    def jogada_humano(self, posicao):
        if not self.jogo_ativo or self.tabuleiro[posicao] != "":
            return

        self.tabuleiro[posicao] = JOGADOR_HUMANO
        self.botoes[posicao].setText(JOGADOR_HUMANO)

        if self.verificar_fim_de_jogo():
            return

        # EXERCÍCIO 2: Atualiza o texto do turno para a IA
        self.label_status.setText("Vez da IA")
        self.travar_tabuleiro(True)
        QTimer.singleShot(300, self.turno_ia)

    def escolher_jogada(self, melhor_posicao, avaliacoes):
        if random.random() < self.probabilidade_aleatoria:
            posicoes_piores = [pos for pos, _ in avaliacoes if pos != melhor_posicao]
            if posicoes_piores:
                return random.choice(posicoes_piores)
        return melhor_posicao

    def turno_ia(self):
        melhor_posicao, avaliacoes = melhor_jogada(self.tabuleiro, JOGADOR_IA, JOGADOR_HUMANO)
        posicao_escolhida = self.escolher_jogada(melhor_posicao, avaliacoes)
        self.painel_ia.iniciar_analise()

        for indice, (pos, pontuacao) in enumerate(avaliacoes):
            atraso = ATRASO_ENTRE_ANALISES_MS * (indice + 1)
            QTimer.singleShot(
                atraso,
                lambda p=pos, pt=pontuacao: self.painel_ia.adicionar_avaliacao(p, pt)
            )

        atraso_final = ATRASO_ENTRE_ANALISES_MS * (len(avaliacoes) + 1)
        QTimer.singleShot(atraso_final, lambda: self.executar_jogada_ia(posicao_escolhida, avaliacoes))

    def executar_jogada_ia(self, posicao, avaliacoes):
        pontuacao_escolhida = next((pt for p, pt in avaliacoes if p == posicao), 0)
        self.painel_ia.mostrar_escolha(posicao, pontuacao_escolhida)

        self.tabuleiro[posicao] = JOGADOR_IA
        self.botoes[posicao].setText(JOGADOR_IA)

        if self.verificar_fim_de_jogo():
            return

        # EXERCÍCIO 2: Atualiza o texto do turno de volta para o jogador
        self.label_status.setText("Sua vez")
        self.travar_tabuleiro(False)

    def verificar_fim_de_jogo(self):
        vencedor = verificar_vencedor(self.tabuleiro)
        if vencedor:
            self.jogo_ativo = False
            # EXERCÍCIO 2 e 3: Atualiza mensagens de vitória e soma pontos ao placar
            if vencedor == JOGADOR_HUMANO:
                texto = "Você venceu!"
                self.label_status.setText("você venceu")
                self.placar_jogador += 1
            else:
                texto = "A IA venceu!"
                self.label_status.setText("A IA venceu")
                self.placar_ia += 1
                
            self.atualizar_placar()
            QMessageBox.information(self, "Fim de jogo", texto)
            return True

        if tabuleiro_cheio(self.tabuleiro):
            self.jogo_ativo = False
            # EXERCÍCIO 2 e 3: Atualiza mensagem de empate e soma pontos ao placar
            self.label_status.setText("empate")
            self.placar_empates += 1
            self.atualizar_placar()
            QMessageBox.information(self, "Fim de jogo", "Empate!")
            return True

        return False
        
    def atualizar_placar(self):
        # Atualiza a interface gráfica do placar
        self.label_placar.setText(f"Jogador: {self.placar_jogador} | IA: {self.placar_ia} | Empates: {self.placar_empates}")

    def travar_tabuleiro(self, travado):
        for i, botao in enumerate(self.botoes):
            if self.tabuleiro[i] == "":
                botao.setEnabled(not travado)

    def reiniciar(self):
        self.tabuleiro = [""] * 9
        self.jogo_ativo = True
        self.label_status.setText("Sua vez")
        for botao in self.botoes:
            botao.setText("")
            botao.setEnabled(True)
        self.painel_ia.reiniciar()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaJogo()
    janela.show()
    sys.exit(app.exec())