import json
import os
from datetime import datetime

FEEDBACKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "feedbacks.json")

class FeedbackService:
    @staticmethod
    def _carregar_feedbacks():
        if not os.path.exists(FEEDBACKS_FILE):
            return []
        try:
            with open(FEEDBACKS_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados if isinstance(dados, list) else []
        except Exception:
            return []

    @staticmethod
    def _salvar_feedbacks(feedbacks):
        try:
            with open(FEEDBACKS_FILE, "w", encoding="utf-8") as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar feedbacks.json: {e}")
            return False

    @classmethod
    def listar_feedbacks(cls):
        feedbacks = cls._carregar_feedbacks()
        # Retorna ordenado do mais recente para o mais antigo
        return sorted(feedbacks, key=lambda x: x.get("id", 0), reverse=True)

    @classmethod
    def adicionar_feedback(cls, nome, texto):
        nome = (nome or "").strip()
        texto = (texto or "").strip()

        if not nome or not texto:
            raise ValueError("Por favor, preencha seu nome e a mensagem de feedback.")

        if len(nome) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")

        if len(texto) < 5:
            raise ValueError("O feedback deve ter pelo menos 5 caracteres.")

        feedbacks = cls._carregar_feedbacks()
        
        # Gera o próximo ID
        proximo_id = max([item.get("id", 0) for item in feedbacks], default=0) + 1
        
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y às %H:%M")

        novo_feedback = {
            "id": proximo_id,
            "nome": nome,
            "texto": texto,
            "data": data_formatada
        }

        feedbacks.append(novo_feedback)
        cls._salvar_feedbacks(feedbacks)
        return novo_feedback

    @classmethod
    def excluir_feedback(cls, feedback_id):
        feedbacks = cls._carregar_feedbacks()
        feedbacks_filtrados = [f for f in feedbacks if f.get("id") != int(feedback_id)]
        cls._salvar_feedbacks(feedbacks_filtrados)
        return True
