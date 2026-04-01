def simple_explain(features, values, result):

    explanation = []

    # handle single float value
    if isinstance(values, (int, float)):
        vals = [values]

    # handle numpy arrays / pandas rows
    elif hasattr(values, "tolist"):
        vals = values.tolist()

    # handle normal list
    elif isinstance(values, (list, tuple)):
        vals = list(values)

    else:
        vals = [values]

    # flatten nested lists
    if len(vals) == 1 and isinstance(vals[0], (list, tuple)):
        vals = vals[0]

    for f, v in zip(features, vals):
        try:
            impact = round(float(v), 2)
        except:
            impact = 0

        explanation.append({
            "feature": f,
            "impact": impact
        })

    return explanation