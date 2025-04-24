def get_risk_score(fwi_indices, ndvi, slope, T_max):
    """
    Calculate the fire risk score based on FWI indices, NDVI, and slope.

    Parameters:
    fwi_indices (dict): Dictionary containing FWI indices.
    ndvi (float): NDVI value.
    slope (float): Slope value.

    Returns:
    float: Fire risk score.
    """
    # normalize values

    # Calculate the fire risk score using the given formula
    risk_score = 0.35 * fwi_indices['BUI'] + 0.15 * ndvi + 0.2 * slope + 0.3* T_max
    return risk_score