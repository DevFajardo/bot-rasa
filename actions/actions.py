import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re

class ActionProcesarDatosPrestamo(Action):
    
    def name(self):
        return "action_prediccion_prestamo"

    def run(self, dispatcher, tracker, domain):
        def extraer_numero(oracion, clave):
            patron = rf"{clave}\D*(\d+)"
            match = re.search(patron, oracion)
            if match:
                return int(match.group(1))
            return None
        user_id = tracker.sender_id
        income = extraer_numero(tracker.get_slot("ingreso"), "ingreso")
        credit_score = extraer_numero(tracker.get_slot("puntaje"), "puntaje")
        loan_amount = extraer_numero(tracker.get_slot("monto"), "monto")
        years_employed = extraer_numero(tracker.get_slot("años_trabajados"), "llevo")
        payload = {
            "user_id": user_id,
            "income": income,
            "credit_score": credit_score,
            "loan_amount": loan_amount,
            "years_employed": years_employed
        }
        
        response = requests.post(
            "http://localhost:5000/predict",
            json=payload
        ).json()
        print(response)

        rf = response.get("Random Forest")
        gb = response.get("Gradient Boosting")
        xg = response.get("XGBoost")
        print(rf , gb, xg)
        # Lógica del mensaje final
        if rf or gb or xg:
            mensaje_final = "🎉 ¡Felicidades! Tu préstamo podría ser aprobado."
        else:
            mensaje_final = "❌ Lo siento, según el análisis tu préstamo no sería aprobado."

        dispatcher.utter_message(
            text=(
                f"Resultados del análisis de crédito:\n"
                f"- Random Forest: {rf}\n"
                f"- Gradient Boosting: {gb}\n"
                f"- XGBoost: {xg}\n"
                f"{mensaje_final}\n\n"
            )
        )

        return []
    
class ActionUltimaPrediccion(Action):

    def name(self):
        return "action_ultima_prediccion"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id     # viene desde el mobile

        try:
            url = f"http://127.0.0.1:5000/prediction/latest/{user_id}"
            response = requests.get(url).json()

            if "error" in response:
                dispatcher.utter_message(text="No encontré predicciones registradas.")
                return []
            
            def estado(valor):
                return "Aprobado ✅" if int(valor) == 1 else "No aprobado ❌"

            años_empleado = response["años_empleado"]
            ingresos = response["ingresos"]
            puntos = response["puntos"]
            monto = response["monto"]

            resultado_rf = estado(response["resultado_rf"])
            resultado_gb = estado(response["resultado_gb"])
            resultado_xgb = estado(response["resultado_xgb"])

            fecha = response["creado_en"]

            mensaje = (
                "📊 **Tu última predicción de crédito**:\n"
                f"- Años empleado: {años_empleado}\n"
                f"- Ingresos: {ingresos}$ \n"
                f"- Puntos de crédito: {puntos}\n"
                f"- Monto solicitado: {monto}$ \n"
                f"- Random Forest: {resultado_rf}\n"
                f"- Gradient Boosting: {resultado_gb}\n"
                f"- XGBoost: {resultado_xgb}\n"
                f"- Fecha: {fecha}"
            )
            dispatcher.utter_message(text=mensaje)

        except Exception:
            dispatcher.utter_message(text="Hubo un problema consultando tu predicción.")
        
        return []
