"""Automatisk retting av 1T-04-trigonometri.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1_stige', 'vinkel_fra_sider(4.2, 5) skal gi ca. 57.14°', 'naer(vinkel_fra_sider(4.2, 5), 57.1401, rel=1e-4)'),
    ('1_30', 'vinkel_fra_sider(1, 2) skal gi 30°', 'naer(vinkel_fra_sider(1, 2), 30)'),
    ('2_side', 'cosinussetning_side(5, 7, 60) skal gi √39 ≈ 6.245', 'naer(cosinussetning_side(5, 7, 60), 39**0.5)'),
    ('2_rett', 'cosinussetning_side(3, 4, 90) skal gi 5', 'naer(cosinussetning_side(3, 4, 90), 5)'),
    ('2_areal', 'areal(5, 7, 60) skal gi ca. 15.155', 'naer(areal(5, 7, 60), 15.15544, rel=1e-4)'),
    ('3_rett', 'cosinussetning_vinkel(5, 3, 4) skal gi 90°', 'naer(cosinussetning_vinkel(5, 3, 4), 90)'),
    ('3_spiss', 'cosinussetning_vinkel(3, 4, 5) skal gi ca. 36.87°', 'naer(cosinussetning_vinkel(3, 4, 5), 36.8699, rel=1e-4)'),
    ('4_to', 'mulige_B(5, 7, 30) skal gi to vinkler: ca. 44.43° og 135.57°', 'len(mulige_B(5, 7, 30)) == 2 and naer(sorted(mulige_B(5, 7, 30))[0], 44.427, rel=1e-4) and naer(sorted(mulige_B(5, 7, 30))[1], 135.573, rel=1e-4)'),
    ('4_en', 'mulige_B(10, 7, 30) skal gi én vinkel: ca. 20.49°', 'len(mulige_B(10, 7, 30)) == 1 and naer(mulige_B(10, 7, 30)[0], 20.487, rel=1e-4)'),
    ('4_ingen', 'mulige_B(3, 7, 30) skal gi [] (ingen trekant)', 'mulige_B(3, 7, 30) == [] and len(mulige_B(5, 7, 30)) == 2'),
    ('4_rett', 'mulige_B(5, 10, 30) skal gi [90.0] (bare én gang)', 'len(mulige_B(5, 10, 30)) == 1 and naer(mulige_B(5, 10, 30)[0], 90)'),
    ('5_345', 'los_trekant(3, 4, 5) skal gi A ≈ 36.87, B ≈ 53.13, C = 90 og areal 6', "naer(los_trekant(3, 4, 5)['A'], 36.8699, rel=1e-4) and naer(los_trekant(3, 4, 5)['B'], 53.1301, rel=1e-4) and naer(los_trekant(3, 4, 5)['C'], 90) and naer(los_trekant(3, 4, 5)['areal'], 6)"),
    ('5_likesidet', 'los_trekant(2, 2, 2) skal gi tre vinkler på 60° og areal √3', "all(naer(los_trekant(2, 2, 2)[v], 60) for v in 'ABC') and naer(los_trekant(2, 2, 2)['areal'], 3**0.5)"),
    ('5_umulig', 'los_trekant(1, 2, 10) skal gi None', 'los_trekant(1, 2, 10) is None and los_trekant(3, 4, 5) is not None'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
