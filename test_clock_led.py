# Tests using pytest of the clock leds helper functions that turn on the leds

import pytest
from clock import Clock


def test_clock_leds():
    # test the clock leds
    n_leds_per_line = 11
    n_leds = n_leds_per_line * 10
    pixels = [(0, 0, 0) for i in range(n_leds)]
    clk = Clock(n_leds_per_line, pixels)

    # test the clock leds
    assert clk.show_il_est() == "ILEST"
    assert clk.show_heure() == "HEURE"
    assert clk.show_une() == "UNE"
    assert clk.show_deux() == "DEUX"
    assert clk.show_trois() == "TROIS"
    assert clk.show_quatre() == "QUATRE"
    assert clk.show_cinq() == "CINQ"
    assert clk.show_six() == "SIX"
    assert clk.show_sept() == "SEPT"
    assert clk.show_huit() == "HUIT"
    assert clk.show_neuf() == "NEUF"
    assert clk.show_dix() == "DIX"
    assert clk.show_onze() == "ONZE"
    assert clk.show_midi() == "MIDI"
    assert clk.show_minuit() == "MINUIT"
    assert clk.show_moins() == "MOINS"
    assert clk.show_et_above() == "ET"
    assert clk.show_et_below() == "ET"
    assert clk.show_quart() == "QUART"
    assert clk.show_demie() == "DEMIE"
    assert clk.show_vingt_min() == "VINGT"
    assert clk.show_cinq_min() == "CINQ"
    assert clk.show_dash_min() == "-"
