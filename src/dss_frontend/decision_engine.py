import pandas as pd

from src.dss_backend.decision_policy import build_decision_from_probability
from src.dss_backend.ml.inference import ModelBundle, predict_probability_for_customer
from src.dss_frontend.schema import MODEL_FEATURE_COLUMNS

from .schema import CHANNEL_LABELS, PRIORITY_LEVELS


def enrich_with_model_decisions(frame: pd.DataFrame, bundle: ModelBundle) -> pd.DataFrame:
    enriched = frame.copy()
    probabilities = bundle.pipeline.predict_proba(enriched[MODEL_FEATURE_COLUMNS])[:, 1]
    decisions = []
    for row, probability in zip(enriched.to_dict("records"), probabilities):
        decision = build_decision_from_probability(round(float(probability), 4))
        decisions.append(
            {
                "customer_label": row["customer_label"],
                "scoring_source": "logistic_regression",
                **decision,
            }
        )
    decision_frame = pd.DataFrame(decisions)
    return enriched.drop(columns=[column for column in decision_frame.columns if column in enriched.columns], errors="ignore").join(
        decision_frame
    )


def build_model_decision_view(row: pd.Series, bundle: ModelBundle) -> dict:
    customer = row.to_dict()
    probability = predict_probability_for_customer(bundle, customer)
    decision = build_decision_from_probability(probability)
    return {
        "customer_label": row["customer_label"],
        "scoring_source": "logistic_regression",
        **decision,
    }


def build_decision_view(row: pd.Series) -> dict:
    probability = 0.32
    probability += 0.10 if row.get("campaign", 0) <= 2 else -0.05
    probability += 0.12 if row.get("previous", 0) > 0 else 0.0
    probability += 0.08 if row.get("contact") == "cellular" else 0.0
    probability += 0.03 if row.get("housing") == "yes" else 0.0
    probability -= 0.03 if row.get("loan") == "yes" else 0.0
    probability += 0.10 if row.get("poutcome") == "success" else 0.0
    probability -= 0.04 if row.get("default") == "yes" else 0.0
    probability = max(0.05, min(0.95, round(probability, 2)))

    if probability >= 0.75:
        priority_level = PRIORITY_LEVELS[0]
        recommended_channel = CHANNEL_LABELS[0]
        product_name = "6\u4e2a\u6708\u5b9a\u671f\u5b58\u6b3e"
        recommended_action = (
            "\u5efa\u8bae\u572848\u5c0f\u65f6\u5185\u7535\u8bdd\u89e6\u8fbe\uff0c"
            "\u4e3b\u63a86\u4e2a\u6708\u5b9a\u671f\u5b58\u6b3e\u3002"
        )
    elif probability >= 0.55:
        priority_level = PRIORITY_LEVELS[1]
        recommended_channel = CHANNEL_LABELS[1]
        product_name = "\u7a33\u5065\u578b\u5b58\u6b3e\u4ea7\u54c1"
        recommended_action = (
            "\u5efa\u8bae\u5148\u77ed\u4fe1\u89e6\u8fbe\uff0c"
            "\u518d\u6839\u636e\u53cd\u9988\u51b3\u5b9a\u662f\u5426\u7535\u8bdd\u8ddf\u8fdb\u3002"
        )
    else:
        priority_level = PRIORITY_LEVELS[2]
        recommended_channel = CHANNEL_LABELS[2]
        product_name = "\u57fa\u7840\u5b58\u6b3e\u4ea7\u54c1"
        recommended_action = (
            "\u5efa\u8bae\u6682\u4e0d\u4f18\u5148\u7535\u8bdd\u89e6\u8fbe\uff0c"
            "\u5148\u4f7f\u7528\u4f4e\u6210\u672c\u6e20\u9053\u89c2\u5bdf\u3002"
        )

    return {
        "customer_label": row["customer_label"],
        "conversion_probability": probability,
        "priority_level": priority_level,
        "recommended_channel": recommended_channel,
        "product_name": product_name,
        "recommended_action": recommended_action,
    }
