from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt

class PainelNeuronios(QWidget):
    def __init__(self):
        super().__init__()
        self.neuronios = []
        grade = QGridLayout()
        for i in range(9):
            lbl = QLabel("?")
            lbl.setFixedSize(60, 60)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background-color: #333; color: white; border-radius: 30px; font-weight: bold; font-size: 16px;")
            self.neuronios.append(lbl)
            grade.addWidget(lbl, i // 3, i % 3)
        self.setLayout(grade)

    def iniciar_analise(self):
        self.reiniciar()

    def adicionar_avaliacao(self, posicao, pontuacao):
        # Fica verde se a jogada for boa para a IA, vermelho se for ruim, cinza se for empate
        cor = "#4CAF50" if pontuacao > 0 else "#F44336" if pontuacao < 0 else "#9E9E9E"
        self.neuronios[posicao].setText(str(pontuacao))
        self.neuronios[posicao].setStyleSheet(f"background-color: {cor}; color: white; border-radius: 30px; font-weight: bold; font-size: 16px;")

    def mostrar_escolha(self, posicao, pontuacao):
        # Destaca de amarelo a casa que a IA escolheu jogar
        self.neuronios[posicao].setStyleSheet("background-color: #FFD700; color: black; border-radius: 30px; font-weight: bold; font-size: 16px; border: 3px solid #FF8C00;")

    def reiniciar(self):
        for lbl in self.neuronios:
            lbl.setText("?")
            lbl.setStyleSheet("background-color: #333; color: white; border-radius: 30px; font-weight: bold; font-size: 16px;")