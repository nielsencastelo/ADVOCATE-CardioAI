from schemas import CheckIn

class RiskEngine:
    def evaluate(self, checkin: CheckIn, last_checkins: list[CheckIn]):
        s = checkin.symptoms or {}
        v = checkin.vitals or {}

        reasons = []
        urgent = False
        watch = False

        chest_pain = bool(s.get("chest_pain", False))
        severe_sob = s.get("shortness_of_breath", "") in ["severe", "at_rest"]
        syncope = bool(s.get("syncope", False))
        neuro = bool(s.get("stroke_symptoms", False))

        if chest_pain:
            urgent = True; reasons.append("Reported chest pain.")
        if severe_sob:
            urgent = True; reasons.append("Severe dyspnea or dyspnea at rest.")
        if syncope:
            urgent = True; reasons.append("Syncope reported.")
        if neuro:
            urgent = True; reasons.append("Acute neurological symptoms (possible stroke).")

        edema = bool(s.get("leg_swelling", False))
        sob_mod = s.get("shortness_of_breath", "") in ["mild", "moderate", "on_exertion"]

        delta_w = None
        weight = v.get("weight_kg", None)
        if weight is not None and last_checkins:
            prev_w = last_checkins[-1].vitals.get("weight_kg", None)
            if prev_w is not None:
                delta_w = float(weight) - float(prev_w)
                if delta_w >= 1.0:
                    watch = True; reasons.append("Weight gain ≥ 1 kg vs prior day (possible fluid retention).")

        if edema:
            watch = True; reasons.append("Leg swelling/edema reported.")
        if sob_mod:
            watch = True; reasons.append("Mild/moderate dyspnea with exertion.")

        if urgent:
            return "urgent", reasons, delta_w
        if watch:
            return "watch", reasons, delta_w
        return "stable", ["No rule-based red flags detected today."], delta_w