from collections import Counter
from math import gcd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


ALFABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Tabela 2.1 z wykladu 2: prawdopodobienstwo liter w jezyku angielskim
P_ANG = {'A': .082, 'B': .015, 'C': .028, 'D': .043, 'E': .127, 'F': .022,
         'G': .020, 'H': .061, 'I': .070, 'J': .002, 'K': .008, 'L': .040,
         'M': .024, 'N': .067, 'O': .075, 'P': .019, 'Q': .001, 'R': .060,
         'S': .063, 'T': .091, 'U': .028, 'V': .010, 'W': .023, 'X': .001,
         'Y': .020, 'Z': .001}


CIPHER = "RSPEGXTSDEAPESXGFRGZXNSJFZZDTFZDQYVFFEZHQMXSJDGHXQZDMFZGSXQTDCTXSHGAJZNZFZFRSFGVFPZGXFQRSPEGYDGDBAHCFRSPEGDQDCPZHZZGNYHFZFQRSPEGFYJFZZDTFZ"

def oczysc(tekst):
    """Zostawia same litery A-Z (bez spacji, cyfr, interpunkcji)."""
    return "".join(c for c in tekst.upper() if c in ALFABET)

def szyfruj(tekst, a, b):
    """e(x) = (a*x + b) mod 26 dla kazdej litery."""
    return "".join(ALFABET[(a * ALFABET.index(c) + b) % 26] for c in oczysc(tekst))

def rozwiaz_uklad(x1, y1, x2, y2):
    """Rozwiazuje uklad:  a*x1 + b = y1,  a*x2 + b = y2  (mod 26).
    Odejmujemy rownania -> b znika:  a*(x1 - x2) = (y1 - y2)  (mod 26).
    Zwraca liste par (a, b) - zwykle jedna, czasem zadna lub kilka."""
    dx, dy = (x1 - x2) % 26, (y1 - y2) % 26
    g = gcd(dx, 26)
    if dy % g != 0:
        return []                      # uklad sprzeczny - brak klucza
    m = 26 // g                        # dzielimy kongruencje przez g
    a0 = (dy // g) * pow(dx // g, -1, m) % m
    return [(a, (y1 - a * x1) % 26) for a in range(a0, 26, m)]


def deszyfruj(szyfrogram, a, b):
    """d(y) = a^(-1) * (y - b) mod 26. Wynik malymi literami (tekst jawny)."""
    a_inv = odwrotnosc(a)
    return "".join(ALFABET[a_inv * (ALFABET.index(c) - b) % 26].lower() for c in szyfrogram)


def odwrotnosc(a, m=26):
    """a^(-1) mod m, czyli liczba t, dla ktorej a*t daje reszte 1.
    Istnieje tylko, gdy NWD(a, m) = 1. pow(a, -1, m) liczy ja algorytmem
    Euklidesa (Python 3.8+). Przyklad: odwrotnosc(3) = 9, bo 3*9 = 27 = 26 + 1."""
    return pow(a, -1, m)


def wskaznik_angielski(tekst):
    """Wskaznik M = srednie prawdopodobienstwo (wg tabeli 2.1) liter tekstu.
    Tekst angielski: okolo 0,065. Belkot: okolo 0,038."""
    return sum(P_ANG[c.upper()] for c in tekst) / len(tekst)

def kryptoanaliza(szyfrogram, szyfr, jawne, prog=0.055):
    print("Najczestsze w szyfrogramie:", szyfr, " w angielskim:", [j.lower() for j in jawne])

    # KROK 3: hipotezy. Najpierw para jawnych (e, t), potem (e, a), (t, a), ...
    #         Dla kazdej pary jawnych probujemy par najczestszych liter szyfrogramu.
    nieskuteczne = []
    for i in range(len(jawne)):
        for j in range(i + 1, len(jawne)):
            p1, p2 = jawne[i], jawne[j]
            for c1 in szyfr:
                for c2 in szyfr:
                    if c1 == c2:
                        continue
                    x1, y1 = ALFABET.index(p1), ALFABET.index(c1)
                    x2, y2 = ALFABET.index(p2), ALFABET.index(c2)
                    hip = f"{c1}={p1.lower()}, {c2}={p2.lower()}"

                    # KROK 4: z hipotezy -> uklad rownan -> klucz (a, b)
                    klucze = rozwiaz_uklad(x1, y1, x2, y2)
                    if not klucze:
                        print(f"{hip}: uklad sprzeczny")
                        continue
                    for a, b in klucze:
                        # KROK 5a: klucz niedopuszczalny? (a parzyste albo 13)
                        if gcd(a, 26) != 1:
                            print(f"{hip}: (a, b) = ({a}, {b}) -> NIEDOPUSZCZALNY, NWD({a}, 26) = {gcd(a, 26)}")
                            nieskuteczne.append((a, b, "niedopuszczalny"))
                            continue
                        # KROK 5b: odszyfruj i ocen, czy tekst jest angielski
                        jawny = deszyfruj(szyfrogram, a, b)
                        M = wskaznik_angielski(jawny)
                        print(f"{hip}: (a, b) = ({a}, {b}) -> {jawny[:40]}...  M = {M:.3f}")
                        if M >= prog:
                            return (a, b), jawny, nieskuteczne
                        nieskuteczne.append((a, b, "belkot"))
    return None, None, nieskuteczne


if __name__ == "__main__":
    hist = Counter(CIPHER)

    print("Szyfrogram najczęstrze")
    alp_sorted_by_prop = sorted(P_ANG.items(), key=lambda x: x[1], reverse=True)[:10]
    cipher_sorted_by_prop = sorted(hist.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Histogram liter w całym alfabecie: ")
    print(alp_sorted_by_prop)
    print()
    print("Histogram liter w zaszyfrowanym tekście: ")
    print(cipher_sorted_by_prop)

    etykiety, wartosci = zip(*sorted(hist.items()))

    plt.figure(figsize=(8, 5))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.bar(etykiety, wartosci)
    plt.xlabel("Litera")
    plt.ylabel("Liczba wystąpień")
    plt.title("Histogram liter w zaszyfrowanym tekście")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("histogram.png", dpi=150)
    plt.close()

    keys, plaintext, invalid = kryptoanaliza(
        CIPHER, 
        szyfr=[t[0] for t in cipher_sorted_by_prop], 
        jawne=[t[0] for t in alp_sorted_by_prop]
    )

    print("\nKlucze nieskuteczne:", ", ".join(f"({a}, {b}) {p}" for a, b, p in invalid) or "brak")
    if keys is None:
        print("Nie znaleziono klucza - szyfrogram moze byc za krotki.")
        exit()

    a, b = keys
    print(f"\nZNALEZIONY KLUCZ: (a, b) = ({a}, {b})")
    print(f"Deszyfrowanie: d(y) = {odwrotnosc(a)}*(y - {b}) mod 26")
    print(f"Tekst jawny: {plaintext}")
    print(f"Sprawdzenie: szyfruj(jawny) == szyfrogram -> {szyfruj(plaintext, a, b) == CIPHER.upper()}")