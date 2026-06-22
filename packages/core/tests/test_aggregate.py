from agenteval.scoring.aggregate import WEIGHTS, weighted_score


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_perfect_score():
    assert weighted_score(100, 100, 100) == 100.0


def test_zero_score():
    assert weighted_score(0, 0, 0) == 0.0


def test_weighted_combination():
    # 100*0.4 + 50*0.4 + 0*0.2 = 60
    assert weighted_score(100, 50, 0) == 60.0
